import json
from unittest.mock import Mock, patch

import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from users.models import User
from users.views.dingtalk_login import DingtalkLoginView


class DingtalkLoginViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="dingtalk@example.com",
            phone="",
            nick_name="dingtalk-nick",
            username="dingtalk-user",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.USER.name,
            source="DINGTALK",
            is_active=True,
        )
        SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                "dingtalk": {
                    "config": {
                        "corp_id": "corp-id",
                        "app_key": "app-key",
                        "app_secret": "app-secret",
                    },
                    "is_valid": True,
                    "is_active": True,
                    "state": "enabled",
                    "failure_reason": "",
                }
            },
        )

    @patch("common.platform.dingtalk_client.requests.post")
    @patch("common.platform.dingtalk_client.requests.get")
    def test_dingtalk_login_returns_system_token_for_existing_username(
        self, mock_get, mock_post
    ):
        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {
            "errcode": 0,
            "errmsg": "ok",
            "access_token": "access-token",
            "expires_in": 7200,
        }
        userinfo_response = Mock()
        userinfo_response.raise_for_status.return_value = None
        userinfo_response.json.return_value = {
            "errcode": 0,
            "errmsg": "ok",
            "result": {
                "userid": self.user.username,
            },
        }
        mock_get.return_value = token_response
        mock_post.return_value = userinfo_response

        request = self.factory.get("/dingtalk", data={"code": "dingtalk-code"})
        response = DingtalkLoginView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        token = payload["data"]["token"]
        details = signing.loads(token)
        self.assertEqual(details["id"], str(self.user.id))
        self.assertEqual(details["type"], "SYSTEM_USER")
        version, get_key = Cache_Version.TOKEN.value
        self.assertEqual(cache.get(get_key(token), version=version).id, self.user.id)

    def test_dingtalk_login_rejects_disabled_provider(self):
        setting = SystemSetting.objects.get(type=SettingType.PLATFORM_SOURCE)
        setting.meta["dingtalk"]["is_active"] = False
        setting.save()

        request = self.factory.get("/dingtalk", data={"code": "dingtalk-code"})
        response = DingtalkLoginView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)
