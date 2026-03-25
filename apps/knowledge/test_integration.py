import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType, KnowledgeScope
from users.models import User


class KnowledgeAPIIntegrationTests(TestCase):
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
        self.folder = KnowledgeFolder.objects.create(
            id="kb-folder",
            name="KB Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_create_knowledge(self):
        response = self.client.post(
            "/api/knowledge/knowledge",
            {
                "name": "Test Knowledge",
                "desc": "Test Description",
                "folder_id": str(self.folder.id),
                "type": KnowledgeType.BASE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_knowledge_list(self):
        Knowledge.objects.create(
            id=uuid.uuid7(),
            name="List Knowledge",
            desc="List Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        response = self.client.get("/api/knowledge/knowledge")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

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
            f"/api/knowledge/knowledge/{kb.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["name"], "Detail Knowledge")

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
            f"/api/knowledge/knowledge/{kb.id}",
            {"name": "Updated Knowledge Name"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

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
            f"/api/knowledge/knowledge/{kb.id}"
        )

        self.assertEqual(response.status_code, 200)


class KnowledgeFolderIntegrationTests(TestCase):
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

    def test_create_folder(self):
        response = self.client.post(
            "/api/knowledge/folder",
            {"name": "New KB Folder", "workspace_id": "default"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_folder_list(self):
        response = self.client.get("/api/knowledge/folder")

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
            f"/api/knowledge/folder/{folder.id}"
        )

        self.assertEqual(response.status_code, 200)
