from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_api_key import (
    ApplicationKeyListSerializerModel,
    ApplicationKeySerializerModel,
    EditApplicationKeySerializer,
)
from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer, ResultSerializer


class ApplicationKeyListResult(ResultSerializer):
    def get_data(self):
        return ApplicationKeyListSerializerModel(many=True)


class ApplicationKeyResult(ResultSerializer):
    def get_data(self):
        return ApplicationKeySerializerModel()


class ApplicationKeyPageResult(ResultPageSerializer):
    def get_data(self):
        return ApplicationKeyListSerializerModel(many=True)


class ApplicationKeyAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return ApplicationKeyResult

    class List(APIMixin):
        @staticmethod
        def get_response():
            return ApplicationKeyListResult

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [*ApplicationKeyAPI.get_parameters(), OpenApiParameter(
                name="api_key_id",
                description="ApiKeyId",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )]

        @staticmethod
        def get_request():
            return EditApplicationKeySerializer


class SystemResourceApplicationKeyAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return ApplicationKeyResult

    class List(APIMixin):
        @staticmethod
        def get_response():
            return ApplicationKeyPageResult

        @staticmethod
        def get_parameters():
            return [
                *SystemResourceApplicationKeyAPI.get_parameters(),
                OpenApiParameter(
                    name="current_page",
                    description="Current page",
                    type=OpenApiTypes.INT,
                    location='path',
                    required=True,
                ),
                OpenApiParameter(
                    name="page_size",
                    description="Page size",
                    type=OpenApiTypes.INT,
                    location='path',
                    required=True,
                ),
            ]

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                *SystemResourceApplicationKeyAPI.get_parameters(),
                OpenApiParameter(
                    name="api_key_id",
                    description="ApiKeyId",
                    type=OpenApiTypes.STR,
                    location='path',
                    required=True,
                )
            ]

        @staticmethod
        def get_request():
            return EditApplicationKeySerializer
