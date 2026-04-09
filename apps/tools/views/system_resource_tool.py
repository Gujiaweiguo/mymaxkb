from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.exception.app_exception import AppApiException
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from tools.api.system_resource_tool import (
    SystemResourceToolQueryAPI,
    SystemResourceToolRecordDetailAPI,
    SystemResourceToolRecordPageAPI,
)
from tools.api.tool import EditIconAPI, PylintAPI, ToolDebugApi, ToolExportAPI, ToolImportAPI, ToolTestConnectionApi
from tools.models import Tool
from tools.serializers.tool import ToolEditRequest, ToolModelSerializer, ToolSerializer
from tools.serializers.system_resource_tool import SystemResourceToolQuerySerializer


def get_tool_operation_object(tool_id: str):
    tool_model = QuerySet(model=Tool).filter(id=tool_id).first()
    if tool_model is not None:
        return {'name': tool_model.name}
    return {}


def get_tool_workspace_id(tool_id: str):
    tool_model = QuerySet(model=Tool).filter(id=tool_id).first()
    if tool_model is None:
        raise AppApiException(500, _('Tool id does not exist'))
    return tool_model.workspace_id


class SystemResourceToolView(APIView):
    authentication_classes = [TokenAuth]

    class Pylint(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            summary=_('Check system tool code'),
            operation_id=_('Check system tool code'),  # type: ignore
            description=_('Check system tool code'),
            request=PylintAPI.get_request(),
            responses=PylintAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_READ, RoleConstants.ADMIN)
        def post(self, request: Request):
            return result.success(ToolSerializer.Pylint(data={'workspace_id': 'system-resource'}).run(request.data))

    class UploadSkillFile(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['PUT'],
            summary=_('Upload system tool skill file'),
            operation_id=_('Upload system tool skill file'),  # type: ignore
            description=_('Upload system tool skill file'),
            request=ToolImportAPI.get_request(),
            responses=ToolImportAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EDIT, RoleConstants.ADMIN)
        def put(self, request: Request):
            return result.success(
                ToolSerializer.UploadSkillFile(
                    data={
                        'workspace_id': 'system-resource',
                        'user_id': request.user.id,
                        'file': request.FILES.get('file'),
                    }
                ).upload()
            )

    class TestConnection(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Test system tool connection'),
            summary=_('Test system tool connection'),
            operation_id=_('Test system tool connection'),  # type: ignore
            request=ToolTestConnectionApi.get_request(),
            responses=ToolTestConnectionApi.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EDIT, RoleConstants.ADMIN)
        def post(self, request: Request):
            return result.success(
                ToolSerializer.TestConnection(
                    data={'workspace_id': 'system-resource', 'code': request.data.get('code')}
                ).test_connection()
            )

    class Debug(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['POST'],
            description=_('Debug system tool resource'),
            summary=_('Debug system tool resource'),
            operation_id=_('Debug system tool resource'),  # type: ignore
            request=ToolDebugApi.get_request(),
            responses=ToolDebugApi.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EDIT, RoleConstants.ADMIN)
        def post(self, request: Request):
            return result.success(
                ToolSerializer.Debug(data={'workspace_id': 'system-resource', 'user_id': request.user.id}).debug(
                    request.data
                )
            )

    class PageToolRecord(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system tool resource records'),
            summary=_('Get system tool resource records'),
            operation_id=_('Get system tool resource records'),  # type: ignore
            parameters=SystemResourceToolRecordPageAPI.get_parameters(),
            responses=SystemResourceToolRecordPageAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EXECUTE_RECORD, RoleConstants.ADMIN)
        def get(self, request: Request, tool_id: str, current_page: int, page_size: int):
            workspace_id = get_tool_workspace_id(tool_id)
            return result.success(ToolSerializer.ToolRecord(data={
                'tool_id': tool_id,
                'workspace_id': workspace_id,
                'source_name': request.query_params.get('source_name'),
                'source_type': request.query_params.get('source_type'),
                'state': request.query_params.get('state'),
            }).get_tool_records(current_page, page_size))

    class ToolRecord(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system tool resource record detail'),
            summary=_('Get system tool resource record detail'),
            operation_id=_('Get system tool resource record detail'),  # type: ignore
            parameters=SystemResourceToolRecordDetailAPI.get_parameters(),
            responses=SystemResourceToolRecordDetailAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EXECUTE_RECORD, RoleConstants.ADMIN)
        def get(self, request: Request, tool_id: str, record_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            return result.success(ToolSerializer.ToolRecord.Operate(data={
                'tool_id': tool_id,
                'workspace_id': workspace_id,
                'id': record_id,
            }).one())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system tool resource list by page'),
            summary=_('Get system tool resource list by page'),
            operation_id=_('Get system tool resource list by page'),  # type: ignore
            parameters=SystemResourceToolQueryAPI.get_parameters(),
            responses=SystemResourceToolQueryAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, current_page: int, page_size: int):
            serializer = SystemResourceToolQuerySerializer(data=request.query_params)
            return result.success(serializer.page(current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system tool resource detail'),
            summary=_('Get system tool resource detail'),
            operation_id=_('Get system tool resource detail'),  # type: ignore
            parameters=[
                OpenApiParameter(
                    name='tool_id',
                    description=_('Tool ID'),
                    type=OpenApiTypes.STR,
                    location='path',
                    required=True,
                )
            ],
            responses=ToolModelSerializer,
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, tool_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            return result.success(ToolSerializer.Operate(data={'id': tool_id, 'workspace_id': workspace_id}).one())

        @extend_schema(
            methods=['PUT'],
            description=_('Update system tool resource'),
            summary=_('Update system tool resource'),
            operation_id=_('Update system tool resource'),  # type: ignore
            parameters=[
                OpenApiParameter(
                    name='tool_id',
                    description=_('Tool ID'),
                    type=OpenApiTypes.STR,
                    location='path',
                    required=True,
                )
            ],
            request=ToolEditRequest,
            responses=ToolModelSerializer,
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EDIT, RoleConstants.ADMIN)
        @log(
            menu='Tool',
            operate='Update system tool',
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def put(self, request: Request, tool_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            return result.success(
                ToolSerializer.Operate(data={'id': tool_id, 'workspace_id': workspace_id}).edit(request.data)
            )

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete system tool resource'),
            summary=_('Delete system tool resource'),
            operation_id=_('Delete system tool resource'),  # type: ignore
            parameters=[
                OpenApiParameter(
                    name='tool_id',
                    description=_('Tool ID'),
                    type=OpenApiTypes.STR,
                    location='path',
                    required=True,
                )
            ],
            responses=None,
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_DELETE, RoleConstants.ADMIN)
        @log(
            menu='Tool',
            operate='Delete system tool',
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def delete(self, request: Request, tool_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            return result.success(ToolSerializer.Operate(data={'id': tool_id, 'workspace_id': workspace_id}).delete())

    class EditIcon(APIView):
        authentication_classes = [TokenAuth]
        parser_classes = [MultiPartParser]

        @extend_schema(
            methods=['PUT'],
            summary=_('Edit system tool icon'),
            operation_id=_('Edit system tool icon'),  # type: ignore
            description=_('Edit system tool icon'),
            request=EditIconAPI.get_request(),
            responses=EditIconAPI.get_response(),
            parameters=EditIconAPI.get_parameters()[1:],
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EDIT, RoleConstants.ADMIN)
        def put(self, request: Request, tool_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            uploaded_file = request.FILES.get('file') or request.data.get('file')
            return result.success(
                ToolSerializer.IconOperate(
                    data={
                        'id': tool_id,
                        'workspace_id': workspace_id,
                        'user_id': request.user.id,
                        'image': uploaded_file,
                    }
                ).edit(request.data)
            )

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Export system tool resource'),
            summary=_('Export system tool resource'),
            operation_id=_('Export system tool resource'),  # type: ignore
            parameters=ToolExportAPI.get_parameters()[1:],
            responses=ToolExportAPI.get_response(),
            tags=[_('Tool')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_TOOL_EXPORT, RoleConstants.ADMIN)
        @log(
            menu='Tool',
            operate='Export system tool',
            get_operation_object=lambda r, k: get_tool_operation_object(k.get('tool_id')),
        )
        def get(self, request: Request, tool_id: str):
            workspace_id = get_tool_workspace_id(tool_id)
            return ToolSerializer.Operate(data={'id': tool_id, 'workspace_id': workspace_id}).export()
