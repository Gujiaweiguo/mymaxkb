import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from system_manage.models import (
    SharedResourceAuthorization,
    Workspace,
    WorkspaceMember,
    WorkspaceUserResourcePermission,
)
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


class ChatUserAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="regular@example.com",
            phone="",
            nick_name="Regular User",
            username="chat-user-regular",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(
            user=self.regular_user, token=get_auth(self.regular_user)
        )

    def test_non_admin_cannot_list_chat_users(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/system/chat_user/list")
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_page_chat_users(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/chat_user/user_manage/1/20"
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_create_chat_user(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/chat_user",
            {
                "username": "test-chat-user",
                "password": "Test123!",
                "nick_name": "Test Chat User",
                "email": "test@example.com",
                "user_group_ids": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_update_chat_user(self):
        from system_manage.models import ChatUser
        import uuid_utils.compat as uuid

        chat_user = ChatUser.objects.create(
            id=uuid.uuid7(),
            username="update-test-user",
            password=password_encrypt("Test123!"),
            nick_name="Update Test User",
            source="LOCAL",
        )
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/chat_user/{chat_user.id}",
            {"nick_name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_delete_chat_user(self):
        from system_manage.models import ChatUser
        import uuid_utils.compat as uuid

        chat_user = ChatUser.objects.create(
            id=uuid.uuid7(),
            username="delete-test-user",
            password=password_encrypt("Test123!"),
            nick_name="Delete Test User",
            source="LOCAL",
        )
        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/chat_user/{chat_user.id}"
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_batch_delete_chat_users(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/chat_user/batch_delete",
            ["fake-id-1", "fake-id-2"],
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_reset_chat_user_password(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/chat_user/fake-id/re_password",
            {"password": "NewPass123!", "re_password": "NewPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_get_sync_types(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/chat_user/sync_types"
        )
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_sync_chat_users(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/chat_user/sync/LOCAL"
        )
        self.assertEqual(response.status_code, 403)


class ChatUserGroupAssignmentDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="group-regular@example.com",
            phone="",
            nick_name="Group Regular User",
            username="group-regular",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(
            user=self.regular_user, token=get_auth(self.regular_user)
        )

    def test_non_admin_cannot_batch_add_chat_users_to_groups(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/chat_user/batch_add_group",
            {"ids": ["fake-id"], "user_group_ids": ["fake-group"], "is_append": True},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class ApplicationChatUserAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="application-auth-user@example.com",
            phone="",
            nick_name="Application Auth User",
            username="application-auth-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="application-auth-workspace",
            name="Application Auth Workspace",
        )
        self.folder = ApplicationFolder.objects.create(
            id="application-auth-folder",
            name="Application Auth Folder",
            workspace_id=self.workspace.id,
            user=self.user,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="application-auth-app",
            desc="Application auth app",
            user=self.user,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_non_privileged_user_cannot_access_workspace_application_chat_user_endpoints(self):
        denied_requests = [
            (
                "get",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/APPLICATION/{self.application.id}/user_group",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/APPLICATION/{self.application.id}/user_group",
                [{"user_group_id": "fake-group", "is_auth": True}],
            ),
            (
                "get",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/APPLICATION/{self.application.id}/user_group_id/fake-group/1/20",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/APPLICATION/{self.application.id}/user_group_id/fake-group",
                [{"chat_user_id": "fake-chat-user", "is_auth": True}],
            ),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)


class KnowledgeChatUserAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="knowledge-auth-user@example.com",
            phone="",
            nick_name="Knowledge Auth User",
            username="knowledge-auth-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="knowledge-auth-workspace",
            name="Knowledge Auth Workspace",
        )
        self.folder = KnowledgeFolder.objects.create(
            id="knowledge-auth-folder",
            name="Knowledge Auth Folder",
            workspace_id=self.workspace.id,
            user=self.user,
        )
        self.knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="knowledge-auth-resource",
            desc="Knowledge auth resource",
            user=self.user,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_non_privileged_user_cannot_access_workspace_knowledge_chat_user_endpoints(self):
        denied_requests = [
            (
                "get",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/KNOWLEDGE/{self.knowledge.id}/user_group",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/KNOWLEDGE/{self.knowledge.id}/user_group",
                [{"user_group_id": "fake-group", "is_auth": True}],
            ),
            (
                "get",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/KNOWLEDGE/{self.knowledge.id}/user_group_id/fake-group/1/20",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/KNOWLEDGE/{self.knowledge.id}/user_group_id/fake-group",
                [{"chat_user_id": "fake-chat-user", "is_auth": True}],
            ),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)

    def test_non_privileged_user_cannot_access_system_knowledge_chat_user_endpoints(self):
        denied_requests = [
            (
                "get",
                f"{ADMIN_API_PREFIX}/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group",
                [{"user_group_id": "fake-group", "is_auth": True}],
            ),
            (
                "get",
                f"{ADMIN_API_PREFIX}/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group_id/fake-group/1/20",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group_id/fake-group",
                [{"chat_user_id": "fake-chat-user", "is_auth": True}],
            ),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)


class SharedResourceAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="shared-resource-user@example.com",
            phone="",
            nick_name="Shared Resource User",
            username="shared-resource-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="shared-resource-workspace",
            name="Shared Resource Workspace",
        )
        self.folder = ToolFolder.objects.create(
            id="shared-resource-tool-folder",
            name="Shared Resource Tool Folder",
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            name="Shared Resource Tool",
            workspace_id=self.workspace.id,
            desc="shared resource tool",
            code="print(1)",
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_non_admin_cannot_manage_shared_resource_authorization_endpoints(self):
        denied_requests = [
            (
                "get",
                f"{ADMIN_API_PREFIX}/system/shared/TOOL/{self.tool.id}/authorization",
                None,
            ),
            (
                "post",
                f"{ADMIN_API_PREFIX}/system/shared/TOOL/{self.tool.id}/authorization",
                {"authentication_type": "WHITE_LIST", "workspace_id_list": [self.workspace.id]},
            ),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)

        self.assertFalse(
            SharedResourceAuthorization.objects.filter(
                resource_type="TOOL",
                resource_id=str(self.tool.id),
            ).exists()
        )
