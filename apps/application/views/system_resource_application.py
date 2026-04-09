# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： system_resource_application.py
@date：2026/3/23
@desc:
"""

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.request import Request
from rest_framework.views import APIView

from application.models.application_chat import ChatUserType
from application.api.system_resource_application import (
    SystemResourceApplicationQueryAPI,
)
from application.api.application_api_key import ApplicationKeyAPI, SystemResourceApplicationKeyAPI
from application.api.application_api import PlayDemoTextAPI, SpeechToTextAPI, TextToSpeechAPI
from application.api.application_stats import ApplicationStatsAPI
from application.models import Application
from application.serializers.application_api_key import ApplicationKeySerializer
from application.serializers.application import ApplicationOperateSerializer, McpServersSerializer
from application.serializers.application_access_token import AccessTokenSerializer
from application.serializers.application_stats import ApplicationStatisticsSerializer
from application.serializers.application_version import ApplicationVersionSerializer
from application.serializers.system_resource_application import (
    SystemResourceApplicationQuerySerializer,
)
from chat.api.chat_api import PromptGenerateAPI
from chat.api.chat_authentication_api import ChatOpenAPI
from chat.serializers.chat import OpenChatSerializers, PromptGenerateSerializer
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log


def _get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {"name": application_model.name}
    return {}


def _get_application_workspace_id(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return application_model.workspace_id
    return None


class SystemResourceApplicationView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system application resource list"),
        summary=_("Get system application resource list"),
        operation_id=_("Get system application resource list"),  # type: ignore
        parameters=SystemResourceApplicationQueryAPI.get_parameters()[2:],
        tags=[_("Application")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request):
        serializer = SystemResourceApplicationQuerySerializer(data=request.query_params)
        return result.success(serializer.list())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=["GET"],
            description=_("Get system application resource list by page"),
            summary=_("Get system application resource list by page"),
            operation_id=_("Get system application resource list by page"),  # type: ignore
            parameters=SystemResourceApplicationQueryAPI.get_parameters(),
            responses=SystemResourceApplicationQueryAPI.get_response(),
            tags=[_("Application")],  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN
        )
        def get(self, request: Request, current_page: int, page_size: int):
            serializer = SystemResourceApplicationQuerySerializer(
                data=request.query_params
            )
            return result.success(serializer.page(current_page, page_size))


class SystemResourceApplicationAccessTokenView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system resource application access restriction information"),
        summary=_("Get system resource application access restriction information"),
        operation_id=_("Get system resource application access restriction information"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            AccessTokenSerializer(data={"application_id": application_id}).one()
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Modify system resource application access restriction information"),
        summary=_("Modify system resource application access restriction information"),
        operation_id=_("Modify system resource application access restriction information"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Modify system resource application access token",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_ACCESS, RoleConstants.ADMIN
    )
    def put(self, request: Request, application_id: str):
        return result.success(
            AccessTokenSerializer(data={"application_id": application_id}).edit(
                request.data
            )
        )


class SystemResourceApplicationSettingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system resource application display settings"),
        summary=_("Get system resource application display settings"),
        operation_id=_("Get system resource application display settings"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_DISPLAY,
        RoleConstants.ADMIN,
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            AccessTokenSerializer(data={"application_id": application_id}).one()
        )

    @extend_schema(
        methods=["PUT"],
        description=_("Modify system resource application display settings"),
        summary=_("Modify system resource application display settings"),
        operation_id=_("Modify system resource application display settings"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Modify system resource application setting",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_DISPLAY,
        RoleConstants.ADMIN,
    )
    def put(self, request: Request, application_id: str):
        return result.success(
            AccessTokenSerializer(data={"application_id": application_id}).edit(
                request.data
            )
        )


class SystemResourceApplicationOpenView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get a temporary session id based on the system resource application id"),
        summary=_("Get a temporary session id based on the system resource application id"),
        operation_id=_("Get a temporary session id based on the system resource application id"),  # type: ignore
        parameters=ChatOpenAPI.get_parameters(),
        responses=None,
        tags=[_("Application")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            OpenChatSerializers(
                data={
                    "workspace_id": _get_application_workspace_id(application_id),
                    "application_id": application_id,
                    "chat_user_id": str(uuid.uuid7()),
                    "chat_user_type": ChatUserType.ANONYMOUS_USER,
                    "debug": True,
                }
            ).open()
        )


class SystemResourceApplicationPromptGenerateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["POST"],
        description=_("Generate prompt for system resource application"),
        summary=_("Generate prompt for system resource application"),
        operation_id=_("Generate prompt for system resource application"),  # type: ignore
        request=PromptGenerateAPI.get_request(),
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="model_id",
                description=_("Model ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        responses=None,
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Generate prompt for system resource application",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN
    )
    def post(self, request: Request, application_id: str, model_id: str):
        return PromptGenerateSerializer(
            data={
                "workspace_id": _get_application_workspace_id(application_id),
                "model_id": model_id,
                "application_id": application_id,
            }
        ).generate_prompt(instance=request.data)


class SystemResourceApplicationPlayDemoTextView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Play demo text for system resource application'),
        summary=_('Play demo text for system resource application'),
        operation_id=_('Play demo text for system resource application'),  # type: ignore
        parameters=[
            OpenApiParameter(
                name='application_id',
                description=_('Application ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ],
        request=PlayDemoTextAPI.get_request(),
        responses=PlayDemoTextAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN)
    @log(
        menu='Application',
        operate='Trial listening for system resource application',
        get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
    )
    def post(self, request: Request, application_id: str):
        byte_data = ApplicationOperateSerializer(
            data={
                'application_id': application_id,
                'workspace_id': _get_application_workspace_id(application_id),
                'user_id': request.user.id,
            }
        ).play_demo_text(request.data)
        return HttpResponse(
            byte_data,
            status=200,
            headers={
                'Content-Type': 'audio/mp3',
                'Content-Disposition': 'attachment; filename="abc.mp3"',
            },
        )


class SystemResourceApplicationTextToSpeechView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Text to speech for system resource application'),
        summary=_('Text to speech for system resource application'),
        operation_id=_('Text to speech for system resource application'),  # type: ignore
        parameters=[
            OpenApiParameter(
                name='application_id',
                description=_('Application ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ],
        request=TextToSpeechAPI.get_request(),
        responses=TextToSpeechAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN)
    @log(
        menu='Application',
        operate='Text to speech for system resource application',
        get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
    )
    def post(self, request: Request, application_id: str):
        byte_data = ApplicationOperateSerializer(
            data={
                'application_id': application_id,
                'workspace_id': _get_application_workspace_id(application_id),
                'user_id': request.user.id,
            }
        ).text_to_speech(request.data)
        return HttpResponse(
            byte_data,
            status=200,
            headers={
                'Content-Type': 'audio/mp3',
                'Content-Disposition': 'attachment; filename="abc.mp3"',
            },
        )


class SystemResourceApplicationSpeechToTextView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Speech to text for system resource application'),
        summary=_('Speech to text for system resource application'),
        operation_id=_('Speech to text for system resource application'),  # type: ignore
        parameters=[
            OpenApiParameter(
                name='application_id',
                description=_('Application ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ],
        request=SpeechToTextAPI.get_request(),
        responses=SpeechToTextAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN)
    @log(
        menu='Application',
        operate='Speech to text for system resource application',
        get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
    )
    def post(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={
                    'application_id': application_id,
                    'workspace_id': _get_application_workspace_id(application_id),
                    'user_id': request.user.id,
                }
            ).speech_to_text({'file': request.FILES.get('file')})
        )


class SystemResourceApplicationMcpToolsView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Get MCP tools for system resource application'),
        summary=_('Get MCP tools for system resource application'),
        operation_id=_('Get MCP tools for system resource application'),  # type: ignore
        parameters=[
            OpenApiParameter(
                name='application_id',
                description=_('Application ID'),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ],
        request=McpServersSerializer,
        responses=None,
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN)
    def post(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={
                    'application_id': application_id,
                    'workspace_id': _get_application_workspace_id(application_id),
                    'user_id': request.user.id,
                }
            ).get_mcp_servers(request.data)
        )


class SystemResourceApplicationVersionView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Get system resource application version list'),
        summary=_('Get system resource application version list'),
        operation_id=_('Get system resource application version list'),  # type: ignore
        parameters=[
            OpenApiParameter(name='application_id', description=_('Application ID'), type=OpenApiTypes.STR, location='path', required=True),
            OpenApiParameter(name='name', description=_('Version Name'), type=OpenApiTypes.STR, required=False),
        ],
        responses=None,
        tags=[_('Application/Version')]  # type: ignore
    )
    @has_permissions(PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN)
    def get(self, request: Request, application_id: str):
        workspace_id = _get_application_workspace_id(application_id)
        return result.success(
            ApplicationVersionSerializer.Query(
                data={'workspace_id': workspace_id}
            ).list({'name': request.query_params.get('name'), 'application_id': application_id})
        )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system resource application version detail'),
            summary=_('Get system resource application version detail'),
            operation_id=_('Get system resource application version detail'),  # type: ignore
            parameters=[
                OpenApiParameter(name='application_id', description=_('Application ID'), type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='application_version_id', description=_('Application Version ID'), type=OpenApiTypes.STR, location='path', required=True),
            ],
            responses=None,
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_APPLICATION_READ, RoleConstants.ADMIN)
        def get(self, request: Request, application_id: str, application_version_id: str):
            workspace_id = _get_application_workspace_id(application_id)
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={
                        'workspace_id': workspace_id,
                        'application_id': application_id,
                        'application_version_id': application_version_id,
                        'user_id': request.user,
                    }
                ).one()
            )

        @extend_schema(
            methods=['PUT'],
            description=_('Modify system resource application version'),
            summary=_('Modify system resource application version'),
            operation_id=_('Modify system resource application version'),  # type: ignore
            parameters=[
                OpenApiParameter(name='application_id', description=_('Application ID'), type=OpenApiTypes.STR, location='path', required=True),
                OpenApiParameter(name='application_version_id', description=_('Application Version ID'), type=OpenApiTypes.STR, location='path', required=True),
            ],
            request=None,
            responses=None,
            tags=[_('Application/Version')]  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN)
        @log(
            menu='Application',
            operate='Modify system resource application version information',
            get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
        )
        def put(self, request: Request, application_id: str, application_version_id: str):
            workspace_id = _get_application_workspace_id(application_id)
            return result.success(
                ApplicationVersionSerializer.Operate(
                    data={
                        'workspace_id': workspace_id,
                        'application_id': application_id,
                        'application_version_id': application_version_id,
                        'user_id': request.user.id,
                    }
                ).edit(request.data)
            )


class SystemResourceApplicationKeyView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['POST'],
        description=_('Create system resource application ApiKey'),
        summary=_('Create system resource application ApiKey'),
        operation_id=_('Create system resource application ApiKey'),  # type: ignore
        parameters=SystemResourceApplicationKeyAPI.get_parameters(),
        request=None,
        responses=SystemResourceApplicationKeyAPI.get_response(),
        tags=[_('Application Api Key')]  # type: ignore
    )
    @log(
        menu='Application', operate='Add system resource ApiKey',
        get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_API_KEY, RoleConstants.ADMIN
    )
    def post(self, request: Request, application_id: str):
        return result.success(
            ApplicationKeySerializer(data={'application_id': application_id}).generate()
        )

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system resource application ApiKey list'),
            summary=_('Get system resource application ApiKey list'),
            operation_id=_('Get system resource application ApiKey list'),  # type: ignore
            parameters=SystemResourceApplicationKeyAPI.List.get_parameters(),
            responses=SystemResourceApplicationKeyAPI.List.get_response(),
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_API_KEY, RoleConstants.ADMIN
        )
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(
                ApplicationKeySerializer(
                    data={
                        'application_id': application_id,
                        'order_by': request.query_params.get('order_by'),
                    }
                ).page(current_page, page_size)
            )

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            description=_('Modify system resource application API_KEY'),
            summary=_('Modify system resource application API_KEY'),
            operation_id=_('Modify system resource application API_KEY'),  # type: ignore
            parameters=SystemResourceApplicationKeyAPI.Operate.get_parameters(),
            request=SystemResourceApplicationKeyAPI.Operate.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_API_KEY, RoleConstants.ADMIN
        )
        @log(
            menu='Application', operate='Modify system resource application API_KEY',
            get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
        )
        def put(self, request: Request, application_id: str, api_key_id: str):
            return result.success(
                ApplicationKeySerializer.Operate(
                    data={'application_id': application_id, 'api_key_id': api_key_id}
                ).edit(request.data)
            )

        @extend_schema(
            methods=['DELETE'],
            description=_('Delete system resource application API_KEY'),
            summary=_('Delete system resource application API_KEY'),
            operation_id=_('Delete system resource application API_KEY'),  # type: ignore
            parameters=SystemResourceApplicationKeyAPI.Operate.get_parameters(),
            request=SystemResourceApplicationKeyAPI.Operate.get_request(),
            responses=result.DefaultResultSerializer,
            tags=[_('Application Api Key')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_API_KEY, RoleConstants.ADMIN
        )
        @log(
            menu='Application', operate='Delete system resource application API_KEY',
            get_operation_object=lambda r, k: _get_application_operation_object(k.get('application_id')),
        )
        def delete(self, request: Request, application_id: str, api_key_id: str):
            return result.success(
                ApplicationKeySerializer.Operate(
                    data={'application_id': application_id, 'api_key_id': api_key_id}
                ).delete()
            )


class SystemResourceApplicationExportView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Export system resource application"),
        summary=_("Export system resource application"),
        operation_id=_("Export system resource application"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Export system resource application",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_EXPORT, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return ApplicationOperateSerializer(
            data={"application_id": application_id, "user_id": request.user.id}
        ).export()


class SystemResourceApplicationOperateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["PUT"],
        description=_("Modify system resource application"),
        summary=_("Modify system resource application"),
        operation_id=_("Modify system resource application"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        responses=result.DefaultResultSerializer,
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Modify system resource application",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN
    )
    def put(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={
                    "application_id": application_id,
                    "user_id": request.user.id,
                    "workspace_id": _get_application_workspace_id(application_id),
                }
            ).edit(request.data)
        )

    @extend_schema(
        methods=["GET"],
        description=_("Get system resource application details"),
        summary=_("Get system resource application details"),
        operation_id=_("Get system resource application details"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        responses=result.DefaultResultSerializer,
        tags=[_("Application")],  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={
                    "application_id": application_id,
                    "user_id": request.user.id,
                    "workspace_id": _get_application_workspace_id(application_id),
                }
            ).one()
        )

    @extend_schema(
        methods=["DELETE"],
        description=_("Delete system resource application"),
        summary=_("Delete system resource application"),
        operation_id=_("Delete system resource application"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Delete system resource application",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_DELETE, RoleConstants.ADMIN
    )
    def delete(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={"application_id": application_id, "user_id": request.user.id}
            ).delete(with_valid=True)
        )


class SystemResourceApplicationPublishView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["PUT"],
        description=_("Publish system resource application"),
        summary=_("Publish system resource application"),
        operation_id=_("Publish system resource application"),  # type: ignore
        parameters=[
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ],
        responses=result.DefaultResultSerializer,
        tags=[_("Application")],  # type: ignore
    )
    @log(
        menu="Application",
        operate="Publish system resource application",
        get_operation_object=lambda r, k: _get_application_operation_object(
            k.get("application_id")
        ),
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_EDIT, RoleConstants.ADMIN
    )
    def put(self, request: Request, application_id: str):
        return result.success(
            ApplicationOperateSerializer(
                data={
                    "application_id": application_id,
                    "user_id": request.user.id,
                    "workspace_id": _get_application_workspace_id(application_id),
                }
            ).publish(request.data)
        )


class SystemResourceApplicationStatsView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('System resource dialogue-related statistical trends'),
        summary=_('System resource dialogue-related statistical trends'),
        operation_id=_('System resource dialogue-related statistical trends'),  # type: ignore
        parameters=ApplicationStatsAPI.get_parameters(),
        responses=ApplicationStatsAPI.get_response(),
        tags=[_('Application')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
    )
    def get(self, request: Request, application_id: str):
        return result.success(
            ApplicationStatisticsSerializer(data={
                'application_id': application_id,
                'workspace_id': _get_application_workspace_id(application_id),
                'start_time': request.query_params.get('start_time'),
                'end_time': request.query_params.get('end_time'),
            }).get_chat_record_aggregate_trend())

    class TokenUsageStatistics(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('System resource application token usage statistics'),
            summary=_('System resource application token usage statistics'),
            operation_id=_('System resource application token usage statistics'),  # type: ignore
            parameters=ApplicationStatsAPI.get_parameters(),
            responses=ApplicationStatsAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
        )
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={
                    'application_id': application_id,
                    'workspace_id': _get_application_workspace_id(application_id),
                    'start_time': request.query_params.get('start_time'),
                    'end_time': request.query_params.get('end_time'),
                }).get_token_usage_statistics())

    class TopQuestionsStatistics(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('System resource application top question statistics'),
            summary=_('System resource application top question statistics'),
            operation_id=_('System resource application top question statistics'),  # type: ignore
            parameters=ApplicationStatsAPI.get_parameters(),
            responses=ApplicationStatsAPI.get_response(),
            tags=[_('Application')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.RESOURCE_APPLICATION_OVERVIEW_READ, RoleConstants.ADMIN
        )
        def get(self, request: Request, application_id: str):
            return result.success(
                ApplicationStatisticsSerializer(data={
                    'application_id': application_id,
                    'workspace_id': _get_application_workspace_id(application_id),
                    'start_time': request.query_params.get('start_time'),
                    'end_time': request.query_params.get('end_time'),
                }).get_top_questions_statistics())
