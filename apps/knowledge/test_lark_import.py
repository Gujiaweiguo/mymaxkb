import json
from types import SimpleNamespace
from unittest.mock import patch

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from knowledge.lark_client import LarkClient
from knowledge.serializers.document import DocumentSerializers
from knowledge.models import Document, Knowledge, KnowledgeFolder, KnowledgeType
from knowledge.views.document import LarkDocumentImportView, LarkDocumentListView
from knowledge.views.knowledge import KnowledgeLarkView, KnowledgeView
from models_provider.models import Model, Status
from system_manage.models import Workspace
from users.models import User


class LarkImportTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-lark",
            username="admin-lark",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-lark", name="workspace-lark"
        )
        self.auth_token = SimpleNamespace(
            role_list=[
                RoleConstants.ADMIN.value.__str__(),
                RoleConstants.WORKSPACE_MANAGE.get_workspace_role()(
                    None, {"workspace_id": self.workspace.id}
                ).__str__(),
                RoleConstants.USER.get_workspace_role()(
                    None, {"workspace_id": self.workspace.id}
                ).__str__(),
            ],
            permission_list=[],
        )
        self.folder = KnowledgeFolder.objects.create(
            id="folder-lark",
            name="folder-lark",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.embedding_model = Model.objects.create(
            name="embedding-model",
            status=Status.SUCCESS,
            model_type="EMBEDDING",
            model_name="embedding-model",
            provider="test",
            credential="{}",
            meta={},
            model_params_form=[],
            workspace_id=self.workspace.id,
            user=self.admin,
        )

    def create_lark_knowledge(self):
        request = self.factory.post(
            f"/workspace/{self.workspace.id}/knowledge/lark/save",
            data={
                "name": "lark-knowledge",
                "folder_id": self.folder.id,
                "desc": "desc",
                "embedding_model_id": str(self.embedding_model.id),
                "app_id": "app-id",
                "app_secret": "app-secret",
                "folder_token": "root-folder",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = KnowledgeLarkView.as_view()(request, workspace_id=self.workspace.id)
        payload = json.loads(response.content)
        return response, payload

    def test_create_lark_knowledge(self):
        response, payload = self.create_lark_knowledge()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["meta"]["app_secret"], "******")
        knowledge = Knowledge.objects.get(id=payload["data"]["id"])
        self.assertEqual(knowledge.type, KnowledgeType.LARK)
        self.assertEqual(knowledge.meta["folder_token"], "root-folder")

    def test_update_lark_knowledge(self):
        _, payload = self.create_lark_knowledge()
        knowledge_id = payload["data"]["id"]
        request = self.factory.put(
            f"/workspace/{self.workspace.id}/knowledge/lark/{knowledge_id}",
            data={
                "name": "lark-knowledge-updated",
                "desc": "desc-2",
                "meta": {
                    "app_id": "app-id-2",
                    "app_secret": "******",
                    "folder_token": "root-folder-2",
                },
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = KnowledgeLarkView.as_view()(
            request, workspace_id=self.workspace.id, knowledge_id=knowledge_id
        )
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["meta"]["app_secret"], "******")
        knowledge = Knowledge.objects.get(id=knowledge_id)
        self.assertEqual(knowledge.name, "lark-knowledge-updated")
        self.assertEqual(knowledge.meta["folder_token"], "root-folder-2")
        self.assertEqual(knowledge.meta["app_secret"], "app-secret")

    def test_get_lark_knowledge_masks_secret(self):
        _, payload = self.create_lark_knowledge()
        knowledge_id = payload["data"]["id"]
        request = self.factory.get(
            f"/workspace/{self.workspace.id}/knowledge/{knowledge_id}"
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = KnowledgeView.Operate.as_view()(
            request, workspace_id=self.workspace.id, knowledge_id=knowledge_id
        )
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["meta"]["app_secret"], "******")

    @patch("knowledge.serializers.document.LarkClient.list_folder_files")
    def test_list_lark_documents_marks_existing(self, mock_list_folder_files):
        _, payload = self.create_lark_knowledge()
        knowledge_id = payload["data"]["id"]
        Document.objects.create(
            knowledge_id=knowledge_id,
            name="Existing Doc",
            char_length=8,
            meta={"token": "doc-existing", "type": "docx", "allow_download": False},
            type=KnowledgeType.LARK,
        )
        mock_list_folder_files.side_effect = lambda token: {
            "root-folder": [
                {"name": "Existing Doc", "token": "doc-existing", "type": "docx"},
                {"name": "Folder", "token": "sub-folder", "type": "folder"},
                {"name": "Sheet", "token": "sheet-1", "type": "sheet"},
            ],
            "sub-folder": [],
        }.get(token, [])
        request = self.factory.post(
            f"/workspace/{self.workspace.id}/knowledge/lark/{knowledge_id}/root-folder/doc_list",
            data={},
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = LarkDocumentListView.as_view()(
            request,
            workspace_id=self.workspace.id,
            knowledge_id=knowledge_id,
            folder_token="root-folder",
        )
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["data"]["files"]), 2)
        self.assertTrue(payload["data"]["files"][0]["is_exist"])

    @patch("knowledge.serializers.document.LarkClient.list_folder_files")
    def test_lark_document_list_rejects_token_outside_root(
        self, mock_list_folder_files
    ):
        _, payload = self.create_lark_knowledge()
        knowledge_id = payload["data"]["id"]
        mock_list_folder_files.side_effect = lambda token: {
            "root-folder": [
                {"name": "Folder", "token": "sub-folder", "type": "folder"},
            ],
            "sub-folder": [],
        }.get(token, [])
        serializer = DocumentSerializers.Create(
            data={"knowledge_id": knowledge_id, "workspace_id": self.workspace.id}
        )
        with self.assertRaises(AppApiException):
            serializer.lark_doc_list("other-folder", with_valid=True)

    @patch("knowledge.serializers.document.LarkClient._get")
    @patch("knowledge.serializers.document.LarkClient.get_tenant_access_token")
    def test_lark_client_lists_paginated_folder_files(
        self, mock_get_tenant_access_token, mock_get
    ):
        mock_get_tenant_access_token.return_value = "tenant-token"
        mock_get.side_effect = [
            {
                "files": [
                    {"name": "Doc 1", "token": "doc-1", "type": "docx"},
                    {"name": "Folder", "token": "sub-folder", "type": "folder"},
                ],
                "has_more": True,
                "next_page_token": "next-page",
            },
            {
                "files": [
                    {"name": "Doc 2", "token": "doc-2", "type": "docx"},
                ],
                "has_more": False,
            },
        ]

        files = LarkClient("app-id", "app-secret").list_folder_files("root-folder")

        self.assertEqual(len(files), 3)
        self.assertEqual(files[0]["token"], "doc-1")
        self.assertEqual(files[2]["token"], "doc-2")
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(
            mock_get.call_args_list[0].kwargs["params"],
            {
                "folder_token": "root-folder",
                "page_size": 200,
            },
        )
        self.assertEqual(
            mock_get.call_args_list[1].kwargs["params"],
            {
                "folder_token": "root-folder",
                "page_size": 200,
                "page_token": "next-page",
            },
        )

    @patch("knowledge.serializers.document.LarkClient.list_folder_files")
    @patch("knowledge.serializers.document.LarkClient.get_document_content")
    def test_import_lark_documents_returns_outcomes(
        self, mock_get_document_content, mock_list_folder_files
    ):
        _, payload = self.create_lark_knowledge()
        knowledge_id = payload["data"]["id"]
        Document.objects.create(
            knowledge_id=knowledge_id,
            name="Existing Doc",
            char_length=8,
            meta={"token": "doc-existing", "type": "docx", "allow_download": False},
            type=KnowledgeType.LARK,
        )
        mock_list_folder_files.side_effect = lambda token: {
            "root-folder": [
                {"name": "Existing Doc", "token": "doc-existing", "type": "docx"},
                {"name": "Doc 1", "token": "doc-1", "type": "docx"},
                {"name": "Folder", "token": "sub-folder", "type": "folder"},
            ],
            "sub-folder": [
                {"name": "Nested Doc", "token": "nested-doc", "type": "docx"},
            ],
        }.get(token, [])
        mock_get_document_content.side_effect = lambda token, file_type: {
            "doc-1": "doc content",
            "nested-doc": "nested doc content",
        }[token]
        request = self.factory.post(
            f"/workspace/{self.workspace.id}/knowledge/lark/{knowledge_id}/import",
            data=[
                {"name": "Doc 1", "token": "doc-1", "type": "docx"},
                {"name": "Doc 1 Duplicate", "token": "doc-1", "type": "docx"},
                {"name": "Existing Doc", "token": "doc-existing", "type": "docx"},
                {"name": "Outside Doc", "token": "outside-doc", "type": "docx"},
                {"name": "Nested Doc", "token": "nested-doc", "type": "docx"},
            ],
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = LarkDocumentImportView.as_view()(
            request, workspace_id=self.workspace.id, knowledge_id=knowledge_id
        )
        payload = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(
            payload["data"]["summary"], {"created": 2, "skipped": 2, "failed": 1}
        )
        outcome_by_token = {
            item["token"]: item
            for item in payload["data"]["items"]
            if item.get("token")
        }
        self.assertEqual(outcome_by_token["doc-1"]["status"], "created")
        self.assertEqual(outcome_by_token["doc-existing"]["reason"], "already_imported")
        self.assertEqual(
            outcome_by_token["outside-doc"]["reason"], "token_outside_configured_root"
        )
        self.assertEqual(
            Document.objects.filter(
                knowledge_id=knowledge_id, type=KnowledgeType.LARK
            ).count(),
            3,
        )
        created_documents = Document.objects.filter(
            knowledge_id=knowledge_id,
            type=KnowledgeType.LARK,
            meta__token__in=["doc-1", "nested-doc"],
        )
        self.assertEqual(created_documents.count(), 2)
        for document in created_documents:
            self.assertFalse(document.meta["allow_download"])
