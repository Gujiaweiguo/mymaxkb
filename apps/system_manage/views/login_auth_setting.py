# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： login_auth_setting.py
@date：2026/3/22
@desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.log.log import log
from common.result import result
from system_manage.api.login_auth_setting import LoginAuthSettingAPI
from system_manage.serializers.login_auth_setting import LoginAuthSettingSerializer


class LoginAuthSettingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        summary=_("Get login auth settings"),
        description=_("Get login auth settings"),
        operation_id=_("Get login auth settings"),  # type: ignore
        responses=LoginAuthSettingAPI.get_response(),
        tags=[_("Login Auth Settings")],  # type: ignore
    )
    @has_permissions(PermissionConstants.LOGIN_AUTH_READ, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(LoginAuthSettingSerializer.one())

    @extend_schema(
        methods=["PUT"],
        summary=_("Create or update login auth settings"),
        description=_("Create or update login auth settings"),
        operation_id=_("Create or update login auth settings"),  # type: ignore
        request=LoginAuthSettingAPI.get_request(),
        responses=LoginAuthSettingAPI.get_response(),
        tags=[_("Login Auth Settings")],  # type: ignore
    )
    @log(menu="Login Auth Settings", operate="Create or update login auth settings")
    @has_permissions(PermissionConstants.LOGIN_AUTH_EDIT, RoleConstants.ADMIN)
    def put(self, request: Request):
        return result.success(
            LoginAuthSettingSerializer.Update(data=request.data).update_or_save()
        )


class PublicLoginAuthSettingView(APIView):
    @extend_schema(
        methods=["GET"],
        summary=_("Get public login auth settings"),
        description=_("Get public login auth settings"),
        operation_id=_("Get public login auth settings"),  # type: ignore
        responses=LoginAuthSettingAPI.get_response(),
        tags=[_("Login Auth Settings")],  # type: ignore
    )
    def get(self, request: Request):
        return result.success(LoginAuthSettingSerializer.one())
