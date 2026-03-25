# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： login_auth_setting.py
@date：2026/3/22
@desc:
"""

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.login_auth_setting import (
    LoginAuthSettingResponseSerializer,
    LoginAuthSettingSerializer,
)


class LoginAuthSettingResult(ResultSerializer):
    def get_data(self):
        return LoginAuthSettingResponseSerializer()


class LoginAuthSettingAPI(APIMixin):
    @staticmethod
    def get_request():
        return LoginAuthSettingSerializer.Update

    @staticmethod
    def get_response():
        return LoginAuthSettingResult
