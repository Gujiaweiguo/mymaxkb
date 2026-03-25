import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.utils.common import password_encrypt
from users.models import User


class ApplicationAPIIntegrationTests(TestCase):
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
        self.folder = ApplicationFolder.objects.create(
            id="test-folder",
            name="Test Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_create_application(self):
        response = self.client.post(
            "/api/application/application",
            {
                "name": "Test App",
                "desc": "Test Description",
                "folder_id": str(self.folder.id),
                "type": ApplicationTypeChoices.SIMPLE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_application_list(self):
        Application.objects.create(
            id=uuid.uuid7(),
            name="List App",
            desc="List Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.get("/api/application/application")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_application_detail(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Detail App",
            desc="Detail Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.get(
            f"/api/application/application/{app.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["name"], "Detail App")

    def test_update_application(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Update App",
            desc="Update Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.put(
            f"/api/application/application/{app.id}",
            {"name": "Updated App Name"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_application(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Delete App",
            desc="Delete Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.delete(
            f"/api/application/application/{app.id}"
        )

        self.assertEqual(response.status_code, 200)


class ApplicationFolderIntegrationTests(TestCase):
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

    def test_create_folder(self):
        response = self.client.post(
            "/api/application/folder",
            {"name": "New Folder", "workspace_id": "default"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_folder_list(self):
        response = self.client.get("/api/application/folder")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_delete_folder(self):
        folder = ApplicationFolder.objects.create(
            id="delete-folder",
            name="Delete Folder",
            user=self.admin_user,
            workspace_id="default",
        )

        response = self.client.delete(
            f"/api/application/folder/{folder.id}"
        )

        self.assertEqual(response.status_code, 200)
