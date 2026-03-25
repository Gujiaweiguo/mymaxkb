from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import (
    PermissionConstants,
    RoleConstants,
)
from common.result import result
from common.utils.common import query_params_to_single_dict
from system_manage.serializers.log_management import OperateLogSerializer


class OperateLogPageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get operation logs"),
        description=_("Get operation logs"),
        tags=["Operation Log"],
        responses=None,
    )
    @has_permissions(PermissionConstants.OPERATION_LOG_READ, RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        return result.success(
            OperateLogSerializer.page(
                query_params_to_single_dict(request.query_params),
                current_page,
                page_size,
            )
        )


class OperateLogMenuOptionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get operation log menu options"),
        description=_("Get operation log menu options"),
        tags=["Operation Log"],
        responses=None,
    )
    @has_permissions(PermissionConstants.OPERATION_LOG_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(OperateLogSerializer.menu_operation_option())


class OperateLogExportView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        summary=_("Export operation logs"),
        description=_("Export operation logs"),
        tags=["Operation Log"],
        request=None,
        responses=None,
    )
    @has_permissions(PermissionConstants.OPERATION_LOG_EXPORT, RoleConstants.ADMIN)
    def post(self, request: Request):
        return OperateLogSerializer.export(request.data)


class OperateLogCleanTimeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get operation log clean time"),
        description=_("Get operation log clean time"),
        tags=["Operation Log"],
        responses=None,
    )
    @has_permissions(
        PermissionConstants.OPERATION_LOG_CLEAR_POLICY, RoleConstants.ADMIN
    )
    def get(self, request: Request):
        return result.success(OperateLogSerializer.get_clean_time())

    @extend_schema(
        methods=["POST"],
        summary=_("Save operation log clean time"),
        description=_("Save operation log clean time"),
        tags=["Operation Log"],
        request=None,
        responses=None,
    )
    @has_permissions(
        PermissionConstants.OPERATION_LOG_CLEAR_POLICY, RoleConstants.ADMIN
    )
    def post(self, request: Request):
        return result.success(OperateLogSerializer.save_clean_time(request.data))
