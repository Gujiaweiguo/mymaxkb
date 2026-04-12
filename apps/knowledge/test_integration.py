import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import MagicMock, patch

from common.utils.common import password_encrypt
from common.auth.handle.impl.user_token import get_auth
from knowledge.models import (
    Document,
    Knowledge,
    KnowledgeFolder,
    KnowledgeScope,
    KnowledgeType,
    Paragraph,
    State,
    Status,
    TaskType,
)
from models_provider.models import Model
from system_manage.models.resource_mapping import ResourceMapping
from system_manage.models.workspace import Workspace
from users.models import User


ADMIN_API_PREFIX = "/admin/api"


class KnowledgeAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="knowledge-api-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="member@example.com",
            phone="",
            nick_name="Member User",
            username="knowledge-api-member",
            password=password_encrypt("Admin123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.default_workspace, _ = Workspace.objects.get_or_create(
            id='default', defaults={'name': 'Default Workspace'}
        )
        self.ops_workspace, _ = Workspace.objects.get_or_create(
            id='ops', defaults={'name': 'Operations Workspace'}
        )
        self.folder = KnowledgeFolder.objects.create(
            id="kb-folder",
            name="KB Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.ops_folder = KnowledgeFolder.objects.create(
            id="kb-folder-ops",
            name="Ops KB Folder",
            user=self.admin_user,
            workspace_id="ops",
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_admin_can_page_system_resource_knowledge_list(self):
        default_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Default Knowledge",
            desc="Default Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        ops_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Ops Knowledge",
            desc="Ops Description",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.WEB,
            scope=KnowledgeScope.WORKSPACE,
        )
        ResourceMapping.objects.create(
            source_type="APPLICATION",
            target_type="KNOWLEDGE",
            source_id=str(uuid.uuid7()),
            target_id=str(ops_knowledge.id),
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/1/20",
            {"workspace_ids": json.dumps(["ops"]), "create_user": str(self.regular_user.id)},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["total"], 1)
        self.assertEqual(len(payload["data"]["records"]), 1)
        record = payload["data"]["records"][0]
        self.assertEqual(record["id"], str(ops_knowledge.id))
        self.assertEqual(record["name"], "Ops Knowledge")
        self.assertEqual(record["workspace_id"], "ops")
        self.assertEqual(record["workspace_name"], "Operations Workspace")
        self.assertEqual(record["nick_name"], "Member User")
        self.assertEqual(record["resource_count"], 1)
        self.assertEqual(record["type"], KnowledgeType.WEB)
        self.assertNotEqual(record["id"], str(default_knowledge.id))

    def test_regular_user_cannot_page_system_resource_knowledge_list(self):
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(f"{ADMIN_API_PREFIX}/system/resource/knowledge/1/20")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_system_resource_knowledge_detail(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Detail System Knowledge",
            desc="System Detail Description",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
            meta={"source_url": "https://example.com"},
            file_size_limit=256,
            file_count_limit=12,
        )
        ResourceMapping.objects.create(
            source_type="APPLICATION",
            target_type="KNOWLEDGE",
            source_id=str(uuid.uuid7()),
            target_id=str(knowledge.id),
        )

        response = self.client.get(f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["id"], str(knowledge.id))
        self.assertEqual(payload["data"]["name"], "Detail System Knowledge")
        self.assertEqual(payload["data"]["workspace_id"], "ops")
        self.assertEqual(payload["data"]["file_size_limit"], 256)
        self.assertEqual(payload["data"]["file_count_limit"], 12)
        self.assertEqual(payload["data"]["meta"], {"source_url": "https://example.com"})
        self.assertEqual(payload["data"]["application_id_list"], [])

    def test_regular_user_cannot_get_system_resource_knowledge_detail(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Forbidden Detail",
            desc="System Detail Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}")

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_detail_returns_404_for_missing_id(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}")

        self.assertEqual(response.status_code, 404)

    def test_admin_can_update_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Editable System Knowledge",
            desc="Before Update",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
            file_size_limit=100,
            file_count_limit=50,
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}",
            {
                "name": "Updated System Knowledge",
                "desc": "After Update",
                "file_size_limit": 512,
                "file_count_limit": 24,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["name"], "Updated System Knowledge")
        self.assertEqual(payload["data"]["desc"], "After Update")
        self.assertEqual(payload["data"]["file_size_limit"], 512)
        self.assertEqual(payload["data"]["file_count_limit"], 24)

        knowledge.refresh_from_db()
        self.assertEqual(knowledge.name, "Updated System Knowledge")
        self.assertEqual(knowledge.desc, "After Update")
        self.assertEqual(knowledge.file_size_limit, 512)
        self.assertEqual(knowledge.file_count_limit, 24)

    def test_regular_user_cannot_update_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Forbidden Update",
            desc="Before Update",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}",
            {"name": "Should Not Update"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_update_returns_404_for_missing_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}",
            {"name": "Missing Knowledge"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_delete_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Delete System Knowledge",
            desc="Delete Description",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertFalse(Knowledge.objects.filter(id=knowledge.id).exists())

    def test_regular_user_cannot_delete_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Forbidden System Delete",
            desc="Delete Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_delete_returns_404_for_missing_id(self):
        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_export_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Export System Knowledge",
            desc="Export Description",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/export"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")
        self.assertIn('attachment; filename="knowledge.xlsx"', response["Content-Disposition"])

    def test_regular_user_cannot_export_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Forbidden System Export",
            desc="Export Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/export"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_export_returns_404_for_missing_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/export"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_export_zip_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Export Zip System Knowledge",
            desc="Export Zip Description",
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id="ops",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/export_zip"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn(
            f'attachment; filename="{knowledge.name}.zip"',
            response["Content-Disposition"],
        )

    def test_regular_user_cannot_export_zip_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Forbidden System Export Zip",
            desc="Export Zip Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/export_zip"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_export_zip_returns_404_for_missing_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/export_zip"
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.knowledge.embedding_by_knowledge.delay')
    def test_admin_can_embedding_system_resource_knowledge(self, delay_mock):
        model = Model.objects.create(
            id=uuid.uuid7(),
            name='knowledge-embedding-model',
            workspace_id='ops',
            model_type='EMBEDDING',
            model_name='test-embedding-model',
            provider='test-provider',
            credential='{}',
            user=self.admin_user,
        )
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Embedding System Knowledge',
            desc='Embedding Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
            embedding_model_id=str(model.id),
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/embedding"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        delay_mock.assert_called_once_with(str(knowledge.id), str(model.id))

    def test_regular_user_cannot_embedding_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden System Embedding',
            desc='Embedding Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/embedding"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_embedding_returns_404_for_missing_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/embedding"
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.knowledge.get_embedding_model_by_knowledge_id')
    @patch('knowledge.serializers.knowledge.VectorStore.get_embedding_vector')
    def test_admin_can_hit_test_system_resource_knowledge(
        self, get_embedding_vector_mock, get_embedding_model_mock
    ):
        vector_store = MagicMock()
        vector_store.hit_test.return_value = []
        get_embedding_vector_mock.return_value = vector_store
        get_embedding_model_mock.return_value = MagicMock()
        model = Model.objects.create(
            id=uuid.uuid7(),
            name='knowledge-hit-test-model',
            workspace_id='ops',
            model_type='EMBEDDING',
            model_name='test-hit-test-model',
            provider='test-provider',
            credential='{}',
            user=self.admin_user,
        )
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Hit Test System Knowledge',
            desc='Hit Test Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
            embedding_model_id=str(model.id),
        )

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/hit_test",
            {
                'query_text': 'test query',
                'top_number': 5,
                'similarity': 0.5,
                'search_mode': 'embedding',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], [])
        vector_store.hit_test.assert_called_once()

    def test_regular_user_cannot_hit_test_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden System Hit Test',
            desc='Hit Test Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/hit_test",
            {
                'query_text': 'test query',
                'top_number': 5,
                'similarity': 0.5,
                'search_mode': 'embedding',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_hit_test_returns_404_for_missing_id(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/hit_test",
            {
                'query_text': 'test query',
                'top_number': 5,
                'similarity': 0.5,
                'search_mode': 'embedding',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.knowledge.generate_related_by_knowledge_id.delay')
    def test_admin_can_generate_related_system_resource_knowledge(self, delay_mock):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Generate Related System Knowledge',
            desc='Generate Related Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        model_id = str(uuid.uuid7())
        state_list = ['0', '1']

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/generate_related",
            {
                'model_id': model_id,
                'prompt': 'Generate questions',
                'state_list': state_list,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        delay_mock.assert_called_once_with(
            str(knowledge.id),
            model_id,
            None,
            'Generate questions',
            state_list,
        )

    def test_regular_user_cannot_generate_related_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden System Generate Related',
            desc='Generate Related Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/generate_related",
            {
                'model_id': str(uuid.uuid7()),
                'prompt': 'Generate questions',
                'state_list': ['0'],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_generate_related_returns_404_for_missing_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/generate_related",
            {
                'model_id': str(uuid.uuid7()),
                'prompt': 'Generate questions',
                'state_list': ['0'],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.knowledge.sync_replace_web_knowledge.delay')
    def test_admin_can_sync_system_resource_knowledge(self, delay_mock):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Sync System Knowledge',
            desc='Sync Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.WEB,
            scope=KnowledgeScope.WORKSPACE,
            meta={'source_url': 'https://example.com', 'selector': ''},
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/sync?sync_type=replace"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        delay_mock.assert_called_once_with(str(knowledge.id), 'https://example.com', '')

    def test_regular_user_cannot_sync_system_resource_knowledge(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden System Sync',
            desc='Sync Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.WEB,
            scope=KnowledgeScope.WORKSPACE,
            meta={'source_url': 'https://example.com', 'selector': ''},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/sync?sync_type=replace"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_knowledge_sync_returns_404_for_missing_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/sync?sync_type=replace"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_page_system_resource_document_list(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Document List Knowledge',
            desc='Document List Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Ops Document',
            char_length=128,
            type=KnowledgeType.BASE,
            meta={},
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/1/20"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        self.assertEqual(payload['data']['records'][0]['id'], str(document.id))
        self.assertEqual(payload['data']['records'][0]['knowledge_id'], str(knowledge.id))
        self.assertEqual(payload['data']['records'][0]['name'], 'Ops Document')

    def test_admin_can_filter_system_resource_document_list_by_is_active(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Filtered Document List Knowledge',
            desc='Filtered Document List Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        active_document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Active Document',
            char_length=128,
            type=KnowledgeType.BASE,
            meta={},
            is_active=True,
        )
        inactive_document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Inactive Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
            is_active=False,
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/1/20",
            {'is_active': 'false'},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        self.assertEqual(payload['data']['records'][0]['id'], str(inactive_document.id))
        self.assertNotEqual(payload['data']['records'][0]['id'], str(active_document.id))

    def test_regular_user_cannot_page_system_resource_document_list(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Document List',
            desc='Document List Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/1/20"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_list_returns_404_for_missing_knowledge_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/1/20"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_get_system_resource_document_detail(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Document Detail Knowledge',
            desc='Document Detail Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Detail Document',
            char_length=256,
            type=KnowledgeType.BASE,
            meta={'source_url': 'https://example.com/doc'},
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['id'], str(document.id))
        self.assertEqual(payload['data']['knowledge_id'], str(knowledge.id))
        self.assertEqual(payload['data']['name'], 'Detail Document')
        self.assertEqual(payload['data']['char_length'], 256)
        self.assertEqual(payload['data']['meta'], {'source_url': 'https://example.com/doc'})

    def test_regular_user_cannot_get_system_resource_document_detail(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Document Detail',
            desc='Document Detail Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Detail Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_detail_returns_404_for_missing_knowledge_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_edit_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Editable Document Knowledge',
            desc='Editable Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Editable Document',
            char_length=100,
            type=KnowledgeType.BASE,
            meta={},
            is_active=True,
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}",
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['is_active'], False)

        document.refresh_from_db()
        self.assertFalse(document.is_active)

    def test_regular_user_cannot_edit_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Editable Document Knowledge',
            desc='Editable Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Editable Document',
            char_length=80,
            type=KnowledgeType.BASE,
            meta={},
            is_active=True,
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}",
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_edit_returns_404_for_missing_knowledge_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}",
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.document.delete_embedding_by_document')
    def test_admin_can_delete_system_resource_document(self, delete_embedding_mock):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Delete Document Knowledge',
            desc='Delete Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Delete Target Document',
            char_length=128,
            type=KnowledgeType.BASE,
            meta={},
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertFalse(Document.objects.filter(id=document.id).exists())
        delete_embedding_mock.assert_called_once_with(str(document.id))

    def test_regular_user_cannot_delete_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Delete Doc Knowledge',
            desc='Delete Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Delete Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_delete_returns_404_for_missing_knowledge_id(self):
        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_export_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Export Document Knowledge',
            desc='Export Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Export Document',
            char_length=128,
            type=KnowledgeType.BASE,
            meta={},
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/export"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.ms-excel')
        self.assertIn('attachment; filename="data.xlsx"', response['Content-Disposition'])

    def test_regular_user_cannot_export_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Export Doc Knowledge',
            desc='Export Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Export Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/export"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_export_returns_404_for_missing_knowledge_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}/export"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_export_zip_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Export Zip Document Knowledge',
            desc='Export Zip Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Export Zip Document',
            char_length=128,
            type=KnowledgeType.BASE,
            meta={},
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/export_zip"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertIn(
            f'attachment; filename="{document.name}.zip"',
            response['Content-Disposition'],
        )

    def test_regular_user_cannot_export_zip_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Export Zip Doc Knowledge',
            desc='Export Zip Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Export Zip Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/export_zip"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_export_zip_returns_404_for_missing_knowledge_id(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}/export_zip"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_cancel_task_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Cancel Task Document Knowledge',
            desc='Cancel Task Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Cancel Task Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
            status=State.PENDING.value,
        )
        paragraph = Paragraph.objects.create(
            knowledge=knowledge,
            document=document,
            content='cancel task paragraph',
            status=State.PENDING.value,
            position=1,
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/cancel_task",
            {'type': TaskType.EMBEDDING.value},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        document.refresh_from_db()
        paragraph.refresh_from_db()
        self.assertEqual(
            Status(document.status).task_status[TaskType.EMBEDDING],
            State.REVOKE,
        )
        self.assertEqual(
            Status(paragraph.status).task_status[TaskType.EMBEDDING],
            State.REVOKE,
        )

    def test_regular_user_cannot_cancel_task_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Cancel Task Doc Knowledge',
            desc='Cancel Task Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Cancel Task Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/cancel_task",
            {'type': TaskType.EMBEDDING.value},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_cancel_task_returns_404_for_missing_knowledge_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}/cancel_task",
            {'type': TaskType.EMBEDDING.value},
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.document.embedding_by_document.delay')
    def test_admin_can_refresh_system_resource_document(self, delay_mock):
        model = Model.objects.create(
            id=uuid.uuid7(),
            name='document-refresh-model',
            workspace_id='ops',
            model_type='EMBEDDING',
            model_name='test-refresh-model',
            provider='test-provider',
            credential='{}',
            user=self.admin_user,
        )
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Refresh Document Knowledge',
            desc='Refresh Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
            embedding_model_id=str(model.id),
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Refresh Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
            status=State.SUCCESS.value,
        )
        paragraph = Paragraph.objects.create(
            knowledge=knowledge,
            document=document,
            content='refresh paragraph',
            status=State.SUCCESS.value,
            position=1,
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/refresh",
            {'state_list': [State.SUCCESS.value]},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        document.refresh_from_db()
        paragraph.refresh_from_db()
        self.assertEqual(
            Status(document.status).task_status[TaskType.EMBEDDING],
            State.PENDING,
        )
        self.assertEqual(
            Status(paragraph.status).task_status[TaskType.EMBEDDING],
            State.PENDING,
        )
        delay_mock.assert_called_once_with(str(document.id), model.id, [State.SUCCESS.value])

    def test_regular_user_cannot_refresh_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Refresh Doc Knowledge',
            desc='Refresh Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Refresh Document',
            char_length=64,
            type=KnowledgeType.BASE,
            meta={},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/refresh",
            {'state_list': [State.SUCCESS.value]},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_refresh_returns_404_for_missing_knowledge_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}/refresh",
            {'state_list': [State.SUCCESS.value]},
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('knowledge.serializers.document.embedding_by_document.delay')
    @patch('knowledge.serializers.document.Fork')
    def test_admin_can_sync_system_resource_document(self, fork_mock, delay_mock):
        fork_instance = MagicMock()
        fork_instance.fork.return_value = MagicMock(status=200, content='# Synced title\n\nSynced content')
        fork_mock.return_value = fork_instance
        model = Model.objects.create(
            id=uuid.uuid7(),
            name='document-sync-model',
            workspace_id='ops',
            model_type='EMBEDDING',
            model_name='test-sync-model',
            provider='test-provider',
            credential='{}',
            user=self.admin_user,
        )
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Sync Document Knowledge',
            desc='Sync Document Description',
            user=self.regular_user,
            folder=self.ops_folder,
            workspace_id='ops',
            type=KnowledgeType.WEB,
            scope=KnowledgeScope.WORKSPACE,
            embedding_model_id=str(model.id),
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Sync Document',
            char_length=0,
            type=KnowledgeType.WEB,
            meta={'source_url': 'https://example.com/doc', 'selector': ''},
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/sync"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        fork_mock.assert_called_once_with('https://example.com/doc', [''])
        delay_mock.assert_called_once_with(str(document.id), str(model.id))

        document.refresh_from_db()
        self.assertGreater(document.char_length, 0)

    def test_regular_user_cannot_sync_system_resource_document(self):
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Forbidden Sync Doc Knowledge',
            desc='Sync Document Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=KnowledgeType.WEB,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name='Forbidden Sync Document',
            char_length=0,
            type=KnowledgeType.WEB,
            meta={'source_url': 'https://example.com/doc', 'selector': ''},
        )
        self.client.force_authenticate(user=self.regular_user, token=get_auth(self.regular_user))

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{knowledge.id}/document/{document.id}/sync"
        )

        self.assertEqual(response.status_code, 403)

    def test_system_resource_document_sync_returns_404_for_missing_knowledge_id(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/system/resource/knowledge/{uuid.uuid7()}/document/{uuid.uuid7()}/sync"
        )

        self.assertEqual(response.status_code, 404)

    def test_create_knowledge(self):
        embedding_model = Model.objects.create(
            id=uuid.uuid7(),
            name='workspace-knowledge-embedding-model',
            workspace_id='default',
            model_type='EMBEDDING',
            model_name='test-embedding-model',
            provider='openai',
            credential='{}',
            user=self.admin_user,
        )

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/default/knowledge/base",
            {
                "name": "Test Knowledge",
                "desc": "Test Description",
                "folder_id": str(self.folder.id),
                "embedding_model_id": str(embedding_model.id),
                "type": KnowledgeType.BASE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['name'], 'Test Knowledge')
        self.assertEqual(data['data']['desc'], 'Test Description')
        self.assertEqual(data['data']['workspace_id'], 'default')
        self.assertTrue(Knowledge.objects.filter(id=data['data']['id'], name='Test Knowledge').exists())

    def test_get_knowledge_list(self):
        kb = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="List Knowledge",
            desc="List Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.get(f"{ADMIN_API_PREFIX}/workspace/default/knowledge")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)
        matched = [item for item in data['data'] if item['id'] == str(kb.id)]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]['name'], 'List Knowledge')
        self.assertEqual(matched[0]['desc'], 'List Description')

    def test_get_knowledge_detail(self):
        kb = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Detail Knowledge",
            desc="Detail Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.get(
            f"{ADMIN_API_PREFIX}/workspace/default/knowledge/{kb.id}"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['id'], str(kb.id))
        self.assertEqual(payload['data']['name'], 'Detail Knowledge')
        self.assertEqual(payload['data']['desc'], 'Detail Description')
        self.assertEqual(payload['data']['workspace_id'], 'default')

    def test_update_knowledge(self):
        kb = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Update Knowledge",
            desc="Update Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.put(
            f"{ADMIN_API_PREFIX}/workspace/default/knowledge/{kb.id}",
            {"name": "Updated Knowledge Name", "desc": "Updated Knowledge Description"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['name'], 'Updated Knowledge Name')
        self.assertEqual(payload['data']['desc'], 'Updated Knowledge Description')

        kb.refresh_from_db()
        self.assertEqual(kb.name, 'Updated Knowledge Name')
        self.assertEqual(kb.desc, 'Updated Knowledge Description')

    def test_delete_knowledge(self):
        kb = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Delete Knowledge",
            desc="Delete Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/default/knowledge/{kb.id}"
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertFalse(Knowledge.objects.filter(id=kb.id).exists())


class KnowledgeFolderIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="knowledge-folder-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_create_folder(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/workspace/default/KNOWLEDGE/folder",
            {"name": "New KB Folder", "workspace_id": "default"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_folder_list(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/workspace/default/KNOWLEDGE/folder")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_delete_folder(self):
        folder = KnowledgeFolder.objects.create(
            id="delete-kb-folder",
            name="Delete KB Folder",
            user=self.admin_user,
            workspace_id="default",
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/workspace/default/KNOWLEDGE/folder/{folder.id}"
        )

        self.assertEqual(response.status_code, 200)
