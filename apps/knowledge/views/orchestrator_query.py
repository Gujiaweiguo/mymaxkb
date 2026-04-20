# pyright: reportImplicitRelativeImport=false, reportAttributeAccessIssue=false, reportReturnType=false, reportIncompatibleMethodOverride=false, reportMissingTypeArgument=false, reportOptionalMemberAccess=false

import copy
import logging
from collections.abc import Mapping
from typing import Any, cast

import uuid_utils.compat as uuid
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from application.serializers.common import ChatInfo
from chat.serializers.chat import ChatSerializers
from application.models import Application, ApplicationApiKey, Chat, ChatSourceChoices, ChatUserType
from common.handle.base_to_response import BaseToResponse
from knowledge.models import Document
from system_manage.models.resource_mapping import ResourceMapping

from ..services.orchestrator_session import (
    build_user_binding_hash,
    get_session_binding,
    set_session_binding,
    touch_session_binding,
)
from ..serializers.orchestrator_query import (
    OrchestratorErrorResponseSerializer,
    OrchestratorPreviewResponseSerializer,
    OrchestratorQueryErrorCode,
    OrchestratorQueryRequestSerializer,
    OrchestratorQueryResponseSerializer,
)

logger = logging.getLogger(__name__)


class OrchestratorPipelineToResponse(BaseToResponse):
    def to_block_response(
        self,
        chat_id,
        chat_record_id,
        content,
        is_end,
        completion_tokens,
        prompt_tokens,
        other_params: dict | None = None,
        _status=status.HTTP_200_OK,
    ):
        return {
            'chat_id': str(chat_id),
            'chat_record_id': str(chat_record_id),
            'content': content,
            'is_end': is_end,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'status': _status,
            'other_params': other_params or {},
        }

    def to_stream_chunk_response(
        self,
        chat_id,
        chat_record_id,
        node_id,
        up_node_id_list,
        content,
        is_end,
        completion_tokens,
        prompt_tokens,
        other_params: dict | None = None,
    ):
        return None


class OrchestratorQueryView(APIView):
    authentication_classes = []
    permission_classes = []

    def perform_authentication(self, request: Request):
        return

    def post(self, request: Request):
        try:
            bearer_token = self._get_bearer_token(request)
            serializer = OrchestratorQueryRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return self._error_response(
                    OrchestratorQueryErrorCode.INVALID_REQUEST,
                    self._build_validation_message(serializer.errors),
                    status.HTTP_400_BAD_REQUEST,
                )

            validated_data = cast(dict[str, Any], serializer.validated_data)
            application_api_key, application = self._authenticate_application(bearer_token)
            if application_api_key is None or application is None:
                return self._error_response(
                    OrchestratorQueryErrorCode.UNAUTHORIZED,
                    'Invalid API key',
                    status.HTTP_401_UNAUTHORIZED,
                )

            params = cast(Mapping[str, Any], validated_data.get('params') or {})
            if params.get('_param_preview'):
                return self._preview_response(bearer_token, application)
            return self._normal_response(validated_data, application_api_key, application)
        except ParseError as exc:
            return self._error_response(
                OrchestratorQueryErrorCode.INVALID_REQUEST,
                str(exc.detail),
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception('Unhandled orchestrator knowledge query error')
            return self._error_response(
                OrchestratorQueryErrorCode.INTERNAL_ERROR,
                'Internal error',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def _get_bearer_token(request: Request) -> str:
        authorization = request.headers.get('Authorization', '')
        if authorization.startswith('Bearer '):
            return authorization.removeprefix('Bearer ').strip()
        return ''

    def _preview_response(self, bearer_token: str, application: Application) -> Response:
        from knowledge.models import Knowledge

        mapped_knowledge_ids = [
            str(row.target_id)
            for row in ResourceMapping.objects.filter(
                source_id=str(application.id),
                source_type='APPLICATION',
                target_type='KNOWLEDGE',
            )
        ]
        knowledge_map = {
            str(k.id): k.name
            for k in Knowledge.objects.filter(id__in=mapped_knowledge_ids)
        }
        kb_scope_options = [
            {'label': knowledge_map.get(kid, kid), 'value': kid}
            for kid in mapped_knowledge_ids
        ]

        knowledge_setting = application.knowledge_setting or {}
        default_top_n = knowledge_setting.get('top_n', 3)
        default_similarity = knowledge_setting.get('similarity', 0.6)

        param_schema = {
            'kb_scope': {
                'type': 'array',
                'items': {'type': 'string'},
                'options': kb_scope_options,
                'description': 'Knowledge base scope — restricts retrieval to selected knowledge bases',
            },
            'top_n': {
                'type': 'integer',
                'default': default_top_n,
                'minimum': 1,
                'maximum': 100,
                'step': 1,
                'description': 'Number of top matching paragraphs to retrieve',
            },
            'similarity': {
                'type': 'number',
                'default': default_similarity,
                'minimum': 0.0,
                'maximum': 1.0,
                'step': 0.01,
                'description': 'Minimum similarity threshold for retrieval',
            },
        }

        response_data = OrchestratorPreviewResponseSerializer(
            {'param_schema': param_schema}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    def _normal_response(
        self,
        validated_data: dict[str, Any],
        application_api_key: ApplicationApiKey,
        application: Application,
    ) -> Response:
        session_id = str(validated_data.get('session_id') or '').strip()
        context = cast(dict[str, Any], validated_data.get('context') or {})
        params = cast(dict[str, Any], validated_data.get('params') or {})
        question = str(validated_data.get('question') or '')
        knowledge_id_list = self._resolve_knowledge_scope(application, context.get('kb_scope'))
        if knowledge_id_list is None:
            return self._error_response(
                OrchestratorQueryErrorCode.KNOWLEDGE_SCOPE_INVALID,
                'kb_scope contains knowledge outside the application mapping',
                status.HTTP_400_BAD_REQUEST,
            )
        binding_hash = build_user_binding_hash(context)
        chat_id = self._resolve_chat_id(
            session_id=session_id,
            question=question,
            application_api_key=application_api_key,
            application=application,
            user_binding_hash=binding_hash,
        )
        if chat_id is None:
            return self._error_response(
                OrchestratorQueryErrorCode.SESSION_MISMATCH,
                'Session binding does not match the current request context',
                status.HTTP_409_CONFLICT,
            )

        chat_serializer = self._build_chat_serializer(chat_id, application_api_key, application)
        chat_serializer.is_valid(raise_exception=True)
        chat_info = self._build_chat_info(chat_serializer, chat_id, application)
        chat_info.get_application()
        chat_info.get_chat_user()
        chat_serializer.is_valid_chat_id(chat_info)
        chat_serializer.is_valid_chat_user()
        chat_serializer.is_valid_application_simple(raise_exception=True, chat_info=chat_info)

        chat_info.knowledge_id_list = knowledge_id_list
        chat_info.exclude_document_id_list = self._get_excluded_document_id_list(knowledge_id_list)
        chat_info.application.knowledge_setting = self._resolve_knowledge_setting(
            chat_info.application, params
        )
        resolved_application = chat_info.application
        chat_info.get_application = lambda: resolved_application
        chat_info.set_cache()

        pipeline_result = chat_serializer.chat_simple(
            chat_info,
            {'message': question, 're_chat': False, 'stream': False},
            OrchestratorPipelineToResponse(),
        )
        if int(pipeline_result.get('status') or status.HTTP_200_OK) >= status.HTTP_400_BAD_REQUEST:
            raise RuntimeError(str(pipeline_result.get('content') or 'Pipeline execution failed'))

        latest_chat_record = chat_info.chat_record_list[-1] if len(chat_info.chat_record_list) > 0 else None
        search_step = (
            latest_chat_record.details.get('search_step', {})
            if latest_chat_record is not None and isinstance(latest_chat_record.details, dict)
            else {}
        )
        paragraph_list = search_step.get('paragraph_list') or []
        tokens_used = int(pipeline_result.get('prompt_tokens') or 0) + int(
            pipeline_result.get('completion_tokens') or 0
        )

        references = [
            {
                'title': p.get('document_name', '') or p.get('title', ''),
                'snippet': (p.get('content', '') or '')[:200],
                'document_id': str(p.get('document_id', '')),
                'paragraph_id': str(p.get('id', '')),
                'knowledge_name': p.get('knowledge_name', ''),
                'confidence': p.get('comprehensive_score'),
            }
            for p in paragraph_list
        ]

        # v1: suggestions return [] as conservative default.
        # Task 8 hardening will add retrieval-grounded suggestion generation.
        suggestions: list[str] = []

        response_data = OrchestratorQueryResponseSerializer(
            {
                'text': str(pipeline_result.get('content') or ''),
                'references': references,
                'suggestions': suggestions,
                'cards': [],
                'meta': {
                    'chat_id': chat_id,
                    'tokens_used': tokens_used,
                    'hit_paragraph_count': len(paragraph_list),
                },
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    def _build_chat_serializer(
        self,
        chat_id: str,
        application_api_key: ApplicationApiKey,
        application: Application,
    ) -> ChatSerializers:
        return ChatSerializers(
            data={
                'chat_id': chat_id,
                'chat_user_id': str(application_api_key.id),
                'chat_user_type': ChatUserType.APPLICATION_API_KEY,
                'application_id': application.id,
                'debug': False,
                'ip_address': '-',
                'source': {'type': ChatSourceChoices.API_CALL.value},
            }
        )

    @staticmethod
    def _build_chat_info(
        chat_serializer: ChatSerializers, chat_id: str, application: Application
    ) -> ChatInfo:
        chat_info = ChatInfo.get_cache(chat_id)
        if chat_info is None:
            chat_info = chat_serializer.re_open_chat_simple(chat_id, application)
        return chat_info

    @staticmethod
    def _normalize_scope_values(kb_scope: Any) -> tuple[bool, list[str] | None]:
        if kb_scope is None:
            return True, None
        if isinstance(kb_scope, str):
            value = kb_scope.strip()
            return True, ([] if len(value) == 0 else [value])
        if isinstance(kb_scope, (list, tuple, set)):
            values: list[str] = []
            for item in kb_scope:
                if isinstance(item, Mapping) or isinstance(item, (list, tuple, set)):
                    return False, None
                value = str(item).strip()
                if len(value) > 0:
                    values.append(value)
            return True, values
        return False, None

    def _resolve_knowledge_scope(self, application: Application, kb_scope: Any) -> list[str] | None:
        mapped_knowledge_id_list = [
            str(row.target_id)
            for row in ResourceMapping.objects.filter(
                source_id=str(application.id),
                source_type='APPLICATION',
                target_type='KNOWLEDGE',
            )
        ]
        is_valid, scope_values = self._normalize_scope_values(kb_scope)
        if not is_valid:
            return None
        if scope_values is None:
            return mapped_knowledge_id_list
        invalid_scope_values = [value for value in scope_values if value not in mapped_knowledge_id_list]
        if len(invalid_scope_values) > 0:
            return None
        return [knowledge_id for knowledge_id in mapped_knowledge_id_list if knowledge_id in scope_values]

    @staticmethod
    def _get_excluded_document_id_list(knowledge_id_list: list[str]) -> list[str]:
        return [
            str(document.id)
            for document in Document.objects.filter(knowledge_id__in=knowledge_id_list, is_active=False)
        ]

    @staticmethod
    def _resolve_knowledge_setting(application: Any, params: Mapping[str, Any]) -> dict[str, Any]:
        knowledge_setting = copy.deepcopy(application.knowledge_setting or {})
        if params.get('top_n') is not None:
            knowledge_setting['top_n'] = params.get('top_n')
        if params.get('similarity') is not None:
            knowledge_setting['similarity'] = params.get('similarity')
        return knowledge_setting

    def _error_response(self, error_code: str, message: str, response_status: int) -> Response:
        response_data = OrchestratorErrorResponseSerializer(
            {'error_code': error_code, 'message': message}
        ).data
        return Response(response_data, status=response_status)

    @staticmethod
    def _build_validation_message(errors: Any) -> str:
        first_field, first_error = next(iter(cast(dict[str, Any], errors).items()))
        if isinstance(first_error, (list, tuple)) and len(first_error) > 0:
            return f'{first_field}: {first_error[0]}'
        return f'{first_field}: {first_error}'

    @staticmethod
    def _authenticate_application(bearer_token: str) -> tuple[ApplicationApiKey | None, Application | None]:
        if not bearer_token:
            return None, None

        now = timezone.now()
        application_api_key = cast(
            ApplicationApiKey | None,
            ApplicationApiKey.objects
            .filter(secret_key=bearer_token, is_active=True)
            .filter(Q(is_permanent=True) | Q(expire_time__gt=now))
            .select_related('application')
            .first(),
        )
        if application_api_key is None or application_api_key.application is None:
            return None, None

        application = cast(Application | None, cast(object, application_api_key.application))
        if application is None:
            return None, None
        return application_api_key, application

    def _resolve_chat_id(
        self,
        *,
        session_id: str,
        question: str,
        application_api_key: ApplicationApiKey,
        application: Application,
        user_binding_hash: str,
    ) -> str | None:
        if not session_id:
            return self._create_internal_chat(application, application_api_key, question)

        binding = get_session_binding(session_id)
        if binding is None:
            chat_id = self._create_internal_chat(application, application_api_key, question)
            _ = set_session_binding(
                session_id,
                chat_id=chat_id,
                application_id=str(application.id),
                api_key_id=str(application_api_key.id),
                user_binding_hash=user_binding_hash,
            )
            return chat_id

        if (
            binding.get('application_id') != str(application.id)
            or binding.get('api_key_id') != str(application_api_key.id)
            or binding.get('user_binding_hash') != user_binding_hash
        ):
            return None

        _ = touch_session_binding(session_id, binding)
        return str(binding.get('chat_id') or '')

    @staticmethod
    def _create_internal_chat(
        application: Application,
        application_api_key: ApplicationApiKey,
        question: str,
    ) -> str:
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=application,
            abstract=question[:1024],
            chat_user_id=str(application_api_key.id),
            chat_user_type=ChatUserType.APPLICATION_API_KEY,
            source={'type': ChatSourceChoices.API_CALL.value},
            ip_address='-',
        )
        return str(chat.id)
