from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import (
    CompareConstants,
    PermissionConstants,
    RoleConstants,
    ViewPermission,
)
from common.log.log import log
from common.result import result
from knowledge.api.knowledge_chat_user_authorize import KnowledgeChatUserAuthorizeAPI
from knowledge.serializers.knowledge_chat_user_authorize import (
    KnowledgeChatUserAuthorizeSerializer,
)
from system_manage.models import ResourceType


class WorkspaceKnowledgeChatUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get knowledge chat-user groups"),
        description=_("Get knowledge chat-user groups"),
        operation_id=_("Get knowledge chat-user groups"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_workspace_parameters(),
        responses=KnowledgeChatUserAuthorizeAPI.get_group_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CHAT_USER_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_CHAT_USER_READ.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, resource_id: str):
        return result.success(
            KnowledgeChatUserAuthorizeSerializer.GroupQuery.list(
                ResourceType.KNOWLEDGE, resource_id, workspace_id
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update knowledge chat-user groups"),
        description=_("Update knowledge chat-user groups"),
        operation_id=_("Update knowledge chat-user groups"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_workspace_parameters(),
        request=KnowledgeChatUserAuthorizeAPI.get_group_request(),
        responses=KnowledgeChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CHAT_USER_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_CHAT_USER_EDIT.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    @log(menu="Knowledge Base", operate="Update knowledge chat-user groups")
    def put(self, request: Request, workspace_id: str, resource_id: str):
        serializer = KnowledgeChatUserAuthorizeSerializer.GroupOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(ResourceType.KNOWLEDGE, resource_id, workspace_id)
        )


class WorkspaceKnowledgeChatUserGroupUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get knowledge chat-user group users"),
        description=_("Get knowledge chat-user group users"),
        operation_id=_("Get knowledge chat-user group users"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_workspace_parameters()
        + KnowledgeChatUserAuthorizeAPI.get_user_group_parameters(),
        responses=KnowledgeChatUserAuthorizeAPI.get_user_page_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CHAT_USER_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_CHAT_USER_READ.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(
        self,
        request: Request,
        workspace_id: str,
        resource_id: str,
        user_group_id: str,
        current_page: int,
        page_size: int,
    ):
        return result.success(
            KnowledgeChatUserAuthorizeSerializer.UserQuery(
                data=request.query_params
            ).page(
                ResourceType.KNOWLEDGE,
                resource_id,
                user_group_id,
                current_page,
                page_size,
                workspace_id,
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update knowledge chat-user group users"),
        description=_("Update knowledge chat-user group users"),
        operation_id=_("Update knowledge chat-user group users"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_workspace_parameters()
        + [KnowledgeChatUserAuthorizeAPI.get_user_group_parameters()[0]],
        request=KnowledgeChatUserAuthorizeAPI.get_user_request(),
        responses=KnowledgeChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CHAT_USER_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_CHAT_USER_EDIT.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    @log(menu="Knowledge Base", operate="Update knowledge chat-user group users")
    def put(
        self,
        request: Request,
        workspace_id: str,
        resource_id: str,
        user_group_id: str,
    ):
        serializer = KnowledgeChatUserAuthorizeSerializer.UserOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(
                ResourceType.KNOWLEDGE, resource_id, user_group_id, workspace_id
            )
        )


class SystemKnowledgeChatUserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get resource knowledge chat-user groups"),
        description=_("Get resource knowledge chat-user groups"),
        operation_id=_("Get resource knowledge chat-user groups"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_system_parameters(),
        responses=KnowledgeChatUserAuthorizeAPI.get_group_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_KNOWLEDGE_CHAT_USER_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, resource_id: str):
        return result.success(
            KnowledgeChatUserAuthorizeSerializer.GroupQuery.list(
                ResourceType.KNOWLEDGE, resource_id
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update resource knowledge chat-user groups"),
        description=_("Update resource knowledge chat-user groups"),
        operation_id=_("Update resource knowledge chat-user groups"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_system_parameters(),
        request=KnowledgeChatUserAuthorizeAPI.get_group_request(),
        responses=KnowledgeChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_KNOWLEDGE_CHAT_USER_EDIT, RoleConstants.ADMIN
    )
    @log(menu="Knowledge Base", operate="Update resource knowledge chat-user groups")
    def put(self, request: Request, resource_id: str):
        serializer = KnowledgeChatUserAuthorizeSerializer.GroupOperate(
            data={"data": request.data}
        )
        return result.success(serializer.save(ResourceType.KNOWLEDGE, resource_id))


class SystemKnowledgeChatUserGroupUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get resource knowledge chat-user group users"),
        description=_("Get resource knowledge chat-user group users"),
        operation_id=_("Get resource knowledge chat-user group users"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_system_parameters()
        + KnowledgeChatUserAuthorizeAPI.get_user_group_parameters(),
        responses=KnowledgeChatUserAuthorizeAPI.get_user_page_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_KNOWLEDGE_CHAT_USER_READ, RoleConstants.ADMIN
    )
    def get(
        self,
        request: Request,
        resource_id: str,
        user_group_id: str,
        current_page: int,
        page_size: int,
    ):
        return result.success(
            KnowledgeChatUserAuthorizeSerializer.UserQuery(
                data=request.query_params
            ).page(
                ResourceType.KNOWLEDGE,
                resource_id,
                user_group_id,
                current_page,
                page_size,
            )
        )

    @extend_schema(
        methods=["PUT"],
        summary=_("Update resource knowledge chat-user group users"),
        description=_("Update resource knowledge chat-user group users"),
        operation_id=_("Update resource knowledge chat-user group users"),  # type: ignore
        parameters=KnowledgeChatUserAuthorizeAPI.get_system_parameters()
        + [KnowledgeChatUserAuthorizeAPI.get_user_group_parameters()[0]],
        request=KnowledgeChatUserAuthorizeAPI.get_user_request(),
        responses=KnowledgeChatUserAuthorizeAPI.get_default_response(),
        tags=[_("Knowledge Base")],
    )
    @has_permissions(
        PermissionConstants.RESOURCE_KNOWLEDGE_CHAT_USER_EDIT, RoleConstants.ADMIN
    )
    @log(
        menu="Knowledge Base", operate="Update resource knowledge chat-user group users"
    )
    def put(self, request: Request, resource_id: str, user_group_id: str):
        serializer = KnowledgeChatUserAuthorizeSerializer.UserOperate(
            data={"data": request.data}
        )
        return result.success(
            serializer.save(ResourceType.KNOWLEDGE, resource_id, user_group_id)
        )
