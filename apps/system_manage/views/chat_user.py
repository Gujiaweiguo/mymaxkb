from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.exception.app_exception import AppApiException
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from system_manage.api.chat_user import (
    ChatUserApi,
    ChatUserSyncResult,
    ChatUserSyncTypeResult,
)
from system_manage.serializers.chat_user import (
    ChatUserBatchDeleteSerializer,
    ChatUserGroupAssignmentSerializer,
    ChatUserManageSerializer,
    ChatUserPasswordSerializer,
    ChatUserSyncSerializer,
)


class ChatUserListView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get chat users"),
        description=_("Get chat users"),
        operation_id=_("Get chat users"),
        tags=[_("Chat User Management")],
        responses=ChatUserApi.get_list_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(ChatUserManageSerializer.Query(data={}).list())


class ChatUserManageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Create chat user"),
        description=_("Create chat user"),
        operation_id=_("Create chat user"),
        tags=[_("Chat User Management")],
        request=ChatUserApi.get_create_request(),
        responses=ChatUserApi.get_list_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_CREATE, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Create chat user",
        get_operation_object=lambda r, k: {"name": r.data.get("username")},
    )
    def post(self, request: Request):
        return result.success(ChatUserManageSerializer.Create(data=request.data).save())


class ChatUserPageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get chat user paginated list"),
        description=_("Get chat user paginated list"),
        operation_id=_("Get chat user paginated list"),
        tags=[_("Chat User Management")],
        parameters=ChatUserApi.get_page_parameters(),
        responses=ChatUserApi.get_page_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_READ, RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            ChatUserManageSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)}
            ).page(current_page, page_size)
        )


class ChatUserOperateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["PUT"],
        summary=_("Update chat user"),
        description=_("Update chat user"),
        operation_id=_("Update chat user"),
        tags=[_("Chat User Management")],
        parameters=ChatUserApi.get_parameters(),
        request=ChatUserApi.get_update_request(),
        responses=ChatUserApi.get_list_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_EDIT, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Update chat user",
        get_operation_object=lambda r, k: {"id": k.get("user_id")},
    )
    def put(self, request: Request, user_id: str):
        payload = {
            key: request.data.get(key)
            for key in [
                "username",
                "email",
                "nick_name",
                "phone",
                "source",
                "is_active",
                "user_group_ids",
            ]
            if key in request.data
        }
        return result.success(
            ChatUserManageSerializer.Update(
                data=payload, context={"user_id": user_id}
            ).save()
        )

    @extend_schema(
        methods=["DELETE"],
        summary=_("Delete chat user"),
        description=_("Delete chat user"),
        operation_id=_("Delete chat user"),
        tags=[_("Chat User Management")],
        parameters=ChatUserApi.get_parameters(),
        responses=ChatUserApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_DELETE, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Delete chat user",
        get_operation_object=lambda r, k: {"id": k.get("user_id")},
    )
    def delete(self, request: Request, user_id: str):
        return result.success(ChatUserManageSerializer.delete(user_id))


class ChatUserPasswordView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["PUT"],
        summary=_("Reset chat user password"),
        description=_("Reset chat user password"),
        operation_id=_("Reset chat user password"),
        tags=[_("Chat User Management")],
        parameters=ChatUserApi.get_parameters(),
        request=ChatUserApi.get_password_request(),
        responses=ChatUserApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_EDIT, RoleConstants.ADMIN)
    @log(
        menu="Chat user management",
        operate="Reset chat user password",
        get_operation_object=lambda r, k: {"id": k.get("user_id")},
    )
    def put(self, request: Request, user_id: str):
        return result.success(
            ChatUserPasswordSerializer(data=request.data).save(user_id)
        )


class ChatUserBatchAddGroupView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Batch set chat user groups"),
        description=_("Batch set chat user groups"),
        operation_id=_("Batch set chat user groups"),
        tags=[_("Chat User Management")],
        request=ChatUserApi.get_group_request(),
        responses=ChatUserApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_GROUP, RoleConstants.ADMIN)
    @log(menu="Chat user management", operate="Batch set chat user groups")
    def post(self, request: Request):
        return result.success(
            ChatUserGroupAssignmentSerializer(data=request.data).save()
        )


class ChatUserBatchDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Batch delete chat users"),
        description=_("Batch delete chat users"),
        operation_id=_("Batch delete chat users"),
        tags=[_("Chat User Management")],
        request=ChatUserApi.get_batch_delete_request(),
        responses=ChatUserApi.get_default_response(),
    )
    @has_permissions(PermissionConstants.CHAT_USER_DELETE, RoleConstants.ADMIN)
    @log(menu="Chat user management", operate="Batch delete chat users")
    def post(self, request: Request):
        if not isinstance(request.data, list):
            raise AppApiException(500, _("Chat user IDs are required"))
        return result.success(
            ChatUserBatchDeleteSerializer(data={"ids": request.data}).save()
        )


class ChatUserSyncTypeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get chat user sync types"),
        description=_("Get chat user sync types"),
        operation_id=_("Get chat user sync types"),
        tags=[_("Chat User Management")],
        responses=ChatUserSyncTypeResult,
    )
    @has_permissions(PermissionConstants.CHAT_USER_SYNC, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(ChatUserSyncSerializer.get_sync_types())


class ChatUserSyncView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Sync chat users"),
        description=_("Sync chat users"),
        operation_id=_("Sync chat users"),
        tags=[_("Chat User Management")],
        parameters=[
            OpenApiParameter(
                name="sync_type",
                description=_("Sync type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ],
        responses=ChatUserSyncResult,
    )
    @has_permissions(PermissionConstants.CHAT_USER_SYNC, RoleConstants.ADMIN)
    @log(menu="Chat user management", operate="Sync chat users")
    def post(self, request: Request, sync_type: str):
        return result.success(ChatUserSyncSerializer.sync(sync_type))
