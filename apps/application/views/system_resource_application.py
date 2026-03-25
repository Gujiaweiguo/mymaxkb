# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： system_resource_application.py
@date：2026/3/23
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.system_resource_application import (
    SystemResourceApplicationQueryAPI,
)
from application.serializers.system_resource_application import (
    SystemResourceApplicationQuerySerializer,
)
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants


class SystemResourceApplicationView(APIView):
    authentication_classes = [TokenAuth]

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get system application resource list by page"),
            summary=_("Get system application resource list by page"),
            operation_id=_("Get system application resource list by page"),  # type: ignore
            parameters=SystemResourceApplicationQueryAPI.get_parameters(),
            responses=SystemResourceApplicationQueryAPI.get_response(),
            tags=[_("Application")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN
        )
        def get(self, request: Request, current_page: int, page_size: int):
            serializer = SystemResourceApplicationQuerySerializer(
                data=request.query_params
            )
            return result.success(serializer.page(current_page, page_size))
