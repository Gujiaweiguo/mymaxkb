import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.utils.common import password_encrypt
from users.models import User
from system_manage.models import Workspace


class WorkspaceAPIIntegrationTests(TestCase):
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

    def test_create_workspace(self):
        response = self.client.post(
            "/api/system_manage/workspace",
            {"name": "New Workspace"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_workspace_list(self):
        Workspace.objects.create(
            id="list-workspace",
            name="List Workspace",
        )

        response = self.client.get("/api/system_manage/workspace")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_workspace_detail(self):
        workspace = Workspace.objects.create(
            id="detail-workspace",
            name="Detail Workspace",
        )

        response = self.client.get(
            f"/api/system_manage/workspace/{workspace.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["name"], "Detail Workspace")

    def test_update_workspace(self):
        workspace = Workspace.objects.create(
            id="update-workspace",
            name="Update Workspace",
        )

        response = self.client.put(
            f"/api/system_manage/workspace/{workspace.id}",
            {"name": "Updated Workspace Name"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_workspace(self):
        workspace = Workspace.objects.create(
            id="delete-workspace",
            name="Delete Workspace",
        )

        response = self.client.delete(
            f"/api/system_manage/workspace/{workspace.id}"
        )

        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_default_workspace(self):
        Workspace.objects.get_or_create(
            id="default",
            defaults={"name": "Default Workspace"}
        )

        response = self.client.delete(
            "/api/system_manage/workspace/default"
        )

        self.assertNotEqual(response.status_code, 200)


class WorkspaceMemberIntegrationTests(TestCase):
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
        self.workspace = Workspace.objects.create(
            id="member-workspace",
            name="Member Workspace",
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_add_workspace_member(self):
        member = User.objects.create(
            id=uuid.uuid7(),
            email="member@example.com",
            phone="",
            nick_name="Member User",
            username="member",
            password=password_encrypt("Member123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        response = self.client.post(
            f"/api/system_manage/workspace/{self.workspace.id}/member",
            {"user_ids": [str(member.id)], "role_ids": ["USER"]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_get_workspace_members(self):
        response = self.client.get(
            f"/api/system_manage/workspace/{self.workspace.id}/member"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_delete_workspace_member(self):
        member = User.objects.create(
            id=uuid.uuid7(),
            email="delete-member@example.com",
            phone="",
            nick_name="Delete Member",
            username="deletemember",
            password=password_encrypt("Delete123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        response = self.client.delete(
            f"/api/system_manage/workspace/{self.workspace.id}/member",
            {"user_id": str(member.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
