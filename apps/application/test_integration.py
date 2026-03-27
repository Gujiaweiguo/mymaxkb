import json
import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.utils.common import password_encrypt
from maxkb.const import CONFIG
from users.models import User


def set_system_user_auth(client: APIClient, user: User):
    token = signing.dumps(
        {
            "username": user.username,
            "id": str(user.id),
            "email": user.email,
            "type": AuthenticationType.SYSTEM_USER.value,
        }
    )
    version, get_key = Cache_Version.TOKEN.value
    cache.set(get_key(token), user, timeout=CONFIG.get_session_timeout(), version=version)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class ApplicationAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="app-test-admin@example.com",
            phone="",
            nick_name="App Test Admin",
            username="app-test-admin",
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
        set_system_user_auth(self.client, self.admin_user)

    def test_create_application(self):
        response = self.client.post(
            "/admin/api/workspace/default/application",
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

        response = self.client.get("/admin/api/workspace/default/application")

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
            f"/admin/api/workspace/default/application/{app.id}"
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
            f"/admin/api/workspace/default/application/{app.id}",
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
            f"/admin/api/workspace/default/application/{app.id}"
        )

        self.assertEqual(response.status_code, 200)


class ApplicationFolderIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="folder-test-admin@example.com",
            phone="",
            nick_name="Folder Test Admin",
            username="folder-test-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        set_system_user_auth(self.client, self.admin_user)

    def test_create_folder(self):
        response = self.client.post(
            "/admin/api/workspace/default/APPLICATION/folder",
            {"name": "New Folder", "workspace_id": "default"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_folder_list(self):
        response = self.client.get("/admin/api/workspace/default/APPLICATION/folder")

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
            f"/admin/api/workspace/default/APPLICATION/folder/{folder.id}"
        )

        self.assertEqual(response.status_code, 200)
