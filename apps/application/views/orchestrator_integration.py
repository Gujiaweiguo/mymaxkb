# coding=utf-8
import hashlib

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.models import Application
from application.models.application_api_key import ApplicationApiKey
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import (
    PermissionConstants,
    RoleConstants,
    ViewPermission,
    CompareConstants,
)
from common import result
from system_manage.models.resource_mapping import ResourceMapping


class OrchestratorIntegrationConfigView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get Orchestrator integration config'),
        summary=_('Get Orchestrator integration config'),
        operation_id=_('Get Orchestrator integration config'),  # type: ignore
        responses=result.DefaultResultSerializer,
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.APPLICATION_READ.get_workspace_application_permission(),
        PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.APPLICATION.get_workspace_application_permission()],
            CompareConstants.AND,
        ),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str, application_id: str):
        application = QuerySet(Application).filter(id=application_id).first()
        if application is None:
            return result.error(_('Application does not exist'))

        api_key = (
            QuerySet(ApplicationApiKey)
            .filter(application_id=application_id, is_active=True, is_permanent=True)
            .order_by('-create_time')
            .first()
        )
        if api_key is None:
            secret_key = 'agent-' + hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()
            api_key = ApplicationApiKey(
                id=uuid.uuid7(),
                secret_key=secret_key,
                application_id=application_id,
                is_active=True,
                is_permanent=True,
            )
            api_key.save()

        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        endpoint_url = f'{scheme}://{host}/api/knowledge'

        mappings = (
            ResourceMapping.objects
            .filter(source_type='APPLICATION', target_type='KNOWLEDGE', source_id=str(application_id))
            .values_list('target_id', flat=True)
        )
        kb_scope = [str(tid) for tid in mappings]

        knowledge_setting = application.knowledge_setting or {}
        top_n = knowledge_setting.get('top_n', 3)
        similarity = knowledge_setting.get('similarity', 0.6)

        return result.success({
            'endpoint_url': endpoint_url,
            'auth_token': api_key.secret_key,
            'default_params': {
                'kb_scope': kb_scope,
                'top_n': top_n,
                'similarity': similarity,
            },
        })
