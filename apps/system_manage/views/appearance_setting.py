from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from system_manage.api.appearance_setting import AppearanceSettingAPI
from system_manage.serializers.appearance_setting import AppearanceSettingSerializer


class AppearanceSettingView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        methods=["GET"],
        description=_("Get appearance settings"),
        operation_id="get_appearance_settings",
        responses=AppearanceSettingAPI.get_response(),
        tags=["Appearance Settings"],
    )
    def get(self, request: Request):
        return result.success(AppearanceSettingSerializer.one())


class AppearanceSettingOperateView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        methods=["PUT"],
        description=_("Update appearance settings"),
        operation_id="update_appearance_settings",
        request=None,
        responses=AppearanceSettingAPI.get_response(),
        tags=["Appearance Settings"],
    )
    @has_permissions(PermissionConstants.APPEARANCE_SETTINGS_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(
            AppearanceSettingSerializer.Update(data=request.data).update_or_save()
        )
