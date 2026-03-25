import json
import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_chat import Chat, ChatRecord, ChatUserType
from common.utils.common import password_encrypt
from users.models import User


class ChatAPIIntegrationTests(TestCase):
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
        self.folder = ApplicationFolder.objects.create(
            id="chat-folder",
            name="Chat Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="Chat App",
            desc="Chat Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_open_chat(self):
        response = self.client.post(
            "/api/chat/open",
            {"application_id": str(self.application.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_historical_conversations(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Test Chat",
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        response = self.client.get(
            "/api/chat/historical_conversation",
            {"application_id": str(self.application.id)},
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_historical_conversation_page(self):
        response = self.client.get(
            f"/api/chat/historical_conversation/1/20",
            {"application_id": str(self.application.id)},
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_historical_conversation(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Delete Chat",
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        response = self.client.delete(
            f"/api/chat/historical_conversation/{chat.id}"
        )

        self.assertEqual(response.status_code, 200)


class ChatRecordIntegrationTests(TestCase):
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
        self.folder = ApplicationFolder.objects.create(
            id="record-folder",
            name="Record Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="Record App",
            desc="Record Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Test Chat",
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )
        self.client.force_authenticate(user=self.admin_user, token="test-token")

    def test_get_chat_records(self):
        ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text="Hello",
            answer_text="Hi there!",
        )

        response = self.client.get(
            f"/api/chat/historical_conversation_record/{self.chat.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_chat_record_page(self):
        response = self.client.get(
            f"/api/chat/historical_conversation_record/{self.chat.id}/1/20"
        )

        self.assertEqual(response.status_code, 200)

    def test_vote_chat_record(self):
        record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text="Question",
            answer_text="Answer",
        )

        response = self.client.post(
            f"/api/chat/vote/chat/{self.chat.id}/chat_record/{record.id}",
            {"vote_status": "0", "vote_reason": "accurate"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_clear_historical_conversations(self):
        response = self.client.delete(
            "/api/chat/historical_conversation/clear",
            {"application_id": str(self.application.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
