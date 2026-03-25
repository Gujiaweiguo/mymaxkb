from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import (
    DefaultResultSerializer,
    ResultPageSerializer,
    ResultSerializer,
)
from system_manage.serializers.user_group import (
    UserGroupInstanceSerializer,
    UserGroupManageSerializer,
    UserGroupMemberInstanceSerializer,
)


class UserGroupListResult(ResultSerializer):
    def get_data(self):
        return UserGroupInstanceSerializer(many=True)


class UserGroupMemberPageResult(ResultPageSerializer):
    def get_data(self):
        return UserGroupMemberInstanceSerializer(many=True)


class UserGroupApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="user_group_id",
                description=_("User group ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ]

    @staticmethod
    def get_page_parameters():
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
    def get_list_response():
        return UserGroupListResult

    @staticmethod
    def get_page_response():
        return UserGroupMemberPageResult

    @staticmethod
    def get_create_request():
        return UserGroupManageSerializer.CreateOrUpdate

    @staticmethod
    def get_add_member_request():
        return UserGroupManageSerializer.AddMember

    @staticmethod
    def get_remove_member_request():
        return UserGroupManageSerializer.RemoveMember

    @staticmethod
    def get_default_response():
        return DefaultResultSerializer
