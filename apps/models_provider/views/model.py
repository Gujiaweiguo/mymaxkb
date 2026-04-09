# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from models_provider.api.model import (
    ModelCreateAPI,
    GetModelApi,
    ModelEditApi,
    ModelListResponse,
    DefaultModelResponse,
    SystemResourceModelQueryAPI,
)
from models_provider.api.provide import ProvideApi
from models_provider.models import Model
from models_provider.serializers.model_serializer import ModelSerializer, \
    WorkspaceSharedModelSerializer, SystemResourceModelQuerySerializer
from system_manage.views import encryption_str


def encryption_credential(credential):
    if isinstance(credential, dict):
        return {key: encryption_str(credential.get(key)) for key in credential}
    return credential


def get_edit_model_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    credential = body.get('credential', {})
    credential_encryption_ed = encryption_credential(credential)
    return {
        'path': path,
        'body': {**body, 'credential': credential_encryption_ed},
        'query': query
    }


def get_model_operation_object(model_id):
    model_model = QuerySet(model=Model).filter(id=model_id).first()
    if model_model is not None:
        return {
            "name": model_model.name
        }
    return {}


class ModelSetting(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Create model"),
                   description=_("Create model"),
                   operation_id=_("Create model"),  # type: ignore
                   tags=[_("Model")],  # type: ignore
                   parameters=ModelCreateAPI.get_parameters(),
                   request=ModelCreateAPI.get_request(),
                   responses=ModelCreateAPI.get_response())
    @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_permission(),
                     PermissionConstants.MODEL_EDIT.get_workspace_permission_workspace_manage_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role())
    @log(menu='model', operate='Create model',
         get_operation_object=lambda r, k: {'name': r.date.get('name')},
         get_details=get_edit_model_details,
         )
    def post(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Create(
                data={**request.data, 'user_id': request.user.id, 'workspace_id': workspace_id}).insert(workspace_id,
                                                                                                        with_valid=True))

    # @extend_schema(methods=['PUT'],
    #                summary=_('Update model'),
    #                operation_id=_('Update model'),  # type: ignore
    #                request=ModelEditApi.get_request(),
    #                responses=ModelCreateApi.get_response(),
    #                tags=[_('Model')])  # type: ignore
    # @has_permissions(PermissionConstants.MODEL_CREATE)
    # def put(self, request: Request):
    #     return result.success(
    #         ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
    #                                                                                               with_valid=True))

    @extend_schema(methods=['GET'],
                   summary=_('Query model list'),
                   description=_('Query model list'),
                   operation_id=_('Query model list'),  # type: ignore
                   parameters=ModelListResponse.get_parameters(),
                   responses=ModelListResponse.get_response(),
                   tags=[_('Model')])  # type: ignore
    @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission(),
                     PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role())
    def get(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': str(request.user.id)}).list(
                workspace_id=workspace_id,
                with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_('Update model'),
                       description=_('Update model'),
                       operation_id=_('Update model'),  # type: ignore
                       request=ModelEditApi.get_request(),
                       parameters=GetModelApi.get_parameters(),
                       responses=ModelEditApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_EDIT.get_workspace_model_permission(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         PermissionConstants.MODEL_EDIT.get_workspace_permission_workspace_manage_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        @log(menu='model', operate='Update model',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
             get_details=get_edit_model_details,
             )
        def put(self, request: Request, workspace_id, model_id: str):
            return result.success(
                ModelSerializer.Operate(
                    data={'id': model_id, 'user_id': request.user.id, 'workspace_id': workspace_id}).edit(request.data,
                                                                                                          str(request.user.id)))

        @extend_schema(methods=['DELETE'],
                       summary=_('Delete model'),
                       description=_('Delete model'),
                       operation_id=_('Delete model'),  # type: ignore
                       parameters=GetModelApi.get_parameters(),
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_DELETE.get_workspace_model_permission(),
                         PermissionConstants.MODEL_DELETE.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        @log(menu='model', operate='Delete model',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
             )
        def delete(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(
                    data={'id': model_id, 'user_id': request.user.id, 'workspace_id': workspace_id}).delete())

        @extend_schema(methods=['GET'],
                       summary=_('Query model details'),
                       description=_('Query model details'),
                       operation_id=_('Query model details'),  # type: ignore
                       parameters=GetModelApi.get_parameters(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_model_permission(),
                         PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(
                    data={'id': model_id, 'user_id': request.user.id, 'workspace_id': workspace_id}).one(
                    with_valid=True))

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_('Get model parameter form'),
                       description=_('Get model parameter form'),
                       operation_id=_('Get model parameter form'),  # type: ignore
                       parameters=GetModelApi.get_parameters(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_model_permission(),
                         PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                         PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
                         PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
                         PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                         PermissionConstants.MODEL_READ.get_workspace_permission(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         RoleConstants.USER.get_workspace_role(),)
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).get_model_params())

        @extend_schema(methods=['PUT'],
                       summary=_('Save model parameter form'),
                       description=_('Save model parameter form'),
                       operation_id=_('Save model parameter form'),  # type: ignore
                       parameters=GetModelApi.get_parameters(),
                       request=GetModelApi.get_request(),
                       responses=ProvideApi.ModelParamsForm.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_EDIT.get_workspace_model_permission(),
                         PermissionConstants.MODEL_EDIT.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         PermissionConstants.MODEL_READ.get_workspace_permission(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        @log(menu='model', operate='Save model parameter form',
             get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
             )
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).save_model_params_form(request.data))

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       description=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       operation_id=_(
                           'Query model meta information, this interface does not carry authentication information'),
                       parameters=GetModelApi.get_parameters(),
                       responses=GetModelApi.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_READ.get_workspace_model_permission(),
                         PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         PermissionConstants.MODEL_READ.get_workspace_permission(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        def get(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'workspace_id': workspace_id}).one_meta(with_valid=True))

    class PauseDownload(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_('Pause model download'),
                       description=_('Pause model download'),
                       operation_id=_('Pause model download'),  # type: ignore
                       parameters=GetModelApi.get_parameters(),
                       request=GetModelApi.get_request(),
                       responses=DefaultModelResponse.get_response(),
                       tags=[_('Model')])  # type: ignore
        @has_permissions(PermissionConstants.MODEL_CREATE.get_workspace_model_permission(),
                         PermissionConstants.MODEL_CREATE.get_workspace_permission_workspace_manage_role(),
                         RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
                         ViewPermission([RoleConstants.USER.get_workspace_role()],
                                        [PermissionConstants.MODEL.get_workspace_model_permission()],
                                        CompareConstants.AND), )
        def put(self, request: Request, workspace_id: str, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'workspace_id': workspace_id}).pause_download())


class WorkspaceSharedModelSetting(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['Get'],
        summary=_('Get Share model by workspace id'),
        description=_('Get Share model by workspace id'),
        operation_id=_('Get Share model by workspace id'),  # type: ignore
        parameters=ModelListResponse.get_parameters(),
        responses=DefaultModelResponse.get_response(),
        tags=[_('Shared Model')]
    )  # type: ignore
    @has_permissions(
        PermissionConstants.MODEL_READ.get_workspace_permission(),
        PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        RoleConstants.USER.get_workspace_role(),
    )
    def get(self, request: Request, workspace_id: str):
        return result.success(
            WorkspaceSharedModelSerializer(data={**query_params_to_single_dict(request.query_params),
                                                 'workspace_id': workspace_id}).get_share_model_list())


class SystemSharedModelSetting(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['Get'],
        summary=_('Get shared model list for system management'),
        description=_('Get shared model list for system management'),
        operation_id=_('Get shared model list for system management'),  # type: ignore
        parameters=ModelListResponse.get_parameters(),
        responses=DefaultModelResponse.get_response(),
        tags=[_('Shared Model')]
    )  # type: ignore
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(
            WorkspaceSharedModelSerializer(
                data={**query_params_to_single_dict(request.query_params), 'workspace_id': ''}
            ).get_share_model_list()
        )


class SystemResourceModelView(APIView):
    authentication_classes = [TokenAuth]

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            description=_('Get system model resource list by page'),
            summary=_('Get system model resource list by page'),
            operation_id=_('Get system model resource list by page'),  # type: ignore
            parameters=SystemResourceModelQueryAPI.get_parameters(),
            responses=SystemResourceModelQueryAPI.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, current_page: int, page_size: int):
            serializer = SystemResourceModelQuerySerializer(data=request.query_params)
            return result.success(serializer.page(current_page, page_size))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Query system model details'),
            description=_('Query system model details'),
            operation_id=_('Query system model details'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            responses=GetModelApi.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, model_id: str):
            return result.success(ModelSerializer.Operate(data={'id': model_id}).one(with_valid=True))

        @extend_schema(
            methods=['PUT'],
            summary=_('Update system model'),
            description=_('Update system model'),
            operation_id=_('Update system model'),  # type: ignore
            request=ModelEditApi.get_request(),
            parameters=GetModelApi.get_query_params_api()[1:],
            responses=ModelEditApi.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_EDIT, RoleConstants.ADMIN)
        @log(
            menu='model', operate='Update system model',
            get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
            get_details=get_edit_model_details,
        )
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).edit(request.data, str(request.user.id))
            )

        @extend_schema(
            methods=['DELETE'],
            summary=_('Delete system model'),
            description=_('Delete system model'),
            operation_id=_('Delete system model'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            responses=DefaultModelResponse.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_DELETE, RoleConstants.ADMIN)
        @log(
            menu='model', operate='Delete system model',
            get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
        )
        def delete(self, request: Request, model_id: str):
            return result.success(ModelSerializer.Operate(data={'id': model_id}).delete())

    class ModelParamsForm(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Get system model parameter form'),
            description=_('Get system model parameter form'),
            operation_id=_('Get system model parameter form'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            responses=ProvideApi.ModelParamsForm.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, model_id: str):
            return result.success(ModelSerializer.ModelParams(data={'id': model_id}).get_model_params())

        @extend_schema(
            methods=['PUT'],
            summary=_('Save system model parameter form'),
            description=_('Save system model parameter form'),
            operation_id=_('Save system model parameter form'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            request=GetModelApi.get_request(),
            responses=ProvideApi.ModelParamsForm.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_EDIT, RoleConstants.ADMIN)
        @log(
            menu='model', operate='Save system model parameter form',
            get_operation_object=lambda r, k: get_model_operation_object(k.get('model_id')),
        )
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.ModelParams(data={'id': model_id}).save_model_params_form(request.data)
            )

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['GET'],
            summary=_('Query system model meta information'),
            description=_('Query system model meta information'),
            operation_id=_('Query system model meta information'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            responses=GetModelApi.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_READ, RoleConstants.ADMIN)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).one_meta(with_valid=True)
            )

    class PauseDownload(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['PUT'],
            summary=_('Pause system model download'),
            description=_('Pause system model download'),
            operation_id=_('Pause system model download'),  # type: ignore
            parameters=GetModelApi.get_query_params_api()[1:],
            request=GetModelApi.get_request(),
            responses=DefaultModelResponse.get_response(),
            tags=[_('Model')],  # type: ignore
        )
        @has_permissions(PermissionConstants.RESOURCE_MODEL_EDIT, RoleConstants.ADMIN)
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id}).pause_download()
            )


class ModelList(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_('Query all model list'),
                   description=_('Query all model list'),
                   operation_id=_('Query all model list'),  # type: ignore
                   parameters=ModelListResponse.get_parameters(),
                   responses=ModelListResponse.get_response(),
                   tags=[_('Model')])  # type: ignore
    @has_permissions(PermissionConstants.MODEL_READ.get_workspace_permission(),
                     PermissionConstants.KNOWLEDGE_READ.get_workspace_permission(),
                     PermissionConstants.APPLICATION_READ.get_workspace_permission(),
                     PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
                     PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
                     PermissionConstants.APPLICATION_READ.get_workspace_permission_workspace_manage_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role(), RoleConstants.USER.get_workspace_role())
    def get(self, request: Request, workspace_id: str):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': str(request.user.id)}).model_list(
                workspace_id=workspace_id,
                with_valid=True))
