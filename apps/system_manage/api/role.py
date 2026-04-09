from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer, ResultSerializer
from system_manage.serializers.role import (
    SystemRoleListResponseSerializer,
    SystemRoleMemberItemSerializer,
    SystemRolePermissionModuleSerializer,
)


class SystemRoleListResult(ResultSerializer):
    def get_data(self):
        return SystemRoleListResponseSerializer()


class SystemRolePermissionResult(ResultSerializer):
    def get_data(self):
        return SystemRolePermissionModuleSerializer(many=True)


class SystemRoleMemberPageResult(ResultPageSerializer):
    def get_data(self):
        return SystemRoleMemberItemSerializer(many=True)


class SystemRoleAPI(APIMixin):
    @staticmethod
    def get_response():
        return SystemRoleListResult


class SystemRolePermissionAPI(APIMixin):
    @staticmethod
    def get_response():
        return SystemRolePermissionResult


class SystemRoleMemberAPI(APIMixin):
    @staticmethod
    def get_page_parameters():
        return [
            OpenApiParameter(
                name="role_id",
                description=_("Role ID"),
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
            OpenApiParameter(
                name="username",
                description=_("Username"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="nick_name",
                description=_("Nickname"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ]

    @staticmethod
    def get_page_response():
        return SystemRoleMemberPageResult
