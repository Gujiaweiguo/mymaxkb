# pyright: reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false, reportImplicitRelativeImport=false, reportUninitializedInstanceVariable=false

import importlib.util
import json
import uuid_utils.compat as uuid
from pathlib import Path

from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_api_key import ApplicationApiKey
from application.serializers.application_api_key import ApplicationKeySerializer
from application.serializers.system_resource_application import (
    SystemResourceApplicationQuerySerializer,
)
from application.test_integration import set_system_user_auth
from common.utils.common import password_encrypt
from system_manage.models import Workspace
from users.models import User


class SystemResourceApplicationQueryTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_workspace(self, workspace_id: str, name: str):
        workspace, _ = Workspace.objects.get_or_create(
            id=workspace_id,
            defaults={"name": name},
        )
        return workspace

    def create_folder(self, folder_id: str, workspace_id: str, user):
        return ApplicationFolder.objects.create(
            id=folder_id,
            name=f"{folder_id}-folder",
            user=user,
            workspace_id=workspace_id,
        )

    def create_application(self, name: str, workspace_id: str, user, folder):
        return Application.objects.create(
            id=uuid.uuid7(),
            name=name,
            desc=f"{name}-desc",
            user=user,
            folder=folder,
            workspace_id=workspace_id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_page_filters_applications_by_workspace_ids(self):
        user = self.create_user("resource-admin")
        self.create_workspace("default", "default")
        self.create_workspace("workspace-a", "workspace-a")
        self.create_workspace("workspace-b", "workspace-b")
        folder_a = self.create_folder("folder-a", "workspace-a", user)
        folder_b = self.create_folder("folder-b", "workspace-b", user)
        app_a = self.create_application("app-a", "workspace-a", user, folder_a)
        self.create_application("app-b", "workspace-b", user, folder_b)

        page = SystemResourceApplicationQuerySerializer(
            data={"workspace_ids": '["workspace-a"]'}
        ).page(1, 20)

        self.assertEqual(page["total"], 1)
        self.assertEqual(page["records"][0]["id"], app_a.id)
        self.assertEqual(page["records"][0]["workspace_id"], "workspace-a")


class ApplicationModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_application_creation(self):
        user = self.create_user("app-creator")
        folder = ApplicationFolder.objects.create(
            id="test-folder",
            name="Test Folder",
            user=user,
            workspace_id="default",
        )
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Test App",
            desc="Test Description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(app.name, "Test App")
        self.assertEqual(app.type, ApplicationTypeChoices.SIMPLE)
        self.assertEqual(app.workspace_id, "default")

    def test_application_str_representation(self):
        user = self.create_user("str-user")
        folder = ApplicationFolder.objects.create(
            id="str-folder",
            name="Str Folder",
            user=user,
            workspace_id="default",
        )
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Str App",
            desc="Desc",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(str(app), "Str App")


class ApplicationFolderModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_folder_creation(self):
        user = self.create_user("folder-user")
        folder = ApplicationFolder.objects.create(
            id="new-folder",
            name="New Folder",
            user=user,
            workspace_id="default",
        )

        self.assertEqual(folder.name, "New Folder")
        self.assertEqual(folder.user, user)

    def test_folder_with_applications(self):
        user = self.create_user("folder-app-user")
        folder = ApplicationFolder.objects.create(
            id="app-folder",
            name="App Folder",
            user=user,
            workspace_id="default",
        )
        Application.objects.create(
            id=uuid.uuid7(),
            name="App 1",
            desc="Desc 1",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        Application.objects.create(
            id=uuid.uuid7(),
            name="App 2",
            desc="Desc 2",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(folder.application_set.count(), 2)


class ApplicationApiKeyMaskingTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_application(self):
        user = self.create_user("app-key-user")
        folder = ApplicationFolder.objects.create(
            id="app-key-folder",
            name="App Key Folder",
            user=user,
            workspace_id="default",
        )
        return Application.objects.create(
            id=uuid.uuid7(),
            name="App Key App",
            desc="App key description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_generate_returns_full_secret_key_once(self):
        application = self.create_application()

        result = ApplicationKeySerializer(data={"application_id": application.id}).generate()

        self.assertTrue(result["secret_key"].startswith("agent-"))
        self.assertNotIn("******", result["secret_key"])
        self.assertEqual(len(result["secret_key"]), len("agent-") + 32)

    def test_page_masks_application_secret_key_after_creation(self):
        application = self.create_application()
        created = ApplicationKeySerializer(data={"application_id": application.id}).generate()

        page = ApplicationKeySerializer(data={"application_id": application.id}).page(1, 20)

        self.assertEqual(page["total"], 1)
        record = page["records"][0]
        self.assertEqual(record["id"], created["id"])
        self.assertNotEqual(record["secret_key"], created["secret_key"])
        self.assertIn("******", record["secret_key"])
        self.assertEqual(record["secret_key"], f"{created['secret_key'][:8]}******{created['secret_key'][-4:]}")

        stored = ApplicationApiKey.objects.get(id=created["id"])
        self.assertEqual(stored.secret_key, created["secret_key"])


class OrchestratorIntegrationConfigTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="orch-int-admin@example.com",
            phone="",
            nick_name="Orch Int Admin",
            username="orch-int-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id="orch-int-folder",
            name="Orch Int Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="Orch Int App",
            desc="Orchestrator integration test app",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
            knowledge_setting={'top_n': 5, 'similarity': 0.7, 'search_mode': 'embedding',
                               'max_paragraph_char_number': 5000,
                               'no_references_setting': {'status': 'ai_questioning', 'value': '{question}'}},
        )
        set_system_user_auth(self.client, self.admin_user)

    def _endpoint_url(self):
        return f"/admin/api/workspace/default/application/{self.application.id}/orchestrator_integration"

    def test_returns_endpoint_token_and_default_params(self):
        api_key = ApplicationApiKey.objects.create(
            id=uuid.uuid7(),
            secret_key='agent-testkey1234567890abcdef1234',
            application_id=self.application.id,
            is_active=True,
            is_permanent=True,
        )

        response = self.client.get(self._endpoint_url())

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertIn('endpoint_url', data)
        self.assertTrue(data['endpoint_url'].endswith('/api/knowledge'))
        self.assertEqual(data['auth_token'], api_key.secret_key)
        self.assertIn('default_params', data)
        self.assertIsInstance(data['default_params']['kb_scope'], list)
        self.assertEqual(data['default_params']['top_n'], 5)
        self.assertEqual(data['default_params']['similarity'], 0.7)

    def test_missing_api_key_auto_generates_one(self):
        self.assertFalse(
            ApplicationApiKey.objects.filter(application_id=self.application.id).exists()
        )

        response = self.client.get(self._endpoint_url())

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['data']
        self.assertTrue(data['auth_token'].startswith('agent-'))
        self.assertTrue(
            ApplicationApiKey.objects.filter(
                application_id=self.application.id,
                secret_key=data['auth_token'],
                is_active=True,
                is_permanent=True,
            ).exists()
        )
        self.assertEqual(data['default_params']['top_n'], 5)
        self.assertEqual(data['default_params']['similarity'], 0.7)


_platform_test_path = Path(__file__).with_name('tests').joinpath('test_platform_integration.py')
if _platform_test_path.exists():
    _platform_spec = importlib.util.spec_from_file_location(
        'application.tests.test_platform_integration',
        _platform_test_path,
    )
    if _platform_spec and _platform_spec.loader:
        test_platform_integration = importlib.util.module_from_spec(_platform_spec)
        _platform_spec.loader.exec_module(test_platform_integration)
