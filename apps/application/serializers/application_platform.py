from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application, ApplicationAccessToken
from common.exception.app_exception import AppApiException
from system_manage.models import SettingType
from system_manage.serializers.platform_source import PlatformSourceManageSerializer

READINESS_PLATFORM_TYPES = ["wecom", "dingtalk", "lark"]
ALL_PLATFORM_TYPES = ["wecomBot", "wecom", "dingtalk", "wechat", "lark", "slack"]

APPLICATION_REQUIRED_FIELDS = {
    "wecom": ["app_id", "agent_id", "secret", "token", "encoding_aes_key"],
    "dingtalk": ["client_id", "client_secret", "token", "encoding_aes_key"],
    "lark": ["app_id", "app_secret"],
}


class ApplicationPlatformStatusUpdateSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    status = serializers.BooleanField(required=True)


class ApplicationPlatformConfigSerializer(serializers.Serializer):
    config = serializers.DictField(required=False, default=dict)


def _has_configured_value(config: dict) -> bool:
    return any(
        key not in {"callback_url", "is_active"} and str(value or "").strip() != ""
        for key, value in (config or {}).items()
    )


def _build_state(
    exists: bool, is_valid: bool, is_active: bool, failure_reason: str
) -> str:
    if not exists:
        return "unconfigured"
    if is_active and is_valid:
        return "enabled"
    if is_valid:
        return "ready"
    if failure_reason:
        return "failed"
    return "configured"


class ApplicationPlatformManageSerializer:
    @classmethod
    def _get_application(cls, application_id: str, workspace_id: str | None = None):
        query_set = QuerySet(Application).filter(id=application_id)
        if workspace_id is not None:
            query_set = query_set.filter(workspace_id=workspace_id)
        application = query_set.first()
        if application is None:
            raise AppApiException(500, _("Application not found"))
        return application

    @classmethod
    def _get_access_token(cls, application_id: str):
        access_token = (
            QuerySet(ApplicationAccessToken)
            .filter(application_id=application_id)
            .first()
        )
        if access_token is None:
            access_token = ApplicationAccessToken.objects.create(
                application_id=application_id,
                access_token=f"external-{application_id}".replace("-", "")[:16],
                is_active=True,
            )
        return access_token

    @classmethod
    def _get_platform_meta(cls, application_id: str):
        access_token = cls._get_access_token(application_id)
        raw_auth_value: Any = access_token.authentication_value
        auth_value = raw_auth_value if isinstance(raw_auth_value, dict) else {}
        return (
            auth_value.get("platform_config", {})
            if isinstance(auth_value.get("platform_config", {}), dict)
            else {}
        )

    @classmethod
    def _save_platform_meta(cls, application_id: str, platform_meta: dict):
        access_token = cls._get_access_token(application_id)
        raw_auth_value: Any = access_token.authentication_value
        auth_value = raw_auth_value if isinstance(raw_auth_value, dict) else {}
        auth_value["platform_config"] = platform_meta
        access_token.authentication_value = auth_value
        access_token.save(update_fields=["authentication_value", "update_time"])

    @classmethod
    def get_callback_url(cls, application_id: str, platform_type: str):
        return f"/api/chat/{platform_type}/{application_id}"

    @classmethod
    def _provider_ready(cls, platform_type: str):
        if platform_type not in READINESS_PLATFORM_TYPES:
            return True
        provider = PlatformSourceManageSerializer.get(
            SettingType.PLATFORM_SOURCE, platform_type
        )
        return bool(provider.get("is_valid"))

    @classmethod
    def _normalize_status(cls, platform_type: str, entry: Any, application_id: str):
        raw_entry = entry if isinstance(entry, dict) else {}
        config = (
            raw_entry.get("config", {})
            if isinstance(raw_entry.get("config", {}), dict)
            else {}
        )
        exists = _has_configured_value(config)
        is_active = bool(raw_entry.get("is_active"))
        failure_reason = ""
        is_valid = exists
        if platform_type in READINESS_PLATFORM_TYPES and exists:
            missing = [
                field
                for field in APPLICATION_REQUIRED_FIELDS[platform_type]
                if not config.get(field)
            ]
            if missing:
                is_valid = False
                failure_reason = str(
                    _("Missing required fields: %(fields)s")
                    % {"fields": ", ".join(missing)}
                )
            elif not cls._provider_ready(platform_type):
                is_valid = False
                failure_reason = str(_("Provider configuration is not ready"))
        if not is_valid:
            is_active = False
        return {
            "exists": exists,
            "is_configured": exists,
            "is_active": is_active,
            "is_valid": is_valid,
            "state": _build_state(exists, is_valid, is_active, failure_reason),
            "failure_reason": failure_reason,
            "config": {
                **config,
                "callback_url": config.get("callback_url")
                or cls.get_callback_url(application_id, platform_type),
            },
        }

    @classmethod
    def status_map(cls, application_id: str, workspace_id: str | None = None):
        application = cls._get_application(application_id, workspace_id)
        platform_meta = cls._get_platform_meta(str(application.id))
        return {
            platform_type: cls._normalize_status(
                platform_type, platform_meta.get(platform_type, {}), str(application.id)
            )
            for platform_type in ALL_PLATFORM_TYPES
        }

    @classmethod
    def get_config(
        cls, application_id: str, platform_type: str, workspace_id: str | None = None
    ):
        if platform_type not in ALL_PLATFORM_TYPES:
            raise AppApiException(500, _("Unsupported platform type"))
        application = cls._get_application(application_id, workspace_id)
        platform_meta = cls._get_platform_meta(str(application.id))
        return cls._normalize_status(
            platform_type, platform_meta.get(platform_type, {}), str(application.id)
        )

    @classmethod
    def save_config(
        cls,
        application_id: str,
        platform_type: str,
        config: dict,
        workspace_id: str | None = None,
    ):
        if platform_type not in ALL_PLATFORM_TYPES:
            raise AppApiException(500, _("Unsupported platform type"))
        application = cls._get_application(application_id, workspace_id)
        platform_meta = cls._get_platform_meta(str(application.id))
        current = (
            platform_meta.get(platform_type, {})
            if isinstance(platform_meta.get(platform_type, {}), dict)
            else {}
        )
        current_config = (
            current.get("config", {})
            if isinstance(current.get("config", {}), dict)
            else {}
        )
        platform_meta[platform_type] = {
            "config": config if isinstance(config, dict) else {},
            "is_active": current.get("is_active", False)
            if current_config == config
            else False,
        }
        cls._save_platform_meta(str(application.id), platform_meta)
        return cls.get_config(str(application.id), platform_type, workspace_id)

    @classmethod
    def update_status(
        cls,
        application_id: str,
        platform_type: str,
        is_active: bool,
        workspace_id: str | None = None,
    ):
        if platform_type not in ALL_PLATFORM_TYPES:
            raise AppApiException(500, _("Unsupported platform type"))
        application = cls._get_application(application_id, workspace_id)
        platform_meta = cls._get_platform_meta(str(application.id))
        current = (
            platform_meta.get(platform_type, {})
            if isinstance(platform_meta.get(platform_type, {}), dict)
            else {}
        )
        status = cls._normalize_status(platform_type, current, str(application.id))
        if is_active and not status.get("is_valid"):
            raise AppApiException(
                500,
                _(
                    "Cannot activate application platform before provider readiness succeeds"
                ),
            )
        current["is_active"] = is_active
        platform_meta[platform_type] = current
        cls._save_platform_meta(str(application.id), platform_meta)
        return cls.get_config(str(application.id), platform_type, workspace_id)
