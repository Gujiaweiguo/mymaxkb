from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.shared_resource_authorization import (
    SharedResourceAuthorizationItemSerializer,
    SharedResourceAuthorizationSerializer,
)


class SharedResourceAuthorizationResult(ResultSerializer):
    def get_data(self):
        return SharedResourceAuthorizationItemSerializer()


class SharedResourceAuthorizationAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="resource_type",
                description=_("Shared resource type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name="resource_id",
                description=_("Shared resource id"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return SharedResourceAuthorizationSerializer.Operate

    @staticmethod
    def get_response():
        return SharedResourceAuthorizationResult
