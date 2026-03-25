# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： workspace.py
@date：2026/3/23
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from models_provider.api.model import DefaultModelResponse
from system_manage.api.workspace import (
    WorkspaceAPI,
    WorkspaceListResult,
    WorkspaceRoleAPI,
)
from system_manage.serializers.workspace import (
    WorkspaceMemberSerializer,
    WorkspaceOperateSerializer,
    WorkspaceQuerySerializer,
    get_workspace_user_count,
)


class WorkspaceManageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system workspace list"),
        description=_("Get system workspace list"),
        operation_id=_("Get system workspace list"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        responses=WorkspaceListResult,
    )
    @has_permissions(PermissionConstants.WORKSPACE_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(WorkspaceQuerySerializer.list())

    @extend_schema(
        methods=["POST"],
        summary=_("Create or update workspace"),
        description=_("Create or update workspace"),
        operation_id=_("Create or update workspace"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        request=WorkspaceAPI.get_request(),
        responses=WorkspaceAPI.get_response(),
    )
    @log(menu="Workspace management", operate="Create or update workspace")
    @has_permissions(PermissionConstants.WORKSPACE_EDIT, RoleConstants.ADMIN)
    def post(self, request: Request):
        workspace = WorkspaceOperateSerializer(data=request.data).save()
        return result.success(
            {
                "id": workspace.id,
                "name": workspace.name,
                "user_count": get_workspace_user_count(workspace.id),
            }
        )


class WorkspaceManageOperateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        summary=_("Delete workspace"),
        description=_("Delete workspace"),
        operation_id=_("Delete workspace"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        parameters=WorkspaceAPI.Operate.get_parameters(),
        responses=DefaultModelResponse.get_response(),
    )
    @log(menu="Workspace management", operate="Delete workspace")
    @has_permissions(PermissionConstants.WORKSPACE_DELETE, RoleConstants.ADMIN)
    def delete(self, request: Request, workspace_id: str):
        return result.success(WorkspaceQuerySerializer.delete(workspace_id))


class WorkspaceManageDeleteCheckView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Check workspace deletion"),
        description=_("Check workspace deletion"),
        operation_id=_("Check workspace deletion"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        parameters=WorkspaceAPI.DeleteCheck.get_parameters(),
        responses=WorkspaceAPI.DeleteCheck.get_response(),
    )
    @has_permissions(PermissionConstants.WORKSPACE_DELETE, RoleConstants.ADMIN)
    def get(self, request: Request, workspace_id: str):
        return result.success(WorkspaceQuerySerializer.delete_check(workspace_id))


class WorkspaceMemberPageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get workspace members"),
        description=_("Get workspace members"),
        operation_id=_("Get workspace members"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        parameters=WorkspaceAPI.MemberPage.get_parameters(),
        responses=WorkspaceAPI.MemberPage.get_response(),
    )
    @has_permissions(PermissionConstants.WORKSPACE_READ, RoleConstants.ADMIN)
    def get(
        self, request: Request, workspace_id: str, current_page: int, page_size: int
    ):
        return result.success(
            WorkspaceMemberSerializer.page(
                workspace_id,
                dict(request.query_params),
                current_page,
                page_size,
            )
        )


class WorkspaceMemberCreateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Create workspace members"),
        description=_("Create workspace members"),
        operation_id=_("Create workspace members"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        parameters=WorkspaceAPI.MemberCreate.get_parameters(),
        request=WorkspaceAPI.MemberCreate.get_request(),
        responses=WorkspaceAPI.MemberCreate.get_response(),
    )
    @log(menu="Workspace management", operate="Add workspace member")
    @has_permissions(PermissionConstants.WORKSPACE_ADD_MEMBER, RoleConstants.ADMIN)
    def post(self, request: Request, workspace_id: str):
        return result.success(WorkspaceMemberSerializer.add(workspace_id, request.data))


class WorkspaceMemberDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Delete workspace member"),
        description=_("Delete workspace member"),
        operation_id=_("Delete workspace member"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        parameters=WorkspaceAPI.MemberDelete.get_parameters(),
        responses=WorkspaceAPI.MemberDelete.get_response(),
    )
    @log(menu="Workspace management", operate="Delete workspace member")
    @has_permissions(PermissionConstants.WORKSPACE_REMOVE_MEMBER, RoleConstants.ADMIN)
    def post(self, request: Request, workspace_id: str, user_relation_id: str):
        return result.success(
            WorkspaceMemberSerializer.remove(workspace_id, user_relation_id)
        )


class WorkspaceRoleListView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get workspace role list"),
        description=_("Get workspace role list"),
        operation_id=_("Get workspace role list"),  # type: ignore
        tags=[_("Workspace Management")],  # type: ignore
        responses=WorkspaceRoleAPI.get_response(),
    )
    @has_permissions(PermissionConstants.WORKSPACE_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(WorkspaceMemberSerializer.get_role_list())
