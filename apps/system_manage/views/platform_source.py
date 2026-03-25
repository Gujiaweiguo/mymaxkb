from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from system_manage.api.platform_source import (
    PlatformSourceItemSerializer,
    PlatformSourceRequestSerializer,
)
from system_manage.models import SettingType
from system_manage.serializers.platform_source import PlatformSourceManageSerializer


def _get_is_active(payload: dict):
    if "is_active" in payload:
        return payload.get("is_active")
    if "isActive" in payload:
        return payload.get("isActive")
    return None


class PlatformSourceView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get platform source configurations"),
        responses=PlatformSourceItemSerializer(many=True),
        tags=["Platform Source Settings"],
    )
    @has_permissions(PermissionConstants.LOGIN_AUTH_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(
            PlatformSourceManageSerializer.list(SettingType.PLATFORM_SOURCE)
        )

    @extend_schema(
        methods=["POST"],
        summary=_("Update platform source configuration"),
        request=PlatformSourceRequestSerializer,
        responses=PlatformSourceItemSerializer,
        tags=["Platform Source Settings"],
    )
    @log(
        menu="Platform Source Settings", operate="Update platform source configuration"
    )
    @has_permissions(PermissionConstants.LOGIN_AUTH_EDIT, RoleConstants.ADMIN)
    def post(self, request: Request):
        serializer = PlatformSourceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            PlatformSourceManageSerializer.save(
                SettingType.PLATFORM_SOURCE,
                str(payload.get("key")),
                payload.get("config", {}),
                _get_is_active(payload),
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Validate platform source configuration"),
        request=PlatformSourceRequestSerializer,
        responses=PlatformSourceItemSerializer,
        tags=["Platform Source Settings"],
    )
    @log(
        menu="Platform Source Settings",
        operate="Validate platform source configuration",
    )
    @has_permissions(PermissionConstants.LOGIN_AUTH_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        serializer = PlatformSourceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            PlatformSourceManageSerializer.validate(
                SettingType.PLATFORM_SOURCE,
                str(payload.get("key")),
                payload.get("config", {}),
            )
        )


class ChatUserPlatformSourceView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get chat user platform source configurations"),
        responses=PlatformSourceItemSerializer(many=True),
        tags=["Chat User Platform Source Settings"],
    )
    @has_permissions(PermissionConstants.CHAT_USER_AUTH_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(
            PlatformSourceManageSerializer.list(SettingType.CHAT_USER_PLATFORM_SOURCE)
        )

    @extend_schema(
        methods=["POST"],
        summary=_("Update chat user platform source configuration"),
        request=PlatformSourceRequestSerializer,
        responses=PlatformSourceItemSerializer,
        tags=["Chat User Platform Source Settings"],
    )
    @log(
        menu="Chat User Platform Source Settings",
        operate="Update chat user platform source configuration",
    )
    @has_permissions(PermissionConstants.CHAT_USER_AUTH_EDIT, RoleConstants.ADMIN)
    def post(self, request: Request):
        serializer = PlatformSourceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            PlatformSourceManageSerializer.save(
                SettingType.CHAT_USER_PLATFORM_SOURCE,
                str(payload.get("key")),
                payload.get("config", {}),
                _get_is_active(payload),
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Validate chat user platform source configuration"),
        request=PlatformSourceRequestSerializer,
        responses=PlatformSourceItemSerializer,
        tags=["Chat User Platform Source Settings"],
    )
    @log(
        menu="Chat User Platform Source Settings",
        operate="Validate chat user platform source configuration",
    )
    @has_permissions(PermissionConstants.CHAT_USER_AUTH_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        serializer = PlatformSourceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            PlatformSourceManageSerializer.validate(
                SettingType.CHAT_USER_PLATFORM_SOURCE,
                str(payload.get("key")),
                payload.get("config", {}),
            )
        )
