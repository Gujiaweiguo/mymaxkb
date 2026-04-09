# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： resource_mapping.py
    @date：2025/12/25 15:28
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import Permission, Group, Operate, RoleConstants, ViewPermission, \
    CompareConstants, PermissionConstants
from common.exception.app_exception import AppApiException
from system_manage.api.resource_mapping import ResourceMappingAPI
from system_manage.serializers.resource_mapping_serializers import ResourceMappingSerializer


def get_system_resource_mapping_permission(resource: str):
    permission_map = {
        'APPLICATION': PermissionConstants.RESOURCE_APPLICATION_RELATE_RESOURCE_VIEW,
        'KNOWLEDGE': PermissionConstants.RESOURCE_KNOWLEDGE_RELATE_RESOURCE_VIEW,
        'MODEL': PermissionConstants.RESOURCE_MODEL_RELATE_RESOURCE_VIEW,
        'TOOL': PermissionConstants.RESOURCE_TOOL_RELATE_RESOURCE_VIEW,
    }
    permission = permission_map.get(resource)
    if permission is None:
        raise AppApiException(404, _('Unsupported system resource mapping type'))
    return permission


class ResourceMappingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Retrieve the pagination list of resource relationships'),
        operation_id=_('Retrieve the pagination list of resource relationships'),  # type: ignore
        responses=ResourceMappingAPI.get_response(),
        parameters=ResourceMappingAPI.get_parameters(),
        tags=[_('Resources mapping')]  # type: ignore
    )
    @has_permissions(
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.RELATE_VIEW,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/WORKSPACE_MANAGE"),
        lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                     operate=Operate.RELATE_VIEW,
                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('resource_id')}"),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [lambda r, kwargs: Permission(group=Group(kwargs.get('resource')),
                                                     operate=Operate.SELF,
                                                     resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}/{kwargs.get('resource')}/{kwargs.get('resource_id')}")],
                       CompareConstants.AND),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def get(self, request: Request, workspace_id: str, resource: str, resource_id: str, current_page, page_size):
        return result.success(ResourceMappingSerializer({
            'resource': resource,
            'resource_id': resource_id,
            'resource_name': request.query_params.get('resource_name'),
            'user_name': request.query_params.get('user_name'),
            'source_type': request.query_params.getlist('source_type[]'),
            'workspace_ids': request.query_params.get('workspace_ids'),
        }).page(current_page, page_size))


class SystemResourceMappingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Retrieve the pagination list of system resource relationships'),
        operation_id=_('Retrieve the pagination list of system resource relationships'),  # type: ignore
        responses=ResourceMappingAPI.get_response(),
        parameters=ResourceMappingAPI.get_parameters()[1:],
        tags=[_('Resources mapping')]  # type: ignore
    )
    @has_permissions(lambda r, kwargs: get_system_resource_mapping_permission(kwargs.get('resource')), RoleConstants.ADMIN)
    def get(self, request: Request, resource: str, resource_id: str, current_page, page_size):
        return result.success(ResourceMappingSerializer({
            'resource': resource,
            'resource_id': resource_id,
            'resource_name': request.query_params.get('resource_name'),
            'user_name': request.query_params.get('user_name'),
            'source_type': request.query_params.getlist('source_type[]'),
            'workspace_ids': request.query_params.get('workspace_ids'),
        }).page(current_page, page_size))
