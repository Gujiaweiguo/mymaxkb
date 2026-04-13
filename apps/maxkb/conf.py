# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： conf.py
@date：2025/4/11 16:58
@desc:
"""

import errno
import logging
import os
from typing import Any

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
logger = logging.getLogger("maxkb.conf")


class Config(dict[str, Any]):
    defaults = {
        # 数据库相关配置
        "DB_HOST": "127.0.0.1",
        "DB_PORT": 5432,
        "DB_USER": "root",
        "DB_ENGINE": "dj_db_conn_pool.backends.postgresql",
        "DB_MAX_OVERFLOW": 80,
        # 语言
        "LANGUAGE_CODE": "zh-CN",
        "DEBUG": False,
        # redis host
        "REDIS_HOST": "127.0.0.1",
        # 端口
        "REDIS_PORT": 6379,
        # 库
        "REDIS_DB": 0,
        # 最大连接数
        "REDIS_MAX_CONNECTIONS": 100,
    }

    @staticmethod
    def _is_blank(value: object) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())

    @staticmethod
    def _is_placeholder_secret(value: object) -> bool:
        if not isinstance(value, str):
            return False
        normalized = value.strip()
        return normalized.startswith("change_me_") or normalized in {
            "MaxKB@123..",
            "Password123@postgres",
            "Password123@redis",
            "mac_kb_password",
        }

    def get_required(self, key, display_name=None):
        value = self.get(key)
        if self._is_blank(value):
            config_name = display_name or f"MAXKB_{key}"
            raise ImportError(f"Missing required configuration: {config_name}")
        return value

    def get_required_str(self, key, display_name=None) -> str:
        return str(self.get_required(key, display_name))

    def get_required_secret(self, key, display_name=None) -> str:
        value = self.get_required_str(key, display_name)
        if self._is_placeholder_secret(value):
            config_name = display_name or f"MAXKB_{key}"
            raise ImportError(
                f"Unsafe placeholder configuration is not allowed: {config_name}"
            )
        return value

    def get_int(self, key, default: int) -> int:
        raw_value: Any = self.get(key)
        return default if self._is_blank(raw_value) else int(raw_value)

    def get_bool(self, key, default: bool) -> bool:
        value = self.get(key)
        if self._is_blank(value):
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def get_str(self, key, default: str) -> str:
        value = self.get(key)
        return default if self._is_blank(value) else str(value)

    def get_debug(self) -> bool:
        return self.get_bool("DEBUG", True)

    def get_time_zone(self) -> str:
        return self.get_str("TIME_ZONE", "Asia/Shanghai")

    def get_db_setting(self) -> dict[str, Any]:
        return {
            "NAME": self.get("DB_NAME"),
            "HOST": self.get("DB_HOST"),
            "PORT": self.get("DB_PORT"),
            "USER": self.get("DB_USER"),
            "PASSWORD": self.get_required_secret("DB_PASSWORD"),
            "ENGINE": self.get("DB_ENGINE"),
            "CONN_MAX_AGE": 0,
            "POOL_OPTIONS": {
                "POOL_SIZE": 20,
                "MAX_OVERFLOW": self.get_int("DB_MAX_OVERFLOW", 80),
                "RECYCLE": 1800,
                "PRE_PING": True,
                "TIMEOUT": 30,
            },
        }

    def get_cache_setting(self):
        redis_password = self.get("REDIS_PASSWORD")
        redis_options: dict[str, object] = {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": self.get_int("REDIS_MAX_CONNECTIONS", 100)
            },
        }
        if redis_password:
            redis_options["PASSWORD"] = redis_password

        redis_location = (
            f"redis://{self.get('REDIS_HOST')}:{self.get('REDIS_PORT')}/{self.get('REDIS_DB')}"
        )

        if self.get("REDIS_SENTINEL_SENTINELS") is not None:
            sentinels_str = self.get_required_str("REDIS_SENTINEL_SENTINELS")
            sentinels = [
                (host.strip(), int(port))
                for hostport in sentinels_str.split(",")
                for host, port in [hostport.strip().split(":")]
            ]

            redis_location = (
                f"redis://{self.get('REDIS_SENTINEL_MASTER')}/{self.get('REDIS_DB')}"
            )
            redis_options.update(
                {
                    "CLIENT_CLASS": "django_redis.client.SentinelClient",
                    "SENTINELS": sentinels,
                    "SENTINEL_MASTER": self.get("REDIS_SENTINEL_MASTER"),
                }
            )
            if redis_password:
                redis_options["PASSWORD"] = redis_password

        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": redis_location,
                "OPTIONS": redis_options,
            },
        }

    def get_language_code(self):
        return self.get_str("LANGUAGE_CODE", "zh-CN")

    def get_log_level(self):
        return self.get_str("LOG_LEVEL", "DEBUG")

    def get_sandbox_python_package_paths(self):
        return self.get_str(
            "SANDBOX_PYTHON_PACKAGE_PATHS",
            "/opt/py3/lib/python3.11/site-packages,/opt/maxkb-app/sandbox/python-packages,/opt/maxkb/python-packages",
        )

    def get_admin_path(self):
        return self.get_str("ADMIN_PATH", "/admin")

    def get_chat_path(self):
        return self.get_str("CHAT_PATH", "/chat")

    def get_session_timeout(self):
        return self.get_int("SESSION_TIMEOUT", 28800)

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, dict.__repr__(self))

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)


class ConfigManager:
    config_class = Config

    def __init__(self, root_path=None):
        self.root_path = None if root_path is None else str(root_path)
        self.config = self.config_class()
        for key in self.config_class.defaults:
            self.config[key] = self.config_class.defaults[key]

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.

        .. versionadded:: 0.11
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], "items"):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                "expected at most 1 positional argument, got %d" % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for key, value in mapping:
                if key.isupper():
                    self.config[key] = value
        return True

    def from_yaml(self, filename, silent=False):
        if self.root_path:
            filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, "rt", encoding="utf8") as f:
                obj = yaml.safe_load(f)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        if obj:
            return self.from_mapping(obj)
        return True

    def load_from_yml(self):
        root_path = self.root_path or PROJECT_DIR
        for i in ["config_example.yml", "config.yaml", "config.yml"]:
            if not os.path.isfile(os.path.join(root_path, i)):
                continue
            loaded = self.from_yaml(i)
            if loaded:
                return True
        msg = f"""

                   Error: No config file found.

                   You can run `cp config_example.yml {root_path}/config.yml`, and edit it.

                   """
        raise ImportError(msg)

    def load_from_env(self):
        keys = os.environ.keys()
        config: dict[str, Any] = {
            key.replace("MAXKB_", ""): os.environ.get(key)
            for key in keys
            if key.startswith("MAXKB_")
        }
        if len(config.keys()) <= 0:
            msg = f"""

                             Error: No config env found.

                             Please set environment variables
                                MAXKB_CONFIG_TYPE: 配置文件读取方式 FILE: 使用配置文件配置  ENV: 使用ENV配置
                                MAXKB_DB_NAME: 数据库名称
                                MAXKB_DB_HOST: 数据库主机
                                MAXKB_DB_PORT: 数据库端口
                                MAXKB_DB_USER: 数据库用户名
                                MAXKB_DB_PASSWORD: 数据库密码
                                
                                 MAXKB_REDIS_HOST:缓存数据库主机
                                 MAXKB_REDIS_PORT:缓存数据库端口
                                 MAXKB_REDIS_PASSWORD:缓存数据库密码
                                 MAXKB_REDIS_DB:缓存数据库
                                 MAXKB_REDIS_MAX_CONNECTIONS:缓存数据库最大连接数
                                 MAXKB_SECRET_KEY:Django密钥
                                 MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY:Celery消息签名密钥
                                 MAXKB_RSA_PASSPHRASE:RSA私钥口令
                                 MAXKB_DEFAULT_PASSWORD:初始化管理员密码
                              """
            raise ImportError(msg)
        self.from_mapping(config)
        return True

    @classmethod
    def load_user_config(cls, root_path=None, config_class=None):
        config_class = config_class or Config
        cls.config_class = config_class
        if not root_path:
            root_path = PROJECT_DIR
        root_path = str(root_path)
        manager = cls(root_path=root_path)
        config_type = os.environ.get("MAXKB_CONFIG_TYPE")
        if config_type is None or config_type != "ENV":
            manager.load_from_yml()
        else:
            manager.load_from_env()
        config = manager.config
        return config
