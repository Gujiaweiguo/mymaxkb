import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from users.models import User
from system_manage.models import SystemSetting, SettingType, Workspace


ADMIN_API_PREFIX = "/admin/api"


class SystemSettingsAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="system-settings-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_get_email_setting(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/email_setting")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_update_email_setting(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/email_setting",
            {
                "host": "smtp.example.com",
                "port": 587,
                "username": "test@example.com",
                "password": "password",
                "use_ssl": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_get_auth_setting(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/auth/setting")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_update_auth_setting(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/auth/setting",
            {
                "default_value": "LOCAL",
                "login_methods": ["LOCAL"],
                "max_attempts": 3,
                "lock_time": 15,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)


class ChatUserAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="chat-user-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_get_chat_user_list(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/system/chat_user/list")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_chat_user_page(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/chat_user/user_manage/1/20"
        )

        self.assertEqual(response.status_code, 200)

    def test_get_chat_user_sync_types(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/system/chat_user/sync_types")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)


class SystemAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="system-api-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_get_system_info(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/profile")

        self.assertEqual(response.status_code, 200)

    def test_get_system_logo(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/display/info")

        self.assertEqual(response.status_code, 200)

    def test_get_theme_setting(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/display/info")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_update_theme_setting(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/display/update",
            {"theme_color": "#1890FF", "logo": "/logo.png"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
