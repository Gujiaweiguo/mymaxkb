from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.application_platform import (
    ApplicationPlatformConfigSerializer,
    ApplicationPlatformManageSerializer,
    ApplicationPlatformStatusUpdateSerializer,
)
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result


class WorkspaceApplicationPlatformStatusView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get application platform status"),
        tags=["Application"],
    )
    @has_permissions(
        PermissionConstants.APPLICATION_ACCESS_READ.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_ACCESS_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.USER.get_workspace_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, application_id: str):
        return result.success(
            ApplicationPlatformManageSerializer.status_map(application_id, workspace_id)
        )

    @extend_schema(
        methods=["POST"],
        request=ApplicationPlatformStatusUpdateSerializer,
        summary=_("Update application platform status"),
        tags=["Application"],
    )
    @log(menu="Application", operate="Update application platform status")
    @has_permissions(
        PermissionConstants.APPLICATION_ACCESS_EDIT.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_ACCESS_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.USER.get_workspace_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def post(self, request: Request, workspace_id: str, application_id: str):
        serializer = ApplicationPlatformStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            ApplicationPlatformManageSerializer.update_status(
                application_id,
                str(payload.get("type")),
                bool(payload.get("status")),
                workspace_id,
            )
        )


class WorkspaceApplicationPlatformConfigView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get application platform configuration"),
        tags=["Application"],
    )
    @has_permissions(
        PermissionConstants.APPLICATION_ACCESS_READ.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_ACCESS_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.USER.get_workspace_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(
        self,
        request: Request,
        workspace_id: str,
        application_id: str,
        platform_type: str,
    ):
        return result.success(
            ApplicationPlatformManageSerializer.get_config(
                application_id, platform_type, workspace_id
            )
        )

    @extend_schema(
        methods=["POST"],
        request=ApplicationPlatformConfigSerializer,
        summary=_("Update application platform configuration"),
        tags=["Application"],
    )
    @log(menu="Application", operate="Update application platform configuration")
    @has_permissions(
        PermissionConstants.APPLICATION_ACCESS_EDIT.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_ACCESS_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.USER.get_workspace_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def post(
        self,
        request: Request,
        workspace_id: str,
        application_id: str,
        platform_type: str,
    ):
        serializer = ApplicationPlatformConfigSerializer(data={"config": request.data})
        serializer.is_valid(raise_exception=True)
        return result.success(
            ApplicationPlatformManageSerializer.save_config(
                application_id,
                platform_type,
                serializer.validated_data.get("config", {}),
                workspace_id,
            )
        )


class SystemResourceApplicationPlatformStatusView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system resource application platform status"),
        tags=["Application"],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_ACCESS_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            ApplicationPlatformManageSerializer.status_map(application_id)
        )

    @extend_schema(
        methods=["POST"],
        request=ApplicationPlatformStatusUpdateSerializer,
        summary=_("Update system resource application platform status"),
        tags=["Application"],
    )
    @log(
        menu="Application", operate="Update system resource application platform status"
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_ACCESS_EDIT, RoleConstants.ADMIN
    )
    def post(self, request: Request, application_id: str):
        serializer = ApplicationPlatformStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        return result.success(
            ApplicationPlatformManageSerializer.update_status(
                application_id,
                str(payload.get("type")),
                bool(payload.get("status")),
            )
        )


class SystemResourceApplicationPlatformConfigView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system resource application platform configuration"),
        tags=["Application"],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_ACCESS_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str, platform_type: str):
        return result.success(
            ApplicationPlatformManageSerializer.get_config(
                application_id, platform_type
            )
        )

    @extend_schema(
        methods=["POST"],
        request=ApplicationPlatformConfigSerializer,
        summary=_("Update system resource application platform configuration"),
        tags=["Application"],
    )
    @log(
        menu="Application",
        operate="Update system resource application platform configuration",
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_ACCESS_EDIT, RoleConstants.ADMIN
    )
    def post(self, request: Request, application_id: str, platform_type: str):
        serializer = ApplicationPlatformConfigSerializer(data={"config": request.data})
        serializer.is_valid(raise_exception=True)
        return result.success(
            ApplicationPlatformManageSerializer.save_config(
                application_id,
                platform_type,
                serializer.validated_data.get("config", {}),
            )
        )
