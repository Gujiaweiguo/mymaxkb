import uuid_utils.compat as uuid
from django.test import TestCase

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
        return Workspace.objects.create(id=workspace_id, name=name)

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
