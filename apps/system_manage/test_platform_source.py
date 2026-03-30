import json
from types import SimpleNamespace

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from system_manage.views.platform_source import (
    ChatUserPlatformSourceView,
    PlatformSourceView,
)
from users.models import User


class PlatformSourceTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-platform",
            username="admin-platform",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )

    def test_get_platform_source_returns_three_unconfigured_entries(self):
        request = self.factory.get("/platform/source")
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = PlatformSourceView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["data"]), 3)
        auth_types = {item["auth_type"] for item in payload["data"]}
        self.assertEqual(auth_types, {"wecom", "dingtalk", "lark"})
        for item in payload["data"]:
            self.assertEqual(item["state"], "unconfigured")
            self.assertFalse(item["is_configured"])
            self.assertFalse(item["is_active"])
            self.assertFalse(item["is_valid"])

    def test_system_platform_source_round_trip(self):
        request = self.factory.post(
            "/platform/source",
            data={
                "key": "wecom",
                "config": {
                    "corp_id": "corp",
                    "agent_id": "agent",
                    "app_secret": "secret",
                },
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = PlatformSourceView.as_view()(request)
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["state"], "configured")
        self.assertFalse(payload["data"]["is_valid"])

        validate_request = self.factory.put(
            "/platform/source",
            data={
                "key": "wecom",
                "config": {
                    "corp_id": "corp",
                    "agent_id": "agent",
                    "app_secret": "secret",
                },
            },
            format="json",
        )
        force_authenticate(validate_request, user=self.admin, token=self.auth_token)
        validate_response = PlatformSourceView.as_view()(validate_request)
        validate_payload = json.loads(validate_response.content)
        self.assertTrue(validate_payload["data"]["is_valid"])
        self.assertEqual(validate_payload["data"]["state"], "ready")

        toggle_request = self.factory.post(
            "/platform/source",
            data={
                "key": "wecom",
                "config": {
                    "corp_id": "corp",
                    "agent_id": "agent",
                    "app_secret": "secret",
                },
                "isActive": True,
            },
            format="json",
        )
        force_authenticate(toggle_request, user=self.admin, token=self.auth_token)
        toggle_response = PlatformSourceView.as_view()(toggle_request)
        toggle_payload = json.loads(toggle_response.content)
        self.assertTrue(toggle_payload["data"]["is_active"])
        self.assertEqual(toggle_payload["data"]["state"], "enabled")

    def test_chat_user_platform_source_uses_dedicated_setting_type(self):
        request = self.factory.put(
            "/chat_user/auth/platform/source",
            data={
                "key": "lark",
                "config": {"app_key": "app-key", "app_secret": "app-secret"},
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserPlatformSourceView.as_view()(request)
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["data"]["is_valid"])
        self.assertTrue(
            SystemSetting.objects.filter(
                type=SettingType.CHAT_USER_PLATFORM_SOURCE
            ).exists()
        )

    def test_get_chat_user_platform_source_returns_three_unconfigured_entries(self):
        request = self.factory.get("/chat_user/auth/platform/source")
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = ChatUserPlatformSourceView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["data"]), 3)
        auth_types = {item["auth_type"] for item in payload["data"]}
        self.assertEqual(auth_types, {"wecom", "dingtalk", "lark"})
        for item in payload["data"]:
            self.assertEqual(item["state"], "unconfigured")
            self.assertFalse(item["is_configured"])
            self.assertFalse(item["is_active"])
            self.assertFalse(item["is_valid"])

    def test_chat_user_platform_source_post_persists_configuration(self):
        request = self.factory.post(
            "/chat_user/auth/platform/source",
            data={
                "key": "lark",
                "config": {"app_key": "app-key", "app_secret": "app-secret"},
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = ChatUserPlatformSourceView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["auth_type"], "lark")
        self.assertEqual(payload["data"]["state"], "configured")
        self.assertFalse(payload["data"]["is_active"])
        self.assertFalse(payload["data"]["is_valid"])
        setting = SystemSetting.objects.get(type=SettingType.CHAT_USER_PLATFORM_SOURCE)
        self.assertIn("lark", setting.meta)
        self.assertEqual(
            setting.meta["lark"]["config"],
            {"app_key": "app-key", "app_secret": "app-secret"},
        )
