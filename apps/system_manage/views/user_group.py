from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from system_manage.api.user_group import UserGroupApi
from system_manage.serializers.user_group import UserGroupManageSerializer


class UserGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get user groups"),
        description=_("Get user groups"),
        operation_id=_("Get user groups"),
        tags=[_("Chat User Management")],
        responses=UserGroupApi.get_list_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(UserGroupManageSerializer.list())

    @extend_schema(
        methods=["POST"],
        summary=_("Create or update user group"),
        description=_("Create or update user group"),
        operation_id=_("Create or update user group"),
        tags=[_("Chat User Management")],
        request=UserGroupApi.get_create_request(),
        responses=UserGroupApi.get_list_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_CREATE, RoleConstants.ADMIN)
    @log(menu="Chat user management", operate="Create or update user group")
    def post(self, request: Request):
        return result.success(
            UserGroupManageSerializer.CreateOrUpdate(data=request.data).save()
        )


class UserGroupDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        summary=_("Delete user group"),
        description=_("Delete user group"),
        operation_id=_("Delete user group"),
        tags=[_("Chat User Management")],
        parameters=UserGroupApi.get_parameters(),
        responses=UserGroupApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_DELETE, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Delete user group",
        get_operation_object=lambda r, k: {"id": k.get("user_group_id")},
    )
    def delete(self, request: Request, user_group_id: str):
        return result.success(UserGroupManageSerializer.delete(user_group_id))


class UserGroupMemberAddView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Add user group members"),
        description=_("Add user group members"),
        operation_id=_("Add user group members"),
        tags=[_("Chat User Management")],
        parameters=UserGroupApi.get_parameters(),
        request=UserGroupApi.get_add_member_request(),
        responses=UserGroupApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_ADD_MEMBER, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Add user group members",
        get_operation_object=lambda r, k: {"id": k.get("user_group_id")},
    )
    def post(self, request: Request, user_group_id: str):
        return result.success(
            UserGroupManageSerializer.AddMember(data=request.data).save(user_group_id)
        )


class UserGroupMemberRemoveView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Remove user group members"),
        description=_("Remove user group members"),
        operation_id=_("Remove user group members"),
        tags=[_("Chat User Management")],
        parameters=UserGroupApi.get_parameters(),
        request=UserGroupApi.get_remove_member_request(),
        responses=UserGroupApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_REMOVE_MEMBER, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Remove user group members",
        get_operation_object=lambda r, k: {"id": k.get("user_group_id")},
    )
    def post(self, request: Request, user_group_id: str):
        return result.success(
            UserGroupManageSerializer.RemoveMember(data=request.data).save(
                user_group_id
            )
        )


class UserGroupMemberPageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get user group member paginated list"),
        description=_("Get user group member paginated list"),
        operation_id=_("Get user group member paginated list"),
        tags=[_("Chat User Management")],
        parameters=UserGroupApi.get_page_parameters(),
        responses=UserGroupApi.get_page_response(),
    )
    @has_permissions(PermissionConstants.USER_GROUP_READ, RoleConstants.ADMIN)
    def get(
        self, request: Request, user_group_id: str, current_page: int, page_size: int
    ):
        return result.success(
            UserGroupManageSerializer.MemberQuery(
                data={**query_params_to_single_dict(request.query_params)}
            ).page(user_group_id, current_page, page_size)
        )
