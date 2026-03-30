import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from knowledge.models.knowledge import KnowledgeWorkflow
from models_provider.models import Model
from system_manage.models import (
    Workspace,
    WorkspaceMember,
    WorkspaceUserResourcePermission,
)
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from trigger.models import Trigger, TriggerTypeChoices
from users.models import User

ADMIN_API_PREFIX = "/admin/api"


class WorkspaceDeletionConstraintTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="ws-deletion-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="constraint-workspace",
            name="Constraint Workspace",
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def _check_delete(self, workspace_id):
        return self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{workspace_id}/check"
        )

    def _assert_cannot_delete(self, response):
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["code"], 200)
        self.assertFalse(data["data"]["can_delete"])

    def test_workspace_with_application_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="a@b.com", phone="", nick_name="u",
            username="app-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        folder = ApplicationFolder.objects.create(
            id="app-folder-ws", name="Folder", workspace_id=self.workspace.id, user=user,
        )
        Application.objects.create(
            id=uuid.uuid7(), name="App", user=user, folder=folder,
            workspace_id=self.workspace.id, type=ApplicationTypeChoices.SIMPLE,
            desc="", icon="./favicon.ico",
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_application_folder_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="af@b.com", phone="", nick_name="u",
            username="app-folder-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        ApplicationFolder.objects.create(
            id="app-folder-ws-2", name="Folder", workspace_id=self.workspace.id, user=user,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_knowledge_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="k@b.com", phone="", nick_name="u",
            username="know-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        folder = KnowledgeFolder.objects.create(
            id="know-folder-ws", name="Folder", workspace_id=self.workspace.id, user=user,
        )
        Knowledge.objects.create(
            id=uuid.uuid7(), name="Knowledge", user=user, folder=folder,
            workspace_id=self.workspace.id, type=KnowledgeType.BASE, meta={},
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_knowledge_folder_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="kf@b.com", phone="", nick_name="u",
            username="know-folder-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        KnowledgeFolder.objects.create(
            id="know-folder-ws-2", name="Folder", workspace_id=self.workspace.id, user=user,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_knowledge_workflow_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="kw@b.com", phone="", nick_name="u",
            username="know-wf-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        folder = KnowledgeFolder.objects.create(
            id="know-wf-folder", name="Folder", workspace_id=self.workspace.id, user=user,
        )
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(), name="WF Knowledge", user=user, folder=folder,
            workspace_id=self.workspace.id, type=KnowledgeType.WORKFLOW, meta={},
        )
        KnowledgeWorkflow.objects.create(
            knowledge=knowledge, workspace_id=self.workspace.id, work_flow={},
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_tool_cannot_be_deleted(self):
        folder = ToolFolder.objects.create(
            id="tool-folder-ws", name="Folder", workspace_id=self.workspace.id,
        )
        Tool.objects.create(
            name="Tool", workspace_id=self.workspace.id, desc="d",
            code="print(1)", scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM, folder=folder,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_tool_folder_cannot_be_deleted(self):
        ToolFolder.objects.create(
            id="tool-folder-ws-2", name="Folder", workspace_id=self.workspace.id,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_model_cannot_be_deleted(self):
        Model.objects.create(
            name="TestModel", model_type="LLM", model_name="test-model",
            provider="test", credential="{}", workspace_id=self.workspace.id,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_trigger_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="t@b.com", phone="", nick_name="u",
            username="trigger-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        Trigger.objects.create(
            name="Trigger", workspace_id=self.workspace.id,
            trigger_type=TriggerTypeChoices.SCHEDULED,
            trigger_setting={}, user=user,
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_workspace_with_resource_permission_cannot_be_deleted(self):
        user = User.objects.create(
            id=uuid.uuid7(), email="rp@b.com", phone="", nick_name="u",
            username="rp-user", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id, user=user,
            auth_target_type="APPLICATION", target="fake-resource-id",
            auth_type="ROLE", permission_list=["VIEW"],
        )
        self._assert_cannot_delete(self._check_delete(self.workspace.id))

    def test_empty_workspace_can_be_deleted(self):
        ws = Workspace.objects.create(id="empty-ws", name="Empty Workspace")
        response = self._check_delete(ws.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["data"]["can_delete"])

        delete_response = self.client.delete(f"{ADMIN_API_PREFIX}/workspace/{ws.id}")
        self.assertEqual(delete_response.status_code, 200)

        self.assertFalse(Workspace.objects.filter(id=ws.id).exists())


class DefaultWorkspaceMemberImmutabilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="default-ws-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        Workspace.objects.get_or_create(
            id="default", defaults={"name": "Default Workspace"}
        )
        self.client.force_authenticate(
            user=self.admin_user,
            token=get_auth(self.admin_user),
        )

    def test_default_workspace_rejects_member_add(self):
        member = User.objects.create(
            id=uuid.uuid7(), email="m@b.com", phone="", nick_name="M",
            username="default-member", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/default/add_member",
            [{"user_ids": [str(member.id)], "role_ids": ["USER"]}],
            format="json",
        )
        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)

    def test_default_workspace_rejects_member_page(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/default/user_list/1/20"
        )
        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)

    def test_default_workspace_rejects_member_remove(self):
        member = User.objects.create(
            id=uuid.uuid7(), email="mr@b.com", phone="", nick_name="MR",
            username="default-remove-member", password=password_encrypt("User123!"),
            role="USER", source="LOCAL", is_active=True,
        )
        relation = WorkspaceMember.objects.create(
            workspace_id="default", user_id=member.id, role_id="USER",
        )
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/default/remove_member/{relation.id}"
        )
        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)


class WorkspaceNameUniquenessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="ws-name-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        Workspace.objects.create(id="existing-ws", name="Existing Workspace")
        self.client.force_authenticate(
            user=self.admin_user,
            token=get_auth(self.admin_user),
        )

    def test_create_workspace_with_duplicate_name_fails(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace",
            {"name": "Existing Workspace"},
            format="json",
        )
        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)

    def test_update_workspace_to_existing_name_fails(self):
        other_ws = Workspace.objects.create(id="other-ws", name="Other Workspace")
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace",
            {"id": other_ws.id, "name": "Existing Workspace"},
            format="json",
        )
        data = json.loads(response.content)
        self.assertNotEqual(data["code"], 200)


class WorkspaceUpdatePathTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="ws-update-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(
            user=self.admin_user,
            token=get_auth(self.admin_user),
        )

    def test_post_with_id_updates_workspace_name(self):
        ws = Workspace.objects.create(id="update-ws", name="Original Name")
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace",
            {"id": ws.id, "name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["name"], "Updated Name")

        ws.refresh_from_db()
        self.assertEqual(ws.name, "Updated Name")
