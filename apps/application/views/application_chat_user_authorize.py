from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat_user_authorize import (
    ApplicationChatUserAuthorizeAPI,
    ApplicationChatUserAuthTypeResult,
)
from application.serializers.application_chat_user_authorize import (
    ApplicationChatUserAuthorizeSerializer,
)
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import (
    CompareConstants,
    PermissionConstants,
    RoleConstants,
    ViewPermission,
)
from common.log.log import log


class WorkspaceApplicationChatUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get application chat-user groups"),
        description=_("Get application chat-user groups"),
        operation_id=_("Get application chat-user groups"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_workspace_parameters(),
        responses=ApplicationChatUserAuthorizeAPI.get_group_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.APPLICATION_CHAT_USER_READ.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_CHAT_USER_READ.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(
        self, request: Request, workspace_id: str, resource_type: str, resource_id: str
    ):
        return result.success(
            ApplicationChatUserAuthorizeSerializer.GroupQuery.list(
                resource_type.upper(), resource_id, workspace_id
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update application chat-user groups"),
        description=_("Update application chat-user groups"),
        operation_id=_("Update application chat-user groups"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_workspace_parameters(),
        request=ApplicationChatUserAuthorizeAPI.get_group_request(),
        responses=ApplicationChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.APPLICATION_CHAT_USER_EDIT.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_CHAT_USER_EDIT.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    @log(menu="Application", operate="Update application chat-user groups")
    def put(
        self, request: Request, workspace_id: str, resource_type: str, resource_id: str
    ):
        serializer = ApplicationChatUserAuthorizeSerializer.GroupOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(resource_type.upper(), resource_id, workspace_id)
        )


class WorkspaceApplicationChatUserGroupUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get application chat-user group users"),
        description=_("Get application chat-user group users"),
        operation_id=_("Get application chat-user group users"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_workspace_parameters()
        + ApplicationChatUserAuthorizeAPI.get_user_group_parameters(),
        responses=ApplicationChatUserAuthorizeAPI.get_user_page_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.APPLICATION_CHAT_USER_READ.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_CHAT_USER_READ.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(
        self,
        request: Request,
        workspace_id: str,
        resource_type: str,
        resource_id: str,
        user_group_id: str,
        current_page: int,
        page_size: int,
    ):
        return result.success(
            ApplicationChatUserAuthorizeSerializer.UserQuery(
                data=request.query_params
            ).page(
                resource_type.upper(),
                resource_id,
                user_group_id,
                current_page,
                page_size,
                workspace_id,
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update application chat-user group users"),
        description=_("Update application chat-user group users"),
        operation_id=_("Update application chat-user group users"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_workspace_parameters()
        + [ApplicationChatUserAuthorizeAPI.get_user_group_parameters()[0]],
        request=ApplicationChatUserAuthorizeAPI.get_user_request(),
        responses=ApplicationChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.APPLICATION_CHAT_USER_EDIT.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_CHAT_USER_EDIT.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    @log(menu="Application", operate="Update application chat-user group users")
    def put(
        self,
        request: Request,
        workspace_id: str,
        resource_type: str,
        resource_id: str,
        user_group_id: str,
    ):
        serializer = ApplicationChatUserAuthorizeSerializer.UserOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(
                resource_type.upper(), resource_id, user_group_id, workspace_id
            )
        )


class SystemApplicationChatUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get resource application chat-user groups"),
        description=_("Get resource application chat-user groups"),
        operation_id=_("Get resource application chat-user groups"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_system_parameters(),
        responses=ApplicationChatUserAuthorizeAPI.get_group_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_USER_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, resource_type: str, resource_id: str):
        return result.success(
            ApplicationChatUserAuthorizeSerializer.GroupQuery.list(
                resource_type.upper(), resource_id
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update resource application chat-user groups"),
        description=_("Update resource application chat-user groups"),
        operation_id=_("Update resource application chat-user groups"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_system_parameters(),
        request=ApplicationChatUserAuthorizeAPI.get_group_request(),
        responses=ApplicationChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_USER_EDIT, RoleConstants.ADMIN
    )
    @log(menu="Application", operate="Update resource application chat-user groups")
    def put(self, request: Request, resource_type: str, resource_id: str):
        serializer = ApplicationChatUserAuthorizeSerializer.GroupOperate(
            data={"data": request.data}
        )
        return result.success(serializer.save(resource_type.upper(), resource_id))


class SystemApplicationChatUserGroupUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get resource application chat-user group users"),
        description=_("Get resource application chat-user group users"),
        operation_id=_("Get resource application chat-user group users"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_system_parameters()
        + ApplicationChatUserAuthorizeAPI.get_user_group_parameters(),
        responses=ApplicationChatUserAuthorizeAPI.get_user_page_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_USER_READ, RoleConstants.ADMIN
    )
    def get(
        self,
        request: Request,
        resource_type: str,
        resource_id: str,
        user_group_id: str,
        current_page: int,
        page_size: int,
    ):
        return result.success(
            ApplicationChatUserAuthorizeSerializer.UserQuery(
                data=request.query_params
            ).page(
                resource_type.upper(),
                resource_id,
                user_group_id,
                current_page,
                page_size,
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update resource application chat-user group users"),
        description=_("Update resource application chat-user group users"),
        operation_id=_("Update resource application chat-user group users"),  # type: ignore
        parameters=ApplicationChatUserAuthorizeAPI.get_system_parameters()
        + [ApplicationChatUserAuthorizeAPI.get_user_group_parameters()[0]],
        request=ApplicationChatUserAuthorizeAPI.get_user_request(),
        responses=ApplicationChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Application")],
    )  # type: ignore
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_USER_EDIT, RoleConstants.ADMIN
    )
    @log(
        menu="Application", operate="Update resource application chat-user group users"
    )
    def put(
        self, request: Request, resource_type: str, resource_id: str, user_group_id: str
    ):
        serializer = ApplicationChatUserAuthorizeSerializer.UserOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(resource_type.upper(), resource_id, user_group_id)
        )


class ChatUserAuthTypeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get chat-user auth types"),
        description=_("Get chat-user auth types"),
        operation_id=_("Get chat-user auth types"),  # type: ignore
        responses=ApplicationChatUserAuthTypeResult,
        tags=[_("Application")],
    )  # type: ignore
    def get(self, request: Request):
        return result.success(ApplicationChatUserAuthorizeSerializer.get_auth_types())
