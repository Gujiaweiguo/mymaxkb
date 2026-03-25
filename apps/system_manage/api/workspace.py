# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： workspace.py
@date：2026/3/23
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import (
    ResultSerializer,
    DefaultResultSerializer,
    ResultPageSerializer,
)
from rest_framework import serializers
from system_manage.serializers.workspace import (
    WorkspaceDeleteCheckSerializer,
    WorkspaceItemSerializer,
    WorkspaceMemberCreateItemSerializer,
    WorkspaceMemberItemSerializer,
    WorkspaceOperateSerializer,
)


class WorkspaceListResult(ResultSerializer):
    def get_data(self):
        return WorkspaceItemSerializer(many=True)


class WorkspaceResult(ResultSerializer):
    def get_data(self):
        return WorkspaceItemSerializer()


class WorkspaceDeleteCheckResult(ResultSerializer):
    def get_data(self):
        return WorkspaceDeleteCheckSerializer()


class WorkspaceRoleItemSerializer(serializers.Serializer):
    id = WorkspaceOperateSerializer().fields["name"]
    name = WorkspaceOperateSerializer().fields["name"]
    type = WorkspaceOperateSerializer().fields["name"]


class WorkspaceRoleListResult(ResultSerializer):
    def get_data(self):
        return WorkspaceRoleItemSerializer(many=True)


class WorkspaceMemberPageResult(ResultPageSerializer):
    def get_data(self):
        return WorkspaceMemberItemSerializer(many=True)


class WorkspaceAPI(APIMixin):
    @staticmethod
    def get_request():
        return WorkspaceOperateSerializer

    @staticmethod
    def get_response():
        return WorkspaceResult

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                OpenApiParameter(
                    name="workspace_id",
                    description=_("Workspace ID"),
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.PATH,
                    required=True,
                )
            ]

        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class DeleteCheck(APIMixin):
        @staticmethod
        def get_parameters():
            return WorkspaceAPI.Operate.get_parameters()

        @staticmethod
        def get_response():
            return WorkspaceDeleteCheckResult

    class MemberPage(APIMixin):
        @staticmethod
        def get_parameters():
            return WorkspaceAPI.Operate.get_parameters() + [
                OpenApiParameter(
                    name="current_page",
                    description=_("Current page"),
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                ),
                OpenApiParameter(
                    name="page_size",
                    description=_("Page size"),
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                ),
            ]

        @staticmethod
        def get_response():
            return WorkspaceMemberPageResult

    class MemberCreate(APIMixin):
        @staticmethod
        def get_parameters():
            return WorkspaceAPI.Operate.get_parameters()

        @staticmethod
        def get_request():
            return WorkspaceMemberCreateItemSerializer(many=True)

        @staticmethod
        def get_response():
            return DefaultResultSerializer

    class MemberDelete(APIMixin):
        @staticmethod
        def get_parameters():
            return WorkspaceAPI.Operate.get_parameters() + [
                OpenApiParameter(
                    name="user_relation_id",
                    description=_("Workspace member relation ID"),
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.PATH,
                    required=True,
                )
            ]

        @staticmethod
        def get_response():
            return DefaultResultSerializer


class WorkspaceRoleAPI(APIMixin):
    @staticmethod
    def get_response():
        return WorkspaceRoleListResult
