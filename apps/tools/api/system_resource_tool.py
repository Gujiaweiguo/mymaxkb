from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from common.result import ResultPageSerializer
from tools.serializers.system_resource_tool import (
    SystemResourceToolItemSerializer,
    SystemResourceToolQuerySerializer,
    SystemResourceToolRecordItemSerializer,
)
from tools.serializers.tool import ToolRecordModelSerializer


class SystemResourceToolPageResult(ResultPageSerializer):
    def get_data(self):
        return SystemResourceToolItemSerializer(many=True)


class SystemResourceToolQueryAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='current_page',
                description=_('Current page'),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='page_size',
                description=_('Page size'),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='name',
                description=_('Tool Name'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='create_user',
                description=_('Create User'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='tool_type',
                description=_('Tool Type'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='source',
                description=_('Tool Source'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='workspace_ids',
                description=_('Workspace IDs JSON'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]

    @staticmethod
    def get_request():
        return SystemResourceToolQuerySerializer

    @staticmethod
    def get_response():
        return SystemResourceToolPageResult


class SystemResourceToolRecordPageResult(ResultPageSerializer):
    def get_data(self):
        return SystemResourceToolRecordItemSerializer(many=True)


class SystemResourceToolRecordDetailResult(ResultSerializer):
    def get_data(self):
        return ToolRecordModelSerializer()


class SystemResourceToolRecordPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='tool_id',
                description=_('Tool ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='current_page',
                description=_('Current page'),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='page_size',
                description=_('Page size'),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='source_name',
                description=_('Source name'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='source_type',
                description=_('Source type'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name='state',
                description=_('State'),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return SystemResourceToolRecordPageResult


class SystemResourceToolRecordDetailAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='tool_id',
                description=_('Tool ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name='record_id',
                description=_('Record ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return SystemResourceToolRecordDetailResult
