from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.exception.app_exception import AppApiException
from system_manage.models import SystemSetting

SUPPORTED_PLATFORM_TYPES = ["wecom", "dingtalk", "lark"]

REQUIRED_FIELDS = {
    "wecom": ["corp_id", "agent_id", "app_secret"],
    "dingtalk": ["corp_id", "app_key", "app_secret"],
    "lark": ["app_key", "app_secret"],
}


def _has_configured_value(config: dict) -> bool:
    return any(
        key != "callback_url" and str(value or "").strip() != ""
        for key, value in (config or {}).items()
    )


def _build_state(
    is_configured: bool, is_valid: bool, is_active: bool, failure_reason: str
) -> str:
    if not is_configured:
        return "unconfigured"
    if is_active and is_valid:
        return "enabled"
    if is_valid:
        return "ready"
    if failure_reason:
        return "failed"
    return "configured"


class PlatformSourceManageSerializer:
    @classmethod
    def ensure_supported(cls, platform_type: str):
        if platform_type not in SUPPORTED_PLATFORM_TYPES:
            raise AppApiException(500, _("Unsupported platform type"))

    @classmethod
    def _get_setting(cls, setting_type: int):
        return QuerySet(SystemSetting).filter(type=setting_type).first()

    @classmethod
    def _get_setting_or_create(cls, setting_type: int):
        setting = cls._get_setting(setting_type)
        if setting is None:
            setting = SystemSetting(type=setting_type, meta={})
        return setting

    @classmethod
    def _normalize_platform(cls, auth_type: str, entry: Any):
        raw_entry = entry if isinstance(entry, dict) else {}
        config = (
            raw_entry.get("config", {})
            if isinstance(raw_entry.get("config", {}), dict)
            else {}
        )
        is_configured = _has_configured_value(config)
        is_valid = bool(raw_entry.get("is_valid")) if is_configured else False
        is_active = bool(raw_entry.get("is_active")) if is_valid else False
        failure_reason = str(raw_entry.get("failure_reason", "") or "")
        state = str(
            raw_entry.get("state")
            or _build_state(is_configured, is_valid, is_active, failure_reason)
        )
        return {
            "auth_type": auth_type,
            "config": config,
            "is_active": is_active,
            "is_valid": is_valid,
            "is_configured": is_configured,
            "state": state,
            "failure_reason": failure_reason,
        }

    @classmethod
    def list(cls, setting_type: int):
        setting = cls._get_setting(setting_type)
        raw_meta = getattr(setting, "meta", {}) if setting is not None else {}
        meta = raw_meta if isinstance(raw_meta, dict) else {}
        return [
            cls._normalize_platform(platform_type, meta.get(platform_type))
            for platform_type in SUPPORTED_PLATFORM_TYPES
        ]

    @classmethod
    def get(cls, setting_type: int, platform_type: str):
        cls.ensure_supported(platform_type)
        setting = cls._get_setting(setting_type)
        raw_meta = getattr(setting, "meta", {}) if setting is not None else {}
        meta = raw_meta if isinstance(raw_meta, dict) else {}
        return cls._normalize_platform(platform_type, meta.get(platform_type))

    @classmethod
    def save(
        cls,
        setting_type: int,
        platform_type: str,
        config: dict,
        is_active: bool | None = None,
    ):
        cls.ensure_supported(platform_type)
        setting = cls._get_setting_or_create(setting_type)
        raw_meta = getattr(setting, "meta", {})
        meta = raw_meta if isinstance(raw_meta, dict) else {}
        current = (
            meta.get(platform_type, {})
            if isinstance(meta.get(platform_type, {}), dict)
            else {}
        )
        current_config = (
            current.get("config", {})
            if isinstance(current.get("config", {}), dict)
            else {}
        )
        next_config = config if isinstance(config, dict) else {}
        toggle_only = is_active is not None and next_config == current_config

        if toggle_only:
            if is_active and not current.get("is_valid", False):
                raise AppApiException(
                    500, _("Cannot activate platform before validation succeeds")
                )
            current["is_active"] = is_active
            current["state"] = _build_state(
                _has_configured_value(current_config),
                bool(current.get("is_valid", False)),
                bool(is_active),
                str(current.get("failure_reason", "") or ""),
            )
        else:
            current = {
                "config": next_config,
                "is_active": False,
                "is_valid": False,
                "failure_reason": "",
                "state": "configured"
                if _has_configured_value(next_config)
                else "unconfigured",
            }

        meta[platform_type] = current
        setting.meta = meta
        setting.save()
        return cls._normalize_platform(platform_type, current)

    @classmethod
    def validate(cls, setting_type: int, platform_type: str, config: dict):
        cls.ensure_supported(platform_type)
        setting = cls._get_setting_or_create(setting_type)
        raw_meta = getattr(setting, "meta", {})
        meta = raw_meta if isinstance(raw_meta, dict) else {}
        next_config = config if isinstance(config, dict) else {}
        missing_fields = [
            field
            for field in REQUIRED_FIELDS[platform_type]
            if not next_config.get(field)
        ]
        is_valid = len(missing_fields) == 0
        failure_reason = (
            ""
            if is_valid
            else str(
                _("Missing required fields: %(fields)s")
                % {"fields": ", ".join(missing_fields)}
            )
        )
        current = (
            meta.get(platform_type, {})
            if isinstance(meta.get(platform_type, {}), dict)
            else {}
        )
        current["config"] = next_config
        current["is_valid"] = is_valid
        current["failure_reason"] = failure_reason
        current["is_active"] = current.get("is_active", False) if is_valid else False
        current["state"] = _build_state(
            _has_configured_value(next_config),
            is_valid,
            bool(current["is_active"]),
            failure_reason,
        )
        meta[platform_type] = current
        setting.meta = meta
        setting.save()
        return cls._normalize_platform(platform_type, current)
