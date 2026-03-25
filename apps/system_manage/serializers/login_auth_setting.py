# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： login_auth_setting.py
@date：2026/3/22
@desc:
"""

from django.db.models import QuerySet
from rest_framework import serializers

from system_manage.models import SystemSetting, SettingType


class LoginMethodOptionSerializer(serializers.Serializer):
    label = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class LoginAuthSettingResponseSerializer(serializers.Serializer):
    default_value = serializers.CharField(required=True)
    max_attempts = serializers.IntegerField(required=True)
    failed_attempts = serializers.IntegerField(required=True)
    lock_time = serializers.IntegerField(required=True)
    role_id = serializers.CharField(required=True)
    workspace_id = serializers.CharField(required=True)
    permission = serializers.CharField(required=True)
    login_methods = serializers.ListField(child=serializers.CharField(), required=True)
    auth_types = LoginMethodOptionSerializer(many=True, required=True)
    system_options = LoginMethodOptionSerializer(many=True, required=True)


class LoginAuthSettingSerializer(serializers.Serializer):
    SUPPORTED_LOGIN_METHODS = ["LOCAL"]
    SUPPORTED_LOGIN_OPTIONS = [{"label": "LOCAL", "value": "LOCAL"}]
    DEFAULT_META = {
        "default_value": "LOCAL",
        "max_attempts": 1,
        "failed_attempts": 5,
        "lock_time": 10,
        "role_id": "USER",
        "workspace_id": "default",
        "permission": "NOT_AUTH",
        "login_methods": ["LOCAL"],
    }

    @classmethod
    def _normalize_attempt_value(cls, value, default_value, min_value):
        if not isinstance(value, int):
            return default_value
        if value == 0:
            return default_value
        if value < min_value:
            return min_value
        return value

    @classmethod
    def _normalize_login_methods(cls, login_methods):
        if not isinstance(login_methods, list):
            return ["LOCAL"]
        final_login_methods = [
            login_method
            for login_method in login_methods
            if login_method in cls.SUPPORTED_LOGIN_METHODS
        ]
        return final_login_methods or ["LOCAL"]

    @classmethod
    def _to_response(cls, meta=None):
        meta = meta or {}
        login_methods = cls._normalize_login_methods(meta.get("login_methods"))
        default_value = meta.get("default_value", cls.DEFAULT_META["default_value"])
        if default_value not in login_methods:
            default_value = login_methods[0]

        return {
            "default_value": default_value,
            "max_attempts": cls._normalize_attempt_value(
                meta.get("max_attempts"), cls.DEFAULT_META["max_attempts"], -1
            ),
            "failed_attempts": cls._normalize_attempt_value(
                meta.get("failed_attempts"), cls.DEFAULT_META["failed_attempts"], -1
            ),
            "lock_time": cls._normalize_attempt_value(
                meta.get("lock_time"), cls.DEFAULT_META["lock_time"], 1
            ),
            "role_id": meta.get("role_id", cls.DEFAULT_META["role_id"]),
            "workspace_id": meta.get("workspace_id", cls.DEFAULT_META["workspace_id"]),
            "permission": meta.get("permission", cls.DEFAULT_META["permission"]),
            "login_methods": login_methods,
            "auth_types": cls.SUPPORTED_LOGIN_OPTIONS,
            "system_options": cls.SUPPORTED_LOGIN_OPTIONS,
        }

    @classmethod
    def one(cls):
        system_setting = (
            QuerySet(SystemSetting).filter(type=SettingType.LOGIN_AUTH).first()
        )
        if system_setting is None:
            return cls._to_response()
        return cls._to_response(system_setting.meta)

    class Update(serializers.Serializer):
        default_value = serializers.CharField(required=False)
        max_attempts = serializers.IntegerField(required=False)
        failed_attempts = serializers.IntegerField(required=False)
        lock_time = serializers.IntegerField(required=False)
        role_id = serializers.CharField(required=False)
        workspace_id = serializers.CharField(required=False, allow_blank=True)
        permission = serializers.CharField(required=False)
        login_methods = serializers.ListField(
            child=serializers.CharField(), required=False, allow_empty=False
        )

        def update_or_save(self):
            self.is_valid(raise_exception=True)
            login_auth_meta = LoginAuthSettingSerializer._to_response(self.data)
            login_auth_meta.pop("auth_types", None)
            login_auth_meta.pop("system_options", None)
            system_setting = (
                QuerySet(SystemSetting).filter(type=SettingType.LOGIN_AUTH).first()
            )
            if system_setting is None:
                system_setting = SystemSetting(type=SettingType.LOGIN_AUTH)
            system_setting.meta = login_auth_meta
            system_setting.save()
            return LoginAuthSettingSerializer._to_response(system_setting.meta)
