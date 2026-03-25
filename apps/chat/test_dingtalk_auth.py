import json
from unittest.mock import Mock, patch

import uuid_utils.compat as uuid
from django.core import signing
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationTypeChoices,
)
from chat.views.dingtalk_auth import DingtalkAuthentication
from common.auth.authenticate import ChatTokenAuth
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import ChatUser, SettingType, SystemSetting, Workspace
from users.models import User


class DingtalkChatAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = User.objects.create(
            id=uuid.uuid7(),
            email="owner@example.com",
            phone="",
            nick_name="owner-nick",
            username="owner-user",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.USER.name,
            source="LOCAL",
            is_active=True,
        )
        self.chat_user = ChatUser.objects.create(
            id=uuid.uuid7(),
            email="chat-dingtalk@example.com",
            phone="",
            nick_name="chat-dingtalk-nick",
            username="chat-dingtalk-user",
            password=password_encrypt("Secret1!"),
            source="DINGTALK",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-dingtalk-auth", name="workspace-dingtalk-auth"
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-dingtalk-auth",
            name="folder-dingtalk-auth",
            workspace_id=self.workspace.id,
            user=self.owner,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="DingTalk App",
            desc="desc",
            user=self.owner,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.access = ApplicationAccessToken.objects.create(
            application=self.application,
            access_token="chat-access-token",
            is_active=True,
            authentication=True,
            authentication_value={"type": "dingtalk"},
        )
        SystemSetting.objects.create(
            type=SettingType.CHAT_USER_PLATFORM_SOURCE,
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
    def test_dingtalk_chat_auth_returns_token_usable_by_chat_auth(
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
                "userid": self.chat_user.username,
            },
        }
        mock_get.return_value = token_response
        mock_post.return_value = userinfo_response

        request = self.factory.get(
            "/chat/auth/dingtalk",
            data={"code": "dingtalk-code", "accessToken": self.access.access_token},
        )
        response = DingtalkAuthentication.as_view()(request)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        token = payload["data"]["token"]
        details = signing.loads(token)
        self.assertEqual(details["type"], "CHAT_USER")
        self.assertEqual(details["chat_user_id"], str(self.chat_user.id))

        profile_request = self.factory.get("/chat/application/profile")
        profile_request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        auth_result = ChatTokenAuth().authenticate(profile_request)
        self.assertIsNotNone(auth_result)

    def test_dingtalk_chat_auth_rejects_invalid_access_token(self):
        request = self.factory.get(
            "/chat/auth/dingtalk",
            data={"code": "dingtalk-code", "accessToken": "bad-token"},
        )
        response = DingtalkAuthentication.as_view()(request)

        self.assertEqual(response.status_code, 404)
