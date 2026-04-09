from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import RoleConstants
from common.utils.common import query_params_to_single_dict
from common.result import result
from system_manage.api.role import (
    SystemRoleAPI,
    SystemRoleMemberAPI,
    SystemRolePermissionAPI,
)
from system_manage.serializers.role import SystemRoleSerializer


class SystemRoleListView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system role list"),
        description=_("Get system role list"),
        operation_id=_("Get system role list"),  # type: ignore
        responses=SystemRoleAPI.get_response(),
        tags=[_("Role")],  # type: ignore
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(SystemRoleSerializer.list())


class SystemRolePermissionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system role permissions"),
        description=_("Get system role permissions"),
        operation_id=_("Get system role permissions"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="role_id",
                description=_("Role ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ],
        responses=SystemRolePermissionAPI.get_response(),
        tags=[_("Role")],  # type: ignore
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, role_id: str):
        return result.success(SystemRoleSerializer.permission_list(role_id))


class SystemRoleMemberPageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get system role member paginated list"),
        description=_("Get system role member paginated list"),
        operation_id=_("Get system role member paginated list"),  # type: ignore
        parameters=SystemRoleMemberAPI.get_page_parameters(),
        responses=SystemRoleMemberAPI.get_page_response(),
        tags=[_("Role")],  # type: ignore
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, role_id: str, current_page: int, page_size: int):
        return result.success(
            SystemRoleSerializer.page(
                role_id,
                {**query_params_to_single_dict(request.query_params)},
                current_page,
                page_size,
            )
        )
