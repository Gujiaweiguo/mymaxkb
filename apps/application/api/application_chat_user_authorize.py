from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_chat_user_authorize import (
    ApplicationChatUserEditSerializer,
    ApplicationChatUserGroupEditSerializer,
    ApplicationChatUserGroupItemSerializer,
    ApplicationChatUserGroupUserItemSerializer,
)
from common.mixins.api_mixin import APIMixin
from common.result import (
    DefaultResultSerializer,
    ResultPageSerializer,
    ResultSerializer,
)


class ApplicationChatUserGroupListResult(ResultSerializer):
    def get_data(self):
        return ApplicationChatUserGroupItemSerializer(many=True)


class ApplicationChatUserGroupUserPageResult(ResultPageSerializer):
    def get_data(self):
        return ApplicationChatUserGroupUserItemSerializer(many=True)


class ApplicationChatUserAuthTypeResult(ResultSerializer):
    def get_data(self):
        from rest_framework import serializers

        class Data(serializers.Serializer):
            label = serializers.CharField(required=True)
            value = serializers.CharField(required=True)

        return Data(many=True)


class ApplicationChatUserAuthorizeAPI(APIMixin):
    @staticmethod
    def get_workspace_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description=_("Workspace ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name="resource_type",
                description=_("Resource type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name="resource_id",
                description=_("Resource ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]

    @staticmethod
    def get_system_parameters():
        return [
            OpenApiParameter(
                name="resource_type",
                description=_("Resource type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name="resource_id",
                description=_("Resource ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]

    @staticmethod
    def get_user_group_parameters():
        return [
            OpenApiParameter(
                name="user_group_id",
                description=_("User group ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
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
    def get_group_request():
        return ApplicationChatUserGroupEditSerializer(many=True)

    @staticmethod
    def get_user_request():
        return ApplicationChatUserEditSerializer(many=True)

    @staticmethod
    def get_group_response():
        return ApplicationChatUserGroupListResult

    @staticmethod
    def get_user_page_response():
        return ApplicationChatUserGroupUserPageResult

    @staticmethod
    def get_default_response():
        return DefaultResultSerializer
