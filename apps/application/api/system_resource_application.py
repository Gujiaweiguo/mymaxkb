# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： system_resource_application.py
@date：2026/3/23
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.system_resource_application import (
    SystemResourceApplicationItemSerializer,
    SystemResourceApplicationQuerySerializer,
)
from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer


class SystemResourceApplicationPageResult(ResultPageSerializer):
    def get_data(self):
        return SystemResourceApplicationItemSerializer(many=True)


class SystemResourceApplicationQueryAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description=_("Page size"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description=_("Application Name"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="create_user",
                description=_("Create User"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="type",
                description=_("Application Type"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="workspace_ids",
                description=_("Workspace IDs JSON"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                description=_("Status JSON"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
        ]

    @staticmethod
    def get_request():
        return SystemResourceApplicationQuerySerializer

    @staticmethod
    def get_response():
        return SystemResourceApplicationPageResult
