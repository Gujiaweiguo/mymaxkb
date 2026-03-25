from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import (
    DefaultResultSerializer,
    ResultPageSerializer,
    ResultSerializer,
)
from knowledge.serializers.knowledge_chat_user_authorize import (
    KnowledgeChatUserEditSerializer,
    KnowledgeChatUserGroupEditSerializer,
    KnowledgeChatUserGroupItemSerializer,
    KnowledgeChatUserGroupUserItemSerializer,
)


class KnowledgeChatUserGroupListResult(ResultSerializer):
    def get_data(self):
        return KnowledgeChatUserGroupItemSerializer(many=True)


class KnowledgeChatUserGroupUserPageResult(ResultPageSerializer):
    def get_data(self):
        return KnowledgeChatUserGroupUserItemSerializer(many=True)


class KnowledgeChatUserAuthorizeAPI(APIMixin):
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
                name="resource_id",
                description=_("Resource ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
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
        return KnowledgeChatUserGroupEditSerializer(many=True)

    @staticmethod
    def get_user_request():
        return KnowledgeChatUserEditSerializer(many=True)

    @staticmethod
    def get_group_response():
        return KnowledgeChatUserGroupListResult

    @staticmethod
    def get_user_page_response():
        return KnowledgeChatUserGroupUserPageResult

    @staticmethod
    def get_default_response():
        return DefaultResultSerializer
