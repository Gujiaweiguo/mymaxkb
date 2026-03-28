import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from system_manage.models import Workspace, WorkspaceMember, WorkspaceUserResourcePermission
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User


ADMIN_API_PREFIX = "/admin/api"


class WorkspaceAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="workspace-api-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_create_workspace(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace",
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

        response = self.client.get(f"{ADMIN_API_PREFIX}/workspace")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_workspace_detail(self):
        workspace = Workspace.objects.create(
            id="detail-workspace",
            name="Detail Workspace",
        )

        response = self.client.get(f"{ADMIN_API_PREFIX}/workspace")

        self.assertEqual(response.status_code, 200)

    def test_update_workspace(self):
        workspace = Workspace.objects.create(
            id="update-workspace",
            name="Update Workspace",
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{workspace.id}",
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
            f"{ADMIN_API_PREFIX}/workspace/{workspace.id}"
        )

        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_default_workspace(self):
        Workspace.objects.get_or_create(
            id="default",
            defaults={"name": "Default Workspace"}
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/default"
        )

        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)


class WorkspaceMemberIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="workspace-member-admin",
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
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/add_member",
            [{"user_ids": [str(member.id)], "role_ids": ["USER"]}],
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_get_workspace_members(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_list/1/20"
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

        relation_id = str(
            WorkspaceMember.objects.create(
                workspace_id=self.workspace.id,
                user_id=member.id,
                role_id="USER",
            ).id
        )

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/remove_member/{relation_id}"
        )

        self.assertEqual(response.status_code, 200)


class WorkspaceAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="workspace-user@example.com",
            phone="",
            nick_name="Workspace User",
            username="workspace-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="auth-workspace",
            name="Auth Workspace",
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_non_admin_cannot_manage_workspace_endpoints(self):
        denied_requests = [
            ("get", f"{ADMIN_API_PREFIX}/workspace", None),
            ("post", f"{ADMIN_API_PREFIX}/workspace", {"name": "Denied Workspace"}),
            (
                "post",
                f"{ADMIN_API_PREFIX}/workspace",
                {"id": self.workspace.id, "name": "Denied Rename"},
            ),
            ("delete", f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}", None),
            ("get", f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/check", None),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)


class ResourceAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="resource-user@example.com",
            phone="",
            nick_name="Resource User",
            username="resource-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.target_user = User.objects.create(
            id=uuid.uuid7(),
            email="resource-target@example.com",
            phone="",
            nick_name="Resource Target",
            username="resource-target",
            password=password_encrypt("Target123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="resource-auth-workspace",
            name="Resource Auth Workspace",
        )
        self.folder = ToolFolder.objects.create(
            id="resource-tool-folder",
            name="Resource Tool Folder",
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            name="Resource Tool",
            workspace_id=self.workspace.id,
            desc="desc",
            code="print(1)",
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_non_privileged_user_cannot_read_user_resource_permission_endpoints(self):
        denied_requests = [
            (
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/user/{self.target_user.id}/resource/TOOL",
                None,
            ),
            (
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/user/{self.target_user.id}/resource/TOOL/1/20",
                None,
            ),
        ]

        for url, payload in denied_requests:
            with self.subTest(url=url):
                response = self.client.get(url, payload, format="json")
                self.assertEqual(response.status_code, 403)

    def test_non_privileged_user_cannot_read_resource_user_permission_endpoints(self):
        denied_requests = [
            (
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/resource_user_permission/resource/{self.tool.id}/resource/TOOL",
                None,
            ),
            (
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/resource_user_permission/resource/{self.tool.id}/resource/TOOL/1/20",
                None,
            ),
        ]

        for url, payload in denied_requests:
            with self.subTest(url=url):
                response = self.client.get(url, payload, format="json")
                self.assertEqual(response.status_code, 403)

    def test_non_privileged_user_cannot_edit_user_resource_permission_endpoints(self):
        url = (
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/"
            f"user/{self.target_user.id}/resource/TOOL"
        )

        response = self.client.put(
            url,
            [{"target_id": str(self.tool.id), "permission": "VIEW"}],
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            WorkspaceUserResourcePermission.objects.filter(
                workspace_id=self.workspace.id,
                user_id=self.target_user.id,
                auth_target_type="TOOL",
                target=str(self.tool.id),
            ).exists()
        )

    def test_non_privileged_user_cannot_edit_resource_user_permission_endpoints(self):
        url = (
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/resource_user_permission/"
            f"resource/{self.tool.id}/resource/TOOL"
        )

        response = self.client.put(
            url,
            [{"user_id": str(self.target_user.id), "permission": "VIEW"}],
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            WorkspaceUserResourcePermission.objects.filter(
                workspace_id=self.workspace.id,
                user_id=self.target_user.id,
                auth_target_type="TOOL",
                target=str(self.tool.id),
            ).exists()
        )

    def test_non_admin_cannot_manage_workspace_member_endpoints(self):
        member = User.objects.create(
            id=uuid.uuid7(),
            email="workspace-member@example.com",
            phone="",
            nick_name="Workspace Member",
            username="workspace-member",
            password=password_encrypt("Member123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        relation_id = str(
            WorkspaceMember.objects.create(
                workspace_id=self.workspace.id,
                user_id=member.id,
                role_id="USER",
            ).id
        )
        denied_requests = [
            ("get", f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_list/1/20", None),
            (
                "post",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/add_member",
                [{"user_ids": [str(member.id)], "role_ids": ["USER"]}],
            ),
            ("post", f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/remove_member/{relation_id}", None),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
