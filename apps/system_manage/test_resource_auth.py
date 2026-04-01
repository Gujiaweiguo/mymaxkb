import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from models_provider.models import Model
from common.constants.permission_constants import ResourceAuthType, ResourcePermission
from system_manage.models import Workspace, WorkspaceUserResourcePermission
from system_manage.models.workspace_user_permission import AuthTargetType
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from trigger.models import Trigger, TriggerTypeChoices
from users.models import User


ADMIN_API_PREFIX = "/admin/api"


class ResourceAuthTestMixin:
    @staticmethod
    def create_ce_user(username_prefix="resource-user"):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username_prefix}@example.com",
            phone="",
            nick_name=username_prefix,
            username=username_prefix,
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

    @staticmethod
    def create_workspace(name="test-workspace"):
        return Workspace.objects.create(
            id=str(uuid.uuid7()),
            name=name,
        )

    @staticmethod
    def create_admin_user(username_prefix="resource-admin"):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username_prefix}@example.com",
            phone="",
            nick_name=username_prefix,
            username=username_prefix,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    @staticmethod
    def setup_authenticated_client(user):
        client = APIClient()
        client.force_authenticate(user=user, token=get_auth(user))
        return client


class ApplicationResourceDeniedTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("app-denied-user")
        self.workspace = ResourceAuthTestMixin.create_workspace("app-denied-ws")
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("app-denied-admin")
        self.folder = ApplicationFolder.objects.create(
            id=str(uuid.uuid7()),
            name="App Denied Folder",
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="denied-app",
            desc="denied application",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_non_member_cannot_list_applications(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/application"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_create_application(self):
        resp = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/application",
            {"name": "Blocked App", "type": ApplicationTypeChoices.SIMPLE},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_read_application_detail(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/application/{self.application.id}"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_update_application(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/application/{self.application.id}",
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_delete_application(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/application/{self.application.id}"
        )
        self.assertEqual(resp.status_code, 403)


class KnowledgeResourceDeniedTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("kb-denied-user")
        self.workspace = ResourceAuthTestMixin.create_workspace("kb-denied-ws")
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("kb-denied-admin")
        self.folder = KnowledgeFolder.objects.create(
            id=str(uuid.uuid7()),
            name="KB Denied Folder",
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="denied-knowledge",
            desc="denied knowledge",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=KnowledgeType.BASE,
            meta={},
        )

    def test_non_member_cannot_list_knowledge(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/knowledge"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_create_knowledge(self):
        resp = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/knowledge/base",
            {"name": "Blocked KB", "type": 0},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_read_knowledge_detail(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/knowledge/{self.knowledge.id}"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_update_knowledge(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/knowledge/{self.knowledge.id}",
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_delete_knowledge(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/knowledge/{self.knowledge.id}"
        )
        self.assertEqual(resp.status_code, 403)


class ModelResourceDeniedTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("model-denied-user")
        self.workspace = ResourceAuthTestMixin.create_workspace("model-denied-ws")
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("model-denied-admin")
        self.model = Model.objects.create(
            id=uuid.uuid7(),
            name="denied-model",
            model_type="LLM",
            model_name="denied-model-name",
            credential={},
            user=self.admin,
            workspace_id=self.workspace.id,
        )

    def test_non_member_cannot_list_models(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/model"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_create_model(self):
        resp = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/model",
            {"name": "Blocked Model", "model_type": "LLM", "model_name": "blocked"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_read_model_detail(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/model/{self.model.id}"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_update_model(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/model/{self.model.id}",
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_delete_model(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/model/{self.model.id}"
        )
        self.assertEqual(resp.status_code, 403)


class ToolResourceDeniedTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("tool-denied-user")
        self.workspace = ResourceAuthTestMixin.create_workspace("tool-denied-ws")
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("tool-denied-admin")
        self.folder = ToolFolder.objects.create(
            id=str(uuid.uuid7()),
            name="Tool Denied Folder",
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            id=uuid.uuid7(),
            name="denied-tool",
            workspace_id=self.workspace.id,
            desc="denied tool",
            code="print(1)",
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )

    def test_non_member_cannot_list_tools(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_create_tool(self):
        resp = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool",
            {"name": "Blocked Tool", "code": "print(1)"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_read_tool_detail(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_update_tool(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}",
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_delete_tool(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}"
        )
        self.assertEqual(resp.status_code, 403)


class ToolDefaultWorkspaceUserSplitTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("tool-default-user")
        self.workspace, _ = Workspace.objects.get_or_create(
            id="default", defaults={"name": "default"}
        )
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("tool-default-admin")
        self.folder = ToolFolder.objects.create(
            id=str(uuid.uuid7()),
            name="Tool Default Folder",
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            id=uuid.uuid7(),
            name="default-tool",
            workspace_id=self.workspace.id,
            desc="default workspace tool",
            code="print(1)",
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )

    def test_ce_user_can_list_tools_on_default_workspace(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool"
        )

        self.assertEqual(resp.status_code, 200)

    def test_ce_user_can_read_tool_detail_on_default_workspace(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}"
        )

        self.assertEqual(resp.status_code, 200)

    def test_ce_user_cannot_update_tool_on_default_workspace(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}",
            {"name": "Blocked Default Update"},
            format="json",
        )

        self.assertEqual(resp.status_code, 403)

    def test_ce_user_cannot_delete_tool_on_default_workspace(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}"
        )

        self.assertEqual(resp.status_code, 403)


class ToolDefaultWorkspaceManageGrantTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("tool-manage-user")
        self.workspace, _ = Workspace.objects.get_or_create(
            id="default", defaults={"name": "default"}
        )
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("tool-manage-admin")
        self.folder = ToolFolder.objects.create(
            id=str(uuid.uuid7()),
            name="Tool Manage Grant Folder",
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            id=uuid.uuid7(),
            name="manage-grant-tool",
            workspace_id=self.workspace.id,
            desc="tool for manage grant tests",
            code="print(1)",
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )
        self._grant_manage_permission()
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def _grant_manage_permission(self):
        WorkspaceUserResourcePermission.objects.create(
            id=uuid.uuid7(),
            workspace_id=self.workspace.id,
            user=self.user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
            auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value,
            permission_list=[ResourcePermission.MANAGE.value, ResourcePermission.VIEW.value],
        )

    def test_ce_user_with_manage_grant_can_update_tool_on_default_workspace(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}",
            {"name": "Updated Manage Grant Tool"},
            format="json",
        )

        self.assertEqual(resp.status_code, 200)
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.name, "Updated Manage Grant Tool")

    def test_ce_user_with_manage_grant_can_delete_tool_on_default_workspace(self):
        tool_id = self.tool.id
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/tool/{self.tool.id}"
        )

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Tool.objects.filter(id=tool_id).exists())


class TriggerResourceDeniedTests(TestCase):
    def setUp(self):
        self.user = ResourceAuthTestMixin.create_ce_user("trigger-denied-user")
        self.workspace = ResourceAuthTestMixin.create_workspace("trigger-denied-ws")
        self.client = ResourceAuthTestMixin.setup_authenticated_client(self.user)
        self.admin = ResourceAuthTestMixin.create_admin_user("trigger-denied-admin")
        self.trigger = Trigger.objects.create(
            id=uuid.uuid7(),
            name="denied-trigger",
            trigger_type=TriggerTypeChoices.EVENT,
            trigger_setting={},
            workspace_id=self.workspace.id,
            user=self.admin,
        )

    def test_non_member_cannot_list_triggers(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/trigger"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_create_trigger(self):
        resp = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/trigger",
            {"name": "Blocked Trigger", "type": "EVENT", "setting": {}},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_read_trigger_detail(self):
        resp = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/trigger/{self.trigger.id}"
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_update_trigger(self):
        resp = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/trigger/{self.trigger.id}",
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_non_member_cannot_delete_trigger(self):
        resp = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/trigger/{self.trigger.id}"
        )
        self.assertEqual(resp.status_code, 403)
