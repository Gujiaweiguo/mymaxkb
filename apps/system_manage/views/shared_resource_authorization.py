from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import RoleConstants
from common.log.log import log
from common.result import result
from system_manage.api.shared_resource_authorization import (
    SharedResourceAuthorizationAPI,
)
from system_manage.serializers.shared_resource_authorization import (
    SharedResourceAuthorizationSerializer,
)


class SharedResourceAuthorizationView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get shared resource authorization"),
        description=_("Get shared resource authorization"),
        operation_id=_("Get shared resource authorization"),  # type: ignore
        parameters=SharedResourceAuthorizationAPI.get_parameters(),
        responses=SharedResourceAuthorizationAPI.get_response(),
        tags=[_("Shared Resource Authorization")],  # type: ignore
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, resource_type: str, resource_id: str):
        return result.success(
            SharedResourceAuthorizationSerializer.one(
                resource_type.upper(), resource_id
            )
        )

    @extend_schema(
        methods=["POST"],
        summary=_("Create or update shared resource authorization"),
        description=_("Create or update shared resource authorization"),
        operation_id=_("Create or update shared resource authorization"),  # type: ignore
        parameters=SharedResourceAuthorizationAPI.get_parameters(),
        request=SharedResourceAuthorizationAPI.get_request(),
        responses=SharedResourceAuthorizationAPI.get_response(),
        tags=[_("Shared Resource Authorization")],  # type: ignore
    )
    @log(
        menu="Shared Resource Authorization",
        operate="Create or update shared resource authorization",
    )
    @has_permissions(RoleConstants.ADMIN)
    def post(self, request: Request, resource_type: str, resource_id: str):
        serializer = SharedResourceAuthorizationSerializer.Operate(data=request.data)
        serializer.is_valid(raise_exception=True)
        return result.success(
            serializer.save(
                resource_type=resource_type.upper(), resource_id=resource_id
            )
        )
