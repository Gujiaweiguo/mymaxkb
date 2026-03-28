import uuid_utils.compat as uuid
from django.test import TestCase

from common.utils.shared_resource_auth import (
    filter_authorized_ids,
    filter_ce_authorized_ids,
)
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from system_manage.models import (
    SharedAuthenticationType,
    SharedResourceAuthorization,
    SharedResourceType,
    Workspace,
)
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User


class SharedResourceAuthUtilsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='shared-auth-admin@example.com',
            phone='',
            nick_name='Shared Auth Admin',
            username='shared-auth-admin',
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.target_workspace = Workspace.objects.create(
            id='shared-auth-target-workspace',
            name='Shared Auth Target Workspace',
        )
        self.source_workspace = Workspace.objects.create(
            id='shared-auth-source-workspace',
            name='Shared Auth Source Workspace',
        )
        self.tool_folder = ToolFolder.objects.create(
            id='shared-auth-tool-folder',
            name='Shared Auth Tool Folder',
            workspace_id=self.source_workspace.id,
        )
        self.local_tool_folder = ToolFolder.objects.create(
            id='shared-auth-local-tool-folder',
            name='Shared Auth Local Tool Folder',
            workspace_id=self.target_workspace.id,
        )
        self.knowledge_folder = KnowledgeFolder.objects.create(
            id='shared-auth-knowledge-folder',
            name='Shared Auth Knowledge Folder',
            workspace_id=self.source_workspace.id,
            user=self.user,
        )
        self.shared_tool = Tool.objects.create(
            name='shared-tool',
            workspace_id=self.source_workspace.id,
            desc='shared tool',
            code='print(1)',
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.tool_folder,
        )
        self.blocked_tool = Tool.objects.create(
            name='blocked-tool',
            workspace_id=self.source_workspace.id,
            desc='blocked tool',
            code='print(2)',
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.tool_folder,
        )
        self.local_tool = Tool.objects.create(
            name='local-tool',
            workspace_id=self.target_workspace.id,
            desc='local tool',
            code='print(3)',
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.local_tool_folder,
        )
        self.shared_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='shared-knowledge',
            workspace_id=self.source_workspace.id,
            desc='shared knowledge',
            type=KnowledgeType.BASE,
            meta={},
            user=self.user,
            folder=self.knowledge_folder,
        )

    def test_filter_ce_authorized_ids_denies_cross_workspace_tool_without_auth_row(self):
        result = filter_ce_authorized_ids(
            'tool',
            [str(self.shared_tool.id)],
            self.target_workspace.id,
        )

        self.assertEqual(result, [])

    def test_filter_ce_authorized_ids_allows_whitelisted_workspace(self):
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(self.shared_tool.id),
            authentication_type=SharedAuthenticationType.WHITE_LIST,
            workspace_id_list=[self.target_workspace.id],
        )

        result = filter_ce_authorized_ids(
            'tool',
            [str(self.shared_tool.id)],
            self.target_workspace.id,
        )

        self.assertEqual(result, [str(self.shared_tool.id)])

    def test_filter_ce_authorized_ids_applies_blacklist_inverse_rule(self):
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(self.shared_tool.id),
            authentication_type=SharedAuthenticationType.BLACK_LIST,
            workspace_id_list=[self.target_workspace.id],
        )

        blocked = filter_ce_authorized_ids(
            'tool',
            [str(self.shared_tool.id)],
            self.target_workspace.id,
        )
        allowed = filter_ce_authorized_ids(
            'tool',
            [str(self.shared_tool.id)],
            'different-workspace',
        )

        self.assertEqual(blocked, [])
        self.assertEqual(allowed, [str(self.shared_tool.id)])

    def test_filter_authorized_ids_preserves_order_for_local_and_shared_tools(self):
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(self.shared_tool.id),
            authentication_type=SharedAuthenticationType.WHITE_LIST,
            workspace_id_list=[self.target_workspace.id],
        )
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.TOOL,
            resource_id=str(self.blocked_tool.id),
            authentication_type=SharedAuthenticationType.WHITE_LIST,
            workspace_id_list=['another-workspace'],
        )
        ordered_ids = [
            str(self.shared_tool.id),
            str(self.blocked_tool.id),
            str(self.local_tool.id),
        ]

        result = filter_authorized_ids('tool', ordered_ids, self.target_workspace.id)

        self.assertEqual(
            result,
            [str(self.shared_tool.id), str(self.local_tool.id)],
        )

    def test_filter_authorized_ids_supports_knowledge_shared_resource_rules(self):
        SharedResourceAuthorization.objects.create(
            resource_type=SharedResourceType.KNOWLEDGE,
            resource_id=str(self.shared_knowledge.id),
            authentication_type=SharedAuthenticationType.WHITE_LIST,
            workspace_id_list=[self.target_workspace.id],
        )

        result = filter_authorized_ids(
            'knowledge',
            [str(self.shared_knowledge.id)],
            self.target_workspace.id,
        )

        self.assertEqual(result, [str(self.shared_knowledge.id)])
