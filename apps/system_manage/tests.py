import json
import uuid_utils.compat as uuid
from django.test import TestCase
from types import SimpleNamespace

from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.utils.shared_resource_auth import filter_authorized_ids
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeScope, KnowledgeType
from system_manage.models import (
    AuthTargetType,
    SharedAuthenticationType,
    SharedResourceAuthorization,
    SharedResourceType,
    Workspace,
    WorkspaceUserResourcePermission,
)
from system_manage.serializers.workspace import (
    WorkspaceMemberSerializer,
    WorkspaceQuerySerializer,
    ensure_default_workspace,
    get_workspace_user_count,
)
from system_manage.views.shared_resource_authorization import (
    SharedResourceAuthorizationView,
)
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User
from users.serializers.user import UserManageSerializer


class WorkspaceManagementSerializerTests(TestCase):
    def create_user(self, username: str, role: str = RoleConstants.USER.name):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role=role,
            source="LOCAL",
            is_active=True,
        )

    def create_workspace(self, name: str):
        return Workspace.objects.create(id=str(uuid.uuid7()), name=name)

    def test_workspace_member_add_page_and_remove_round_trip(self):
        workspace = self.create_workspace("ws-members")
        user = self.create_user("workspace-member")

        WorkspaceMemberSerializer.add(
            workspace.id,
            [{"user_ids": [user.id], "role_ids": [RoleConstants.USER.name]}],
        )

        page = WorkspaceMemberSerializer.page(workspace.id, {}, 1, 20)

        self.assertEqual(page["total"], 1)
        self.assertEqual(page["records"][0]["user_id"], user.id)
        self.assertEqual(page["records"][0]["role_id"], RoleConstants.USER.name)
        self.assertEqual(get_workspace_user_count(workspace.id), 1)

        WorkspaceMemberSerializer.remove(
            workspace.id, str(page["records"][0]["user_relation_id"])
        )

        empty_page = WorkspaceMemberSerializer.page(workspace.id, {}, 1, 20)
        self.assertEqual(empty_page["total"], 0)

    def test_delete_check_blocks_workspace_with_constrained_resources(self):
        workspace = self.create_workspace("ws-constrained")
        user = self.create_user("constrained-user")
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=workspace.id,
            user=user,
            auth_target_type=AuthTargetType.APPLICATION,
            target="resource-1",
            permission_list=["VIEW"],
        )

        delete_check = WorkspaceQuerySerializer.delete_check(workspace.id)

        self.assertFalse(delete_check["can_delete"])

    def test_default_workspace_cannot_be_deleted(self):
        ensure_default_workspace()

        delete_check = WorkspaceQuerySerializer.delete_check("default")

        self.assertFalse(delete_check["can_delete"])

    def test_get_user_members_uses_workspace_member_for_non_default_workspace(self):
        workspace = self.create_workspace("ws-auth-members")
        member = self.create_user("auth-member")
        outsider = self.create_user("auth-outsider")
        WorkspaceMemberSerializer.add(
            workspace.id,
            [{"user_ids": [member.id], "role_ids": [RoleConstants.USER.name]}],
        )

        members = UserManageSerializer().get_user_members(workspace.id)

        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["id"], member.id)
        self.assertEqual(members[0]["roles"], [RoleConstants.USER.name])
        self.assertNotEqual(members[0]["id"], outsider.id)


class SharedResourceAuthorizationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = self.create_user("shared-admin", RoleConstants.ADMIN.name)
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )

    def create_user(self, username: str, role: str = RoleConstants.USER.name):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role=role,
            source="LOCAL",
            is_active=True,
        )

    def create_knowledge(self, workspace_id: str, scope: str = KnowledgeScope.SHARED):
        folder = KnowledgeFolder.objects.create(
            id=f"knowledge-folder-{workspace_id}",
            name=f"folder-{workspace_id}",
            workspace_id=workspace_id,
        )
        return Knowledge.objects.create(
            name=f"knowledge-{workspace_id}",
            workspace_id=workspace_id,
            desc="desc",
            type=KnowledgeType.BASE,
            scope=scope,
            folder=folder,
        )

    def create_tool(self, workspace_id: str, scope: str = ToolScope.SHARED):
        folder = ToolFolder.objects.create(
            id=f"tool-folder-{workspace_id}",
            name=f"folder-{workspace_id}",
            workspace_id=workspace_id,
        )
        return Tool.objects.create(
            name=f"tool-{workspace_id}",
            workspace_id=workspace_id,
            desc="desc",
            code="print(1)",
            scope=scope,
            tool_type=ToolType.CUSTOM,
            folder=folder,
        )

    def test_get_authorization_returns_default_when_missing(self):
        knowledge = self.create_knowledge("owner-ws")
        request = self.factory.get(
            f"/system/shared/knowledge/{knowledge.id}/authorization"
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = SharedResourceAuthorizationView.as_view()(
            request, resource_type="knowledge", resource_id=str(knowledge.id)
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(
            payload["data"]["authentication_type"], SharedAuthenticationType.WHITE_LIST
        )
        self.assertEqual(payload["data"]["workspace_id_list"], [])

    def test_post_authorization_persists_configuration(self):
        tool = self.create_tool("owner-ws")
        request = self.factory.post(
            f"/system/shared/tool/{tool.id}/authorization",
            data={
                "authentication_type": SharedAuthenticationType.BLACK_LIST,
                "workspace_id_list": ["blocked-a", "blocked-b", "blocked-a"],
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = SharedResourceAuthorizationView.as_view()(
            request, resource_type="tool", resource_id=str(tool.id)
        )

        self.assertEqual(response.status_code, 200)
        instance = SharedResourceAuthorization.objects.get(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(tool.id),
        )
        self.assertEqual(
            instance.authentication_type, SharedAuthenticationType.BLACK_LIST
        )
        self.assertEqual(instance.workspace_id_list, ["blocked-a", "blocked-b"])

    def test_filter_authorized_ids_allows_same_workspace_without_record(self):
        knowledge = self.create_knowledge("owner-ws")

        authorized_ids = filter_authorized_ids(
            "knowledge", [str(knowledge.id)], "owner-ws"
        )

        self.assertEqual(authorized_ids, [str(knowledge.id)])

    def test_filter_authorized_ids_denies_cross_workspace_without_record(self):
        knowledge = self.create_knowledge("owner-ws")

        authorized_ids = filter_authorized_ids(
            "knowledge", [str(knowledge.id)], "consumer-ws"
        )

        self.assertEqual(authorized_ids, [])

    def test_filter_authorized_ids_applies_white_list(self):
        tool = self.create_tool("owner-ws")
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(tool.id),
            authentication_type=SharedAuthenticationType.WHITE_LIST,
            workspace_id_list=["consumer-ws"],
        )

        self.assertEqual(
            filter_authorized_ids("tool", [str(tool.id)], "consumer-ws"), [str(tool.id)]
        )
        self.assertEqual(filter_authorized_ids("tool", [str(tool.id)], "other-ws"), [])

    def test_filter_authorized_ids_applies_black_list(self):
        knowledge = self.create_knowledge("owner-ws")
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.KNOWLEDGE,
            resource_id=str(knowledge.id),
            authentication_type=SharedAuthenticationType.BLACK_LIST,
            workspace_id_list=["blocked-ws"],
        )

        self.assertEqual(
            filter_authorized_ids("knowledge", [str(knowledge.id)], "blocked-ws"), []
        )
        self.assertEqual(
            filter_authorized_ids("knowledge", [str(knowledge.id)], "consumer-ws"),
            [str(knowledge.id)],
        )


class SystemSettingModelTests(TestCase):
    def test_system_setting_creation(self):
        from system_manage.models import SystemSetting, SettingType

        setting = SystemSetting.objects.create(
            type=SettingType.EMAIL,
            meta={"host": "smtp.example.com", "port": 587},
        )

        self.assertEqual(setting.type, SettingType.EMAIL)
        self.assertEqual(setting.meta["host"], "smtp.example.com")

    def test_system_setting_meta_update(self):
        from system_manage.models import SystemSetting, SettingType

        setting = SystemSetting.objects.create(
            type=SettingType.LOGIN_AUTH,
            meta={"default_value": "LOCAL", "max_attempts": 3},
        )

        setting.meta["max_attempts"] = 5
        setting.save()

        setting.refresh_from_db()
        self.assertEqual(setting.meta["max_attempts"], 5)


class WorkspaceModelTests(TestCase):
    def test_workspace_creation(self):
        workspace = Workspace.objects.create(
            id="test-workspace",
            name="Test Workspace",
        )

        self.assertEqual(workspace.name, "Test Workspace")
        self.assertEqual(workspace.id, "test-workspace")

    def test_workspace_str_representation(self):
        workspace = Workspace.objects.create(
            id="str-workspace",
            name="Str Workspace",
        )

        self.assertEqual(str(workspace), "Str Workspace")

    def test_default_workspace_exists(self):
        from system_manage.serializers.workspace import ensure_default_workspace

        ensure_default_workspace()
        default = Workspace.objects.get(id="default")

        self.assertEqual(default.name, "Default Workspace")
