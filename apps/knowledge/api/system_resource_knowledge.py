from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultPageSerializer, ResultSerializer
from rest_framework import serializers
from knowledge.api.knowledge import KnowledgeCreateResponse
from knowledge.serializers.common import GenerateRelatedSerializer
from knowledge.serializers.document import (
    CancelInstanceSerializer,
    DocumentEditInstanceSerializer,
    DocumentRefreshSerializer,
)
from knowledge.serializers.knowledge import HitTestSerializer, KnowledgeEditRequest
from knowledge.serializers.system_resource_knowledge import (
    SystemResourceDocumentItemSerializer,
    SystemResourceKnowledgeItemSerializer,
    SystemResourceKnowledgeQuerySerializer,
)


class SystemResourceKnowledgePageResult(ResultPageSerializer):
    def get_data(self):
        return SystemResourceKnowledgeItemSerializer(many=True)


class SystemResourceKnowledgeQueryAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='current_page',
                description=_('Current page'),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='page_size',
                description=_('Page size'),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='name',
                description=_('knowledge name'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='create_user',
                description=_('create user'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='type',
                description=_('knowledge type'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='workspace_ids',
                description=_('Workspace IDs JSON'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ]

    @staticmethod
    def get_request():
        return SystemResourceKnowledgeQuerySerializer

    @staticmethod
    def get_response():
        return SystemResourceKnowledgePageResult


class SystemResourceKnowledgeDetailResult(ResultSerializer):
    def get_data(self):
        return serializers.DictField(required=True)


class SystemResourceDocumentPageResult(ResultPageSerializer):
    def get_data(self):
        return SystemResourceDocumentItemSerializer(many=True)


class SystemResourceDocumentDetailResult(ResultSerializer):
    def get_data(self):
        return SystemResourceDocumentItemSerializer()


class SystemResourceKnowledgeReadAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='knowledge_id',
                description=_('knowledge id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return SystemResourceKnowledgeDetailResult


class SystemResourceKnowledgeEditAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_request():
        return KnowledgeEditRequest

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class SystemResourceKnowledgeDeleteAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class SystemResourceKnowledgeExportAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_response():
        return OpenApiTypes.BINARY


class SystemResourceKnowledgeEmbeddingAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceKnowledgeHitTestAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_request():
        return HitTestSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceKnowledgeGenerateRelatedAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return SystemResourceKnowledgeReadAPI.get_parameters()

    @staticmethod
    def get_request():
        return GenerateRelatedSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceKnowledgeSyncAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            *SystemResourceKnowledgeReadAPI.get_parameters(),
            OpenApiParameter(
                name='sync_type',
                description=_('sync type: replace|complete'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceDocumentPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='knowledge_id',
                description=_('knowledge id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='current_page',
                description=_('Current page'),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='page_size',
                description=_('Page size'),
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='folder_id',
                description=_('folder id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='user_id',
                description=_('user id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='name',
                description=_('document name'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='desc',
                description=_('document description'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='tag',
                description=_('tag name'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='tag_exclude',
                description=_('exclude tag name'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='status',
                description=_('document status'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='is_active',
                description=_('document is active'),
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='hit_handling_method',
                description=_('hit handling method'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='order_by',
                description=_('order by'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name='tags[]',
                description=_('tag ids'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                many=True,
            ),
        ]

    @staticmethod
    def get_response():
        return SystemResourceDocumentPageResult


class SystemResourceDocumentReadAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='knowledge_id',
                description=_('knowledge id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
            OpenApiParameter(
                name='document_id',
                description=_('document id'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return SystemResourceDocumentDetailResult


class SystemResourceDocumentEditAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_request():
        return DocumentEditInstanceSerializer


class SystemResourceDocumentDeleteAPI(SystemResourceDocumentReadAPI):
    pass


class SystemResourceDocumentExportAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_response():
        return OpenApiTypes.BINARY


class SystemResourceDocumentExportZipAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_response():
        return OpenApiTypes.BINARY


class SystemResourceDocumentCancelTaskAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_request():
        return CancelInstanceSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceDocumentRefreshAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_request():
        return DocumentRefreshSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SystemResourceDocumentSyncAPI(SystemResourceDocumentReadAPI):
    @staticmethod
    def get_response():
        return DefaultResultSerializer
