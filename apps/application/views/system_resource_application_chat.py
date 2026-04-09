# coding=utf-8
"""
    @project: MaxKB
    @Author：OpenCode
    @file： system_resource_application_chat.py
    @date：2026/4/3
    @desc:
"""

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.api.application_chat import ApplicationChatExportAPI, ApplicationChatQueryPageAPI
from application.api.application_chat_record import (
    ApplicationChatRecordAddKnowledgeAPI,
    ApplicationChatRecordImproveParagraphAPI,
    ApplicationChatRecordPageQueryAPI,
    ApplicationChatRecordQueryAPI,
)
from application.models import Application
from application.serializers.application_chat import ApplicationChatQuerySerializers
from application.serializers.application_chat_record import (
    ApplicationChatRecordAddKnowledgeSerializer,
    ApplicationChatRecordImproveSerializer,
    ApplicationChatRecordQuerySerializers,
    ChatRecordImproveSerializer,
    ChatRecordOperateSerializer,
)
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.utils.common import query_params_to_single_dict


def _get_application_workspace_id(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return application_model.workspace_id
    return None


class SystemResourceApplicationChat(APIView):
    authentication_classes = [TokenAuth]

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the system resource conversation list by page"),
            summary=_("Get the system resource conversation list by page"),
            operation_id=_("Get the system resource conversation list by page"),  # type: ignore
            request=ApplicationChatQueryPageAPI.get_request(),
            parameters=ApplicationChatQueryPageAPI.get_parameters(),
            responses=ApplicationChatQueryPageAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_READ,
            RoleConstants.ADMIN,
        )
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            workspace_id = _get_application_workspace_id(application_id)
            return result.success(ApplicationChatQuerySerializers(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'application_id': application_id,
                }
            ).page(current_page=current_page, page_size=page_size))

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_("Export system resource conversation"),
            summary=_("Export system resource conversation"),
            operation_id=_("Export system resource conversation"),  # type: ignore
            request=ApplicationChatExportAPI.get_request(),
            parameters=ApplicationChatExportAPI.get_parameters(),
            responses=ApplicationChatExportAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_EXPORT,
            RoleConstants.ADMIN,
        )
        def post(self, request: Request, application_id: str):
            workspace_id = _get_application_workspace_id(application_id)
            return ApplicationChatQuerySerializers(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'application_id': application_id,
                }
            ).export(request.data)


class SystemResourceApplicationChatRecord(APIView):
    authentication_classes = [TokenAuth]

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_("Get the system resource conversation record list by page"),
            summary=_("Get the system resource conversation record list by page"),
            operation_id=_("Get the system resource conversation record list by page"),  # type: ignore
            request=ApplicationChatRecordPageQueryAPI.get_request(),
            parameters=ApplicationChatRecordPageQueryAPI.get_parameters(),
            responses=ApplicationChatRecordPageQueryAPI.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_READ,
            RoleConstants.ADMIN,
        )
        def get(self, request: Request, application_id: str, chat_id: str, current_page: int, page_size: int):
            workspace_id = _get_application_workspace_id(application_id)
            return result.success(ApplicationChatRecordQuerySerializers(
                data={
                    **query_params_to_single_dict(request.query_params),
                    'workspace_id': workspace_id,
                    'application_id': application_id,
                    'chat_id': chat_id,
                }
            ).page(current_page=current_page, page_size=page_size))


class SystemResourceApplicationChatRecordOperate(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get system resource conversation record details"),
        summary=_("Get system resource conversation record details"),
        operation_id=_("Get system resource conversation record details"),  # type: ignore
        request=ApplicationChatRecordQueryAPI.get_request(),
        parameters=ApplicationChatRecordQueryAPI.get_parameters(),
        responses=ApplicationChatRecordQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_READ,
        RoleConstants.ADMIN,
    )
    def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
        workspace_id = _get_application_workspace_id(application_id)
        return result.success(ChatRecordOperateSerializer(
            data={
                'workspace_id': workspace_id,
                'application_id': application_id,
                'chat_id': chat_id,
                'chat_record_id': chat_record_id,
            }
        ).one(True))


class SystemResourceApplicationChatRecordAddKnowledge(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_("Add system resource conversation to Knowledge Base"),
        summary=_("Add system resource conversation to Knowledge Base"),
        operation_id=_("Add system resource conversation to Knowledge Base"),  # type: ignore
        request=ApplicationChatRecordAddKnowledgeAPI.get_request(),
        parameters=[
            OpenApiParameter(
                name='application_id',
                description='Application ID',
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ],
        responses=ApplicationChatRecordAddKnowledgeAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE,
        RoleConstants.ADMIN,
    )
    def post(self, request: Request, application_id: str):
        workspace_id = _get_application_workspace_id(application_id)
        payload = {
            **request.data,
            'workspace_id': workspace_id,
            'application_id': application_id,
        }
        return result.success(
            ApplicationChatRecordAddKnowledgeSerializer(data=payload).post_improve(
                payload,
                request=request,
                scope='SYSTEM_RESOURCE',
            )
        )


class SystemResourceApplicationChatRecordImprove(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_("Get system resource marked paragraph list"),
        summary=_("Get system resource marked paragraph list"),
        operation_id=_("Get system resource marked paragraph list"),  # type: ignore
        request=ApplicationChatRecordQueryAPI.get_request(),
        parameters=[
            OpenApiParameter(name='application_id', description='Application ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='chat_id', description='Chat ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='chat_record_id', description='Chat Record ID', type=OpenApiTypes.STR, location='path', required=True),
        ],
        responses=ApplicationChatRecordQueryAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_ANNOTATION, RoleConstants.ADMIN)
    def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
        workspace_id = _get_application_workspace_id(application_id)
        return result.success(ChatRecordImproveSerializer(data={
            'workspace_id': workspace_id,
            'application_id': application_id,
            'chat_id': chat_id,
            'chat_record_id': chat_record_id,
        }).get())


class SystemResourceApplicationChatRecordImproveParagraph(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['PUT'],
        description=_("Annotate system resource chat record"),
        summary=_("Annotate system resource chat record"),
        operation_id=_("Annotate system resource chat record"),  # type: ignore
        request=ApplicationChatRecordImproveParagraphAPI.get_request(),
        parameters=[
            OpenApiParameter(name='application_id', description='Application ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='chat_id', description='Chat ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='chat_record_id', description='Chat Record ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='knowledge_id', description='Knowledge ID', type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='document_id', description='Document ID', type=OpenApiTypes.STR, location='path', required=True),
        ],
        responses=ApplicationChatRecordImproveParagraphAPI.get_response(),
        tags=[_("Application/Conversation Log")]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_ANNOTATION, RoleConstants.ADMIN)
    def put(self, request: Request, application_id: str, chat_id: str, chat_record_id: str,
            knowledge_id: str, document_id: str):
        workspace_id = _get_application_workspace_id(application_id)
        return result.success(ApplicationChatRecordImproveSerializer(data={
            'workspace_id': workspace_id,
            'application_id': application_id,
            'chat_id': chat_id,
            'chat_record_id': chat_record_id,
            'knowledge_id': knowledge_id,
            'document_id': document_id,
        }).improve(request.data, request=request, scope='SYSTEM_RESOURCE'))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            description=_("Delete system resource annotation"),
            summary=_("Delete system resource annotation"),
            operation_id=_("Delete system resource annotation"),  # type: ignore
            request=ApplicationChatRecordImproveParagraphAPI.Operate.get_request(),
            parameters=[
                OpenApiParameter(name='application_id', description='Application ID', type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='chat_id', description='Chat ID', type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='chat_record_id', description='Chat Record ID', type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='knowledge_id', description='Knowledge ID', type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='document_id', description='Document ID', type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='paragraph_id', description='Paragraph ID', type=OpenApiTypes.STR, location='path', required=True),
            ],
            responses=ApplicationChatRecordImproveParagraphAPI.Operate.get_response(),
            tags=[_("Application/Conversation Log")]  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_APPLICATION_CHAT_LOG_ANNOTATION, RoleConstants.ADMIN)
        def delete(self, request: Request, application_id: str, chat_id: str, chat_record_id: str,
                   knowledge_id: str, document_id: str, paragraph_id: str):
            workspace_id = _get_application_workspace_id(application_id)
            return result.success(ApplicationChatRecordImproveSerializer.Operate(data={
                'workspace_id': workspace_id,
                'chat_id': chat_id,
                'chat_record_id': chat_record_id,
                'knowledge_id': knowledge_id,
                'document_id': document_id,
                'paragraph_id': paragraph_id,
            }).delete(request=request, scope='SYSTEM_RESOURCE'))
