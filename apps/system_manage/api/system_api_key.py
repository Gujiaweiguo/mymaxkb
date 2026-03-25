from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultSerializer
from system_manage.serializers.system_api_key import (
    EditSystemApiKeySerializer,
    SystemApiKeySerializerModel,
)


class SystemApiKeyListResult(ResultSerializer):
    def get_data(self):
        return SystemApiKeySerializerModel(many=True)


class SystemApiKeyResult(ResultSerializer):
    def get_data(self):
        return SystemApiKeySerializerModel()


class SystemApiKeyAPI(APIMixin):
    @staticmethod
    def get_response():
        return SystemApiKeyResult

    class List(APIMixin):
        @staticmethod
        def get_response():
            return SystemApiKeyListResult

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                OpenApiParameter(
                    name="api_key_id",
                    description="ApiKeyId",
                    type=OpenApiTypes.STR,
                    location="path",
                    required=True,
                )
            ]

        @staticmethod
        def get_request():
            return EditSystemApiKeySerializer
