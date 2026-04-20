from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class OrchestratorQueryErrorCode:
    INVALID_REQUEST = 'INVALID_REQUEST'
    UNAUTHORIZED = 'UNAUTHORIZED'
    SESSION_MISMATCH = 'SESSION_MISMATCH'
    KNOWLEDGE_SCOPE_INVALID = 'KNOWLEDGE_SCOPE_INVALID'
    INTERNAL_ERROR = 'INTERNAL_ERROR'

    CHOICES = {
        INVALID_REQUEST,
        UNAUTHORIZED,
        SESSION_MISMATCH,
        KNOWLEDGE_SCOPE_INVALID,
        INTERNAL_ERROR,
    }


class OrchestratorQueryContextSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False, allow_blank=True)
    role_code = serializers.CharField(required=False, allow_blank=True)
    project_id = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)
    kb_scope = serializers.JSONField(required=False)


class OrchestratorQueryParamsSerializer(serializers.Serializer):
    _param_preview = serializers.BooleanField(required=False, default=False)
    top_n = serializers.IntegerField(required=False)
    similarity = serializers.FloatField(required=False)
    kb_scope = serializers.JSONField(required=False)


class OrchestratorQueryRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False, label=_('question'))
    session_id = serializers.CharField(required=False, allow_blank=True)
    request_id = serializers.CharField(required=False, allow_blank=True)
    trace_id = serializers.CharField(required=False, allow_blank=True)
    context = OrchestratorQueryContextSerializer(required=False)  # pyright: ignore[reportIncompatibleMethodOverride, reportAssignmentType]
    params = OrchestratorQueryParamsSerializer(required=False)


class OrchestratorQueryMetaSerializer(serializers.Serializer):
    chat_id = serializers.CharField(required=False, allow_blank=True, default='')
    tokens_used = serializers.IntegerField(required=False, default=0)
    hit_paragraph_count = serializers.IntegerField(required=False, default=0)


class OrchestratorQueryResponseSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True, default='')
    references = serializers.ListField(required=False, default=list)
    suggestions = serializers.ListField(required=False, default=list)
    cards = serializers.ListField(required=False, default=list)
    meta = OrchestratorQueryMetaSerializer(required=False, default=dict)


class OrchestratorPreviewResponseSerializer(serializers.Serializer):
    param_schema = serializers.DictField(required=True)


class OrchestratorErrorResponseSerializer(serializers.Serializer):
    error_code = serializers.ChoiceField(choices=sorted(OrchestratorQueryErrorCode.CHOICES))
    message = serializers.CharField(required=True)
