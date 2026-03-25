import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.utils.common import password_encrypt
from users.models import User


class UserAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="admin",
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
            "/api/user/user/login",
            {"username": "admin", "password": "Admin123!", "login_type": "LOCAL"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("token", data.get("data", {}))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            "/api/user/user/login",
            {"username": "admin", "password": "WrongPassword", "login_type": "LOCAL"},
            format="json",
        )

        self.assertNotEqual(response.status_code, 200)

    def test_login_with_missing_fields(self):
        response = self.client.post(
            "/api/user/user/login",
            {"username": "admin"},
            format="json",
        )

        self.assertNotEqual(response.status_code, 200)

    def test_get_user_list_requires_auth(self):
        response = self.client.get("/api/user/user_manage")

        self.assertNotEqual(response.status_code, 200)

    def test_get_user_list_with_auth(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get("/api/user/user_manage")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.regular_user, token="test-token")
        response = self.client.get("/api/user/user/profile")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["username"], "testuser")

    def test_user_manage_page(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get("/api/user/user_manage/1/20")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)


class UserManageCRUDIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_create_user(self):
        response = self.client.post(
            "/api/user/user_manage",
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
            f"/api/user/user_manage/{self.admin_user.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["username"], "admin")

    def test_update_user(self):
        response = self.client.put(
            f"/api/user/user_manage/{self.admin_user.id}",
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
            f"/api/user/user_manage/{test_user.id}"
        )

        self.assertEqual(response.status_code, 200)
