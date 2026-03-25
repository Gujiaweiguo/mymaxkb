from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result, DefaultResultSerializer
from system_manage.api.system_api_key import SystemApiKeyAPI
from system_manage.serializers.system_api_key import SystemApiKeySerializer


class SystemApiKeyView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create system API key"),
        summary=_("Create system API key"),
        operation_id="create_system_api_key",
        request=None,
        responses=SystemApiKeyAPI.get_response(),
        tags=["System API Key"],
    )
    @has_permissions(PermissionConstants.SYSTEM_API_KEY_EDIT, RoleConstants.ADMIN)
    @log(menu="System API Key", operate="Create system API key")
    def post(self, request: Request):
        return result.success(SystemApiKeySerializer(data={}).generate())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get system API key list"),
            summary=_("Get system API key list"),
            operation_id="get_system_api_key_list",
            responses=SystemApiKeyAPI.List.get_response(),
            tags=["System API Key"],
        )
        @has_permissions(PermissionConstants.SYSTEM_API_KEY_EDIT, RoleConstants.ADMIN)
        def get(self, request: Request, current_page: int, page_size: int):
            return result.success(
                SystemApiKeySerializer(
                    data={"order_by": request.query_params.get("order_by")}
                ).page(current_page, page_size)
            )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            description=_("Modify system API key"),
            summary=_("Modify system API key"),
            operation_id="modify_system_api_key",
            parameters=SystemApiKeyAPI.Operate.get_parameters(),
            request=SystemApiKeyAPI.Operate.get_request(),
            responses=DefaultResultSerializer,
            tags=["System API Key"],
        )
        @has_permissions(PermissionConstants.SYSTEM_API_KEY_EDIT, RoleConstants.ADMIN)
        @log(menu="System API Key", operate="Modify system API key")
        def put(self, request: Request, api_key_id: str):
            return result.success(
                SystemApiKeySerializer.Operate(data={"api_key_id": api_key_id}).edit(
                    request.data
                )
            )

        @extend_schema(
            methods=["DELETE"],
            description=_("Delete system API key"),
            summary=_("Delete system API key"),
            operation_id="delete_system_api_key",
            parameters=SystemApiKeyAPI.Operate.get_parameters(),
            request=None,
            responses=DefaultResultSerializer,
            tags=["System API Key"],
        )
        @has_permissions(PermissionConstants.SYSTEM_API_KEY_EDIT, RoleConstants.ADMIN)
        @log(menu="System API Key", operate="Delete system API key")
        def delete(self, request: Request, api_key_id: str):
            return result.success(
                SystemApiKeySerializer.Operate(data={"api_key_id": api_key_id}).delete()
            )
