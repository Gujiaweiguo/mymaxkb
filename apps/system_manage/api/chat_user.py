from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import (
    DefaultResultSerializer,
    ResultPageSerializer,
    ResultSerializer,
)
from system_manage.serializers.chat_user import (
    ChatUserBatchDeleteSerializer,
    ChatUserGroupAssignmentSerializer,
    ChatUserInstanceSerializer,
    ChatUserManageSerializer,
    ChatUserPasswordSerializer,
)


class ChatUserListResult(ResultSerializer):
    def get_data(self):
        return ChatUserInstanceSerializer(many=True)


class ChatUserPageResult(ResultPageSerializer):
    def get_data(self):
        return ChatUserInstanceSerializer(many=True)


class ChatUserApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="user_id",
                description=_("Chat user ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ]

    @staticmethod
    def get_page_parameters():
        return [
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
    def get_list_response():
        return ChatUserListResult

    @staticmethod
    def get_page_response():
        return ChatUserPageResult

    @staticmethod
    def get_create_request():
        return ChatUserManageSerializer.Create

    @staticmethod
    def get_update_request():
        return ChatUserManageSerializer.Update

    @staticmethod
    def get_password_request():
        return ChatUserPasswordSerializer

    @staticmethod
    def get_group_request():
        return ChatUserGroupAssignmentSerializer

    @staticmethod
    def get_batch_delete_request():
        return serializers.ListSerializer(
            child=serializers.CharField(required=True),
            required=True,
            label=_("Chat user IDs"),
        )

    @staticmethod
    def get_default_response():
        return DefaultResultSerializer


class ChatUserSyncTypeResult(ResultSerializer):
    def get_data(self):
        return serializers.ListField(
            child=serializers.CharField(required=True), required=True
        )


class ChatUserSyncResult(ResultSerializer):
    def get_data(self):
        class Data(serializers.Serializer):
            success_count = serializers.IntegerField(required=True)
            conflict_users = serializers.ListField(required=True)
            sync_type = serializers.CharField(required=True)

        return Data()
