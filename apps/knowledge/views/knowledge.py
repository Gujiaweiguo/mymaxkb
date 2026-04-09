from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import (
    PermissionConstants,
    RoleConstants,
    ViewPermission,
    CompareConstants,
)
from common.exception.app_exception import NotFound404
from common.log.log import log
from common.result import result
from knowledge.api.knowledge import (
    KnowledgeBaseCreateAPI,
    KnowledgeWebCreateAPI,
    KnowledgeTreeReadAPI,
    KnowledgeEditAPI,
    KnowledgeReadAPI,
    KnowledgePageAPI,
    SyncWebAPI,
    GenerateRelatedAPI,
    HitTestAPI,
    EmbeddingAPI,
    GetModelAPI,
    KnowledgeExportAPI,
    KnowledgeLarkCreateAPI,
    KnowledgeLarkUpdateAPI,
)
from knowledge.api.system_resource_knowledge import (
    SystemResourceDocumentCancelTaskAPI,
    SystemResourceDocumentExportAPI,
    SystemResourceDocumentExportZipAPI,
    SystemResourceDocumentDeleteAPI,
    SystemResourceDocumentEditAPI,
    SystemResourceDocumentPageAPI,
    SystemResourceDocumentRefreshAPI,
    SystemResourceDocumentReadAPI,
    SystemResourceDocumentSyncAPI,
)
from knowledge.api.system_resource_knowledge import (
    SystemResourceKnowledgeDeleteAPI,
    SystemResourceKnowledgeEditAPI,
    SystemResourceKnowledgeEmbeddingAPI,
    SystemResourceKnowledgeExportAPI,
    SystemResourceKnowledgeGenerateRelatedAPI,
    SystemResourceKnowledgeHitTestAPI,
    SystemResourceKnowledgeQueryAPI,
    SystemResourceKnowledgeReadAPI,
    SystemResourceKnowledgeSyncAPI,
)
from knowledge.models import Knowledge, KnowledgeScope
from knowledge.serializers.document import DocumentSerializers
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.serializers.system_resource_knowledge import SystemResourceKnowledgeQuerySerializer
from knowledge.views.common import (
    get_document_operation_object,
    get_knowledge_document_operation_object,
)
from models_provider.serializers.model_serializer import ModelSerializer
from tools.api.tool import GetInternalToolAPI


def get_system_resource_knowledge_workspace_id(knowledge_id: str):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).only('workspace_id').first()
    if knowledge is None:
        raise NotFound404(404, _("Knowledge id does not exist"))
    return knowledge.workspace_id


class KnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get knowledge by folder"),
        summary=_("Get knowledge by folder"),
        operation_id=_("Get knowledge by folder"),  # type: ignore
        parameters=KnowledgeTreeReadAPI.get_parameters(),
        responses=KnowledgeTreeReadAPI.get_response(),
        tags=[_("Knowledge Base")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        RoleConstants.USER.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str):
        return result.success(
            KnowledgeSerializer.Query(
                data={
                    "workspace_id": workspace_id,
                    "folder_id": request.query_params.get("folder_id"),
                    "name": request.query_params.get("name"),
                    "desc": request.query_params.get("desc"),
                    "scope": KnowledgeScope.WORKSPACE,
                    "user_id": request.user.id,
                }
            ).list()
        )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            description=_("Edit knowledge"),
            summary=_("Edit knowledge"),
            operation_id=_("Edit knowledge"),  # type: ignore
            parameters=KnowledgeEditAPI.get_parameters(),
            request=KnowledgeEditAPI.get_request(),
            responses=KnowledgeEditAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Modify knowledge base information",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                    }
                ).edit(request.data)
            )

        @extend_schema(
            methods=["DELETE"],
            description=_("Delete knowledge"),
            summary=_("Delete knowledge"),
            operation_id=_("Delete knowledge"),  # type: ignore
            parameters=KnowledgeBaseCreateAPI.get_parameters(),
            request=KnowledgeBaseCreateAPI.get_request(),
            responses=KnowledgeBaseCreateAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Delete knowledge base",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                    }
                ).delete()
            )

        @extend_schema(
            methods=["GET"],
            description=_("Get knowledge"),
            summary=_("Get knowledge"),
            operation_id=_("Get knowledge"),  # type: ignore
            parameters=KnowledgeReadAPI.get_parameters(),
            responses=KnowledgeReadAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                    }
                ).one()
            )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get the knowledge base paginated list"),
            summary=_("Get the knowledge base paginated list"),
            operation_id=_("Get the knowledge base paginated list"),  # type: ignore
            parameters=KnowledgePageAPI.get_parameters(),
            responses=KnowledgePageAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        def get(
            self, request: Request, workspace_id: str, current_page: int, page_size: int
        ):
            return result.success(
                KnowledgeSerializer.Query(
                    data={
                        "workspace_id": workspace_id,
                        "folder_id": request.query_params.get("folder_id"),
                        "name": request.query_params.get("name"),
                        "desc": request.query_params.get("desc"),
                        "scope": KnowledgeScope.WORKSPACE,
                        "user_id": request.user.id,
                        "create_user": request.query_params.get("create_user"),
                    }
                ).page(current_page, page_size)
            )

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            summary=_("Synchronize the knowledge base of the website"),
            description=_("Synchronize the knowledge base of the website"),
            operation_id=_("Synchronize the knowledge base of the website"),  # type: ignore
            parameters=SyncWebAPI.get_parameters(),
            request=SyncWebAPI.get_request(),
            responses=SyncWebAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_SYNC.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_SYNC.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Synchronize the knowledge base of the website",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.SyncWeb(
                    data={
                        "workspace_id": workspace_id,
                        "sync_type": request.query_params.get("sync_type"),
                        "knowledge_id": knowledge_id,
                        "user_id": str(request.user.id),
                    }
                ).sync()
            )

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["POST"],
            summary=_("Hit test list"),
            description=_("Hit test list"),
            operation_id=_("Hit test list"),  # type: ignore
            parameters=HitTestAPI.get_parameters(),
            request=HitTestAPI.get_request(),
            responses=HitTestAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_HIT_TEST.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_HIT_TEST.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.HitTest(
                    data={
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                        "user_id": request.user.id,
                        "query_text": request.data.get("query_text"),
                        "top_number": request.data.get("top_number"),
                        "similarity": request.data.get("similarity"),
                        "search_mode": request.data.get("search_mode"),
                    }
                ).hit_test()
            )

    class StoreKnowledge(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get Appstore tools"),
            summary=_("Get Appstore tools"),
            operation_id=_("Get Appstore tools"),  # type: ignore
            responses=GetInternalToolAPI.get_response(),
            tags=[_("Tool")],  # type: ignore
        )
        def get(self, request: Request):
            return result.success(
                KnowledgeSerializer.StoreKnowledge(
                    data={
                        "user_id": request.user.id,
                        "name": request.query_params.get("name", ""),
                    }
                ).get_appstore_templates()
            )

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            summary=_("Re-vectorize"),
            description=_("Re-vectorize"),
            operation_id=_("Re-vectorize"),  # type: ignore
            parameters=EmbeddingAPI.get_parameters(),
            request=EmbeddingAPI.get_request(),
            responses=EmbeddingAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_VECTOR.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_VECTOR.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Re-vectorize",
            get_operation_object=lambda r, k: get_knowledge_operation_object(
                k.get("knowledge_id")
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        "knowledge_id": knowledge_id,
                        "workspace_id": workspace_id,
                        "user_id": request.user.id,
                    }
                ).embedding()
            )

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Export knowledge base"),
            operation_id=_("Export knowledge base"),  # type: ignore
            parameters=KnowledgeExportAPI.get_parameters(),
            responses=KnowledgeExportAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Export knowledge base",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return KnowledgeSerializer.Operate(
                data={
                    "workspace_id": workspace_id,
                    "knowledge_id": knowledge_id,
                    "user_id": request.user.id,
                }
            ).export_excel()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Export knowledge base containing images"),
            operation_id=_("Export knowledge base containing images"),  # type: ignore
            parameters=KnowledgeExportAPI.get_parameters(),
            responses=KnowledgeExportAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EXPORT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Export knowledge base containing images",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def get(self, request: Request, workspace_id: str, knowledge_id: str):
            return KnowledgeSerializer.Operate(
                data={
                    "workspace_id": workspace_id,
                    "knowledge_id": knowledge_id,
                    "user_id": request.user.id,
                }
            ).export_zip()

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["PUT"],
            summary=_("Generate related"),
            description=_("Generate related"),
            operation_id=_("Generate related"),  # type: ignore
            parameters=GenerateRelatedAPI.get_parameters(),
            request=GenerateRelatedAPI.get_request(),
            responses=GenerateRelatedAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_GENERATE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_GENERATE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="document",
            operate="Generate related documents",
            get_operation_object=lambda r, k: get_knowledge_operation_object(
                k.get("knowledge_id")
            ),
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        "knowledge_id": knowledge_id,
                        "workspace_id": workspace_id,
                        "user_id": request.user.id,
                    }
                ).generate_related(request.data)
            )

    class Model(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            summary=_("Get model for knowledge base"),
            description=_("Get model for knowledge base"),
            operation_id=_("Get model for knowledge base"),  # type: ignore
            parameters=GetModelAPI.get_parameters(),
            responses=GetModelAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                ModelSerializer.Query(
                    data={"workspace_id": workspace_id, "model_type": "LLM"}
                ).list(workspace_id, True)
            )

    class EmbeddingModel(APIView):
        authentication_classes = [TokenAuth]

        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                ModelSerializer.Query(
                    data={"workspace_id": workspace_id, "model_type": "EMBEDDING"}
                ).list(workspace_id, True)
            )

    class TransformWorkflow(APIView):
        authentication_classes = [TokenAuth]

        @has_permissions(
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission(
                [RoleConstants.USER.get_workspace_role()],
                [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                CompareConstants.AND,
            ),
        )
        @log(
            menu="Knowledge Base",
            operate="Modify knowledge base information",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get("knowledge_id")
            ),
        )
        def post(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(
                KnowledgeSerializer.TransformWorkflow(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "knowledge_id": knowledge_id,
                    }
                ).transform(request.data)
            )

    class Tags(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get all tags of knowledge base"),
            summary=_("Get all tags of knowledge base"),
            operation_id=_("Get all tags of knowledge base"),  # type: ignore
            parameters=KnowledgeReadAPI.get_parameters(),
            responses=KnowledgeReadAPI.get_response(),
            tags=[_("Knowledge Base")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            RoleConstants.USER.get_workspace_role(),
        )
        def get(self, request: Request, workspace_id: str):
            return result.success(
                KnowledgeSerializer.Tags(
                    data={
                        "user_id": request.user.id,
                        "workspace_id": workspace_id,
                        "knowledge_ids": request.query_params.getlist(
                            "knowledge_ids[]"
                        ),
                    }
                ).list()
            )


class SystemResourceKnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Export system knowledge resource'),
            summary=_('Export system knowledge resource'),
            operation_id=_('Export system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeExportAPI.get_parameters(),
            responses=SystemResourceKnowledgeExportAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_EXPORT, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Export knowledge base',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def get(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return KnowledgeSerializer.Operate(
                data={
                    'user_id': request.user.id,
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                }
            ).export_excel()

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Export system knowledge resource with images'),
            summary=_('Export system knowledge resource with images'),
            operation_id=_('Export system knowledge resource with images'),  # type: ignore
            parameters=SystemResourceKnowledgeExportAPI.get_parameters(),
            responses=SystemResourceKnowledgeExportAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_EXPORT, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Export knowledge base containing images',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def get(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return KnowledgeSerializer.Operate(
                data={
                    'user_id': request.user.id,
                    'workspace_id': workspace_id,
                    'knowledge_id': knowledge_id,
                }
            ).export_zip()

    class Embedding(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Re-vectorize system knowledge resource'),
            summary=_('Re-vectorize system knowledge resource'),
            operation_id=_('Re-vectorize system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeEmbeddingAPI.get_parameters(),
            responses=SystemResourceKnowledgeEmbeddingAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_VECTOR, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Re-vectorize',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def put(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        'user_id': request.user.id,
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                    }
                ).embedding()
            )

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Hit test system knowledge resource'),
            summary=_('Hit test system knowledge resource'),
            operation_id=_('Hit test system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeHitTestAPI.get_parameters(),
            request=SystemResourceKnowledgeHitTestAPI.get_request(),
            responses=SystemResourceKnowledgeHitTestAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_HIT_TEST, RoleConstants.ADMIN)
        def post(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.HitTest(
                    data={
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                        'user_id': request.user.id,
                        'query_text': request.data.get('query_text'),
                        'top_number': request.data.get('top_number'),
                        'similarity': request.data.get('similarity'),
                        'search_mode': request.data.get('search_mode'),
                    }
                ).hit_test()
            )

    class GenerateRelated(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Generate related for system knowledge resource'),
            summary=_('Generate related for system knowledge resource'),
            operation_id=_('Generate related for system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeGenerateRelatedAPI.get_parameters(),
            request=SystemResourceKnowledgeGenerateRelatedAPI.get_request(),
            responses=SystemResourceKnowledgeGenerateRelatedAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_GENERATE, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Generate related documents',
            get_operation_object=lambda r, k: get_knowledge_operation_object(k.get('knowledge_id')),
        )
        def put(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        'knowledge_id': knowledge_id,
                        'workspace_id': workspace_id,
                        'user_id': request.user.id,
                    }
                ).generate_related(request.data)
            )

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Synchronize system knowledge resource'),
            summary=_('Synchronize system knowledge resource'),
            operation_id=_('Synchronize system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeSyncAPI.get_parameters(),
            responses=SystemResourceKnowledgeSyncAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_SYNC, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Synchronize the knowledge base of the website',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(
                keywords.get('knowledge_id')
            ),
        )
        def put(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.SyncWeb(
                    data={
                        'workspace_id': workspace_id,
                        'sync_type': request.query_params.get('sync_type'),
                        'knowledge_id': knowledge_id,
                        'user_id': str(request.user.id),
                    }
            ).sync()
            )
    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system knowledge resource detail'),
            summary=_('Get system knowledge resource detail'),
            operation_id=_('Get system knowledge resource detail'),  # type: ignore
            parameters=SystemResourceKnowledgeReadAPI.get_parameters(),
            responses=SystemResourceKnowledgeReadAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_READ, RoleConstants.ADMIN)
        def get(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        'user_id': request.user.id,
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                    }
                ).one()
            )

        @extend_schema(
            methods=['PUT'],
            description=_('Edit system knowledge resource'),
            summary=_('Edit system knowledge resource'),
            operation_id=_('Edit system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeEditAPI.get_parameters(),
            request=SystemResourceKnowledgeEditAPI.get_request(),
            responses=SystemResourceKnowledgeEditAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_EDIT, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Modify knowledge base information',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def put(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        'user_id': request.user.id,
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                    }
                ).edit(request.data)
            )

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete system knowledge resource'),
            summary=_('Delete system knowledge resource'),
            operation_id=_('Delete system knowledge resource'),  # type: ignore
            parameters=SystemResourceKnowledgeDeleteAPI.get_parameters(),
            responses=SystemResourceKnowledgeDeleteAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DELETE, RoleConstants.ADMIN)
        @log(
            menu='Knowledge Base',
            operate='Delete knowledge base',
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id')),
        )
        def delete(self, request: Request, knowledge_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                KnowledgeSerializer.Operate(
                    data={
                        'user_id': request.user.id,
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                    }
                ).delete()
            )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system knowledge resource list by page'),
            summary=_('Get system knowledge resource list by page'),
            operation_id=_('Get system knowledge resource list by page'),  # type: ignore
            parameters=SystemResourceKnowledgeQueryAPI.get_parameters(),
            responses=SystemResourceKnowledgeQueryAPI.get_response(),
            tags=[_('Knowledge Base')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_READ, RoleConstants.ADMIN)
        def get(self, request: Request, current_page: int, page_size: int):
            serializer = SystemResourceKnowledgeQuerySerializer(data=request.query_params)
            return result.success(serializer.page(current_page, page_size))


class SystemResourceDocumentView(APIView):
    authentication_classes = [TokenAuth]

    class Sync(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Sync system resource document'),
            summary=_('Sync system resource document'),
            operation_id=_('Sync system resource document'),  # type: ignore
            parameters=SystemResourceDocumentSyncAPI.get_parameters(),
            responses=SystemResourceDocumentSyncAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_SYNC, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Sync system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def put(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                DocumentSerializers.Sync(
                    data={
                        'document_id': document_id,
                        'knowledge_id': knowledge_id,
                        'workspace_id': workspace_id,
                    }
                ).sync()
            )

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Refresh system resource document vector library'),
            summary=_('Refresh system resource document vector library'),
            operation_id=_('Refresh system resource document vector library'),  # type: ignore
            parameters=SystemResourceDocumentRefreshAPI.get_parameters(),
            request=SystemResourceDocumentRefreshAPI.get_request(),
            responses=SystemResourceDocumentRefreshAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_VECTOR, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Refresh system resource document vector library',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def put(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                DocumentSerializers.Operate(
                    data={
                        'document_id': document_id,
                        'knowledge_id': knowledge_id,
                        'workspace_id': workspace_id,
                    }
                ).refresh(request.data.get('state_list'))
            )

    class CancelTask(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Cancel task system resource document'),
            summary=_('Cancel task system resource document'),
            operation_id=_('Cancel task system resource document'),  # type: ignore
            parameters=SystemResourceDocumentCancelTaskAPI.get_parameters(),
            request=SystemResourceDocumentCancelTaskAPI.get_request(),
            responses=SystemResourceDocumentCancelTaskAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Cancel task system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def put(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                DocumentSerializers.Operate(
                    data={
                        'workspace_id': workspace_id,
                        'document_id': document_id,
                        'knowledge_id': knowledge_id,
                    }
                ).cancel(request.data)
            )

    class ExportZip(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Export zip system resource document'),
            summary=_('Export zip system resource document'),
            operation_id=_('Export zip system resource document'),  # type: ignore
            parameters=SystemResourceDocumentExportZipAPI.get_parameters(),
            responses=SystemResourceDocumentExportZipAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Export zip system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def get(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return DocumentSerializers.Operate(
                data={
                    'workspace_id': workspace_id,
                    'document_id': document_id,
                    'knowledge_id': knowledge_id,
                }
            ).export_zip()

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Export system resource document'),
            summary=_('Export system resource document'),
            operation_id=_('Export system resource document'),  # type: ignore
            parameters=SystemResourceDocumentExportAPI.get_parameters(),
            responses=SystemResourceDocumentExportAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Export system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def get(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return DocumentSerializers.Operate(
                data={
                    'workspace_id': workspace_id,
                    'document_id': document_id,
                    'knowledge_id': knowledge_id,
                }
            ).export()

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system resource document list by page'),
            summary=_('Get system resource document list by page'),
            operation_id=_('Get system resource document list by page'),  # type: ignore
            parameters=SystemResourceDocumentPageAPI.get_parameters(),
            responses=SystemResourceDocumentPageAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_READ, RoleConstants.ADMIN)
        def get(self, request: Request, knowledge_id: str, current_page: int, page_size: int):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            raw_tags = request.query_params.getlist('tags[]')
            return result.success(
                DocumentSerializers.Query(
                    data={
                        'workspace_id': workspace_id,
                        'knowledge_id': knowledge_id,
                        'folder_id': request.query_params.get('folder_id'),
                        'name': request.query_params.get('name'),
                        'tag': request.query_params.get('tag'),
                        'tag_exclude': request.query_params.get('tag_exclude'),
                        'tag_ids': [tag for tag in raw_tags if tag != 'NO_TAG'],
                        'no_tag': 'NO_TAG' in raw_tags,
                        'desc': request.query_params.get('desc'),
                        'user_id': request.query_params.get('user_id'),
                        'status': request.query_params.get('status'),
                        'is_active': request.query_params.get('is_active'),
                        'hit_handling_method': request.query_params.get('hit_handling_method'),
                        'order_by': request.query_params.get('order_by'),
                    }
                ).page(current_page, page_size)
            )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            description=_('Get system resource document details'),
            summary=_('Get system resource document details'),
            operation_id=_('Get system resource document details'),  # type: ignore
            parameters=SystemResourceDocumentReadAPI.get_parameters(),
            responses=SystemResourceDocumentReadAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_READ, RoleConstants.ADMIN)
        def get(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            operate = DocumentSerializers.Operate(
                data={
                    'document_id': document_id,
                    'knowledge_id': knowledge_id,
                    'workspace_id': workspace_id,
                }
            )
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @extend_schema(
            methods=['PUT'],
            description=_('Edit system resource document'),
            summary=_('Edit system resource document'),
            operation_id=_('Edit system resource document'),  # type: ignore
            parameters=SystemResourceDocumentEditAPI.get_parameters(),
            request=SystemResourceDocumentEditAPI.get_request(),
            responses=SystemResourceDocumentEditAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Modify system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def put(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            return result.success(
                DocumentSerializers.Operate(
                    data={
                        'document_id': document_id,
                        'knowledge_id': knowledge_id,
                        'workspace_id': workspace_id,
                    }
                ).edit(request.data, with_valid=True)
            )

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete system resource document'),
            summary=_('Delete system resource document'),
            operation_id=_('Delete system resource document'),  # type: ignore
            parameters=SystemResourceDocumentDeleteAPI.get_parameters(),
            responses=SystemResourceDocumentDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Documentation')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_KNOWLEDGE_DOCUMENT_DELETE, RoleConstants.ADMIN)
        @log(
            menu='document',
            operate='Delete system resource document',
            get_operation_object=lambda r, keywords: get_knowledge_document_operation_object(
                get_knowledge_operation_object(keywords.get('knowledge_id')),
                get_document_operation_object(keywords.get('document_id')),
            ),
        )
        def delete(self, request: Request, knowledge_id: str, document_id: str):
            workspace_id = get_system_resource_knowledge_workspace_id(knowledge_id)
            operate = DocumentSerializers.Operate(
                data={
                    'document_id': document_id,
                    'knowledge_id': knowledge_id,
                    'workspace_id': workspace_id,
                }
            )
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())


class KnowledgeBaseView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create base knowledge"),
        summary=_("Create base knowledge"),
        operation_id=_("Create base knowledge"),  # type: ignore
        parameters=KnowledgeBaseCreateAPI.get_parameters(),
        request=KnowledgeBaseCreateAPI.get_request(),
        responses=KnowledgeBaseCreateAPI.get_response(),
        tags=[_("Knowledge Base")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        RoleConstants.USER.get_workspace_role(),
    )
    @log(
        menu="knowledge Base",
        operate="Create base knowledge",
        get_operation_object=lambda r, k: {
            "name": r.data.get("name"),
            "desc": r.data.get("desc"),
        },
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(
            KnowledgeSerializer.Create(
                data={"user_id": request.user.id, "workspace_id": workspace_id}
            ).save_base(request.data)
        )


class KnowledgeWebView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create web knowledge"),
        summary=_("Create web knowledge"),
        operation_id=_("Create web knowledge"),  # type: ignore
        parameters=KnowledgeWebCreateAPI.get_parameters(),
        request=KnowledgeWebCreateAPI.get_request(),
        responses=KnowledgeWebCreateAPI.get_response(),
        tags=[_("Knowledge Base")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        RoleConstants.USER.get_workspace_role(),
    )
    @log(
        menu="Knowledge Base",
        operate="Create a web site knowledge base",
        get_operation_object=lambda r, k: {
            "name": r.data.get("name"),
            "desc": r.data.get("desc"),
            "first_list": r.FILES.getlist("file"),
            "meta": {
                "source_url": r.data.get("source_url"),
                "selector": r.data.get("selector"),
                "embedding_model_id": r.data.get("embedding_model_id"),
            },
        },
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(
            KnowledgeSerializer.Create(
                data={"user_id": request.user.id, "workspace_id": workspace_id}
            ).save_web(request.data)
        )


class KnowledgeLarkView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Create lark knowledge"),
        summary=_("Create lark knowledge"),
        operation_id=_("Create lark knowledge"),  # type: ignore
        parameters=KnowledgeLarkCreateAPI.get_parameters(),
        request=KnowledgeLarkCreateAPI.get_request(),
        responses=KnowledgeLarkCreateAPI.get_response(),
        tags=[_("Knowledge Base")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_CREATE.get_workspace_permission(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        RoleConstants.USER.get_workspace_role(),
    )
    @log(
        menu="Knowledge Base",
        operate="Create lark knowledge",
        get_operation_object=lambda r, k: {
            "name": r.data.get("name"),
            "desc": r.data.get("desc"),
        },
    )
    def post(self, request: Request, workspace_id: str):
        return result.success(
            KnowledgeSerializer.Create(
                data={"user_id": request.user.id, "workspace_id": workspace_id}
            ).save_lark(request.data)
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Update lark knowledge"),
        summary=_("Update lark knowledge"),
        operation_id=_("Update lark knowledge"),  # type: ignore
        parameters=KnowledgeEditAPI.get_parameters(),
        request=KnowledgeLarkUpdateAPI.get_request(),
        responses=KnowledgeLarkCreateAPI.get_response(),
        tags=[_("Knowledge Base")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            CompareConstants.AND,
        ),
    )
    @log(
        menu="Knowledge Base",
        operate="Update lark knowledge",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(
            keywords.get("knowledge_id")
        ),
    )
    def put(self, request: Request, workspace_id: str, knowledge_id: str):
        request_meta = request.data.get("meta", {})

        def get_meta_value(key: str):
            if key in request.data:
                return request.data.get(key)
            if isinstance(request_meta, dict):
                return request_meta.get(key)
            return None

        meta_payload = {}
        for key in ["app_id", "app_secret", "folder_token", "embedding_model_id"]:
            value = get_meta_value(key)
            if value is not None:
                meta_payload[key] = value

        update_payload = {
            "name": request.data.get("name"),
            "desc": request.data.get("desc"),
            "folder_id": request.data.get("folder_id"),
            "embedding_model_id": request.data.get("embedding_model_id")
            or (
                request_meta.get("embedding_model_id")
                if isinstance(request_meta, dict)
                else None
            ),
            "file_count_limit": request.data.get("file_count_limit"),
            "file_size_limit": request.data.get("file_size_limit"),
        }
        update_payload = {
            key: value for key, value in update_payload.items() if value is not None
        }
        if meta_payload:
            update_payload["meta"] = meta_payload

        return result.success(
            KnowledgeSerializer.Operate(
                data={
                    "user_id": request.user.id,
                    "workspace_id": workspace_id,
                    "knowledge_id": knowledge_id,
                }
            ).edit(update_payload)
        )
