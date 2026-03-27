import uuid_utils.compat as uuid
from django.test import TestCase
import importlib.util
from pathlib import Path

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.serializers.system_resource_application import (
    SystemResourceApplicationQuerySerializer,
)
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


_platform_test_path = Path(__file__).with_name('tests').joinpath('test_platform_integration.py')
if _platform_test_path.exists():
    _platform_spec = importlib.util.spec_from_file_location(
        'application.tests.test_platform_integration',
        _platform_test_path,
    )
    if _platform_spec and _platform_spec.loader:
        test_platform_integration = importlib.util.module_from_spec(_platform_spec)
        _platform_spec.loader.exec_module(test_platform_integration)
