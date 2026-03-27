import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.utils.common import password_encrypt
from users.models import User


ADMIN_API_PREFIX = "/admin/api"


class UserAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_username = "users-int-admin"
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username=self.admin_username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="user@example.com",
            phone="",
            nick_name="Regular User",
            username="testuser",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "Admin123!", "login_type": "LOCAL"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("token", data.get("data", {}))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "WrongPassword", "login_type": "LOCAL"},
            format="json",
        )

        data = json.loads(response.content)
        self.assertNotIn("token", data.get("data") or {})

    def test_login_with_missing_fields(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username},
            format="json",
        )

        data = json.loads(response.content)
        self.assertNotIn("token", data.get("data") or {})

    def test_get_user_list_requires_auth(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage")

        self.assertNotEqual(response.status_code, 200)

    def test_get_user_list_with_auth(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.regular_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user/profile")

        self.assertEqual(response.status_code, 200)

    def test_user_manage_page(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage/1/20")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)


class UserManageCRUDIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_username = "users-manage-admin"
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username=self.admin_username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_create_user(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user_manage",
            {
                "username": "newuser",
                "password": "NewUser123!",
                "email": "newuser@example.com",
                "role": "USER",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_user_detail(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/user_manage/{self.admin_user.id}"
        )

        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/user_manage/{self.admin_user.id}",
            {"nick_name": "Updated Admin"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        test_user = User.objects.create(
            id=uuid.uuid7(),
            email="delete@example.com",
            phone="",
            nick_name="Delete User",
            username="deleteuser",
            password=password_encrypt("Delete123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/user_manage/{test_user.id}"
        )

        self.assertEqual(response.status_code, 200)
