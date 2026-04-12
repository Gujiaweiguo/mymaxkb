import json
import uuid_utils.compat as uuid
from unittest.mock import patch
from django.core import signing
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationAccessToken, ApplicationFolder, ApplicationTypeChoices
from application.models.application_chat import Chat, ChatRecord, ChatUserType
from application.models.application_chat import ChatSourceChoices
from common.result import result
from common.utils.common import password_encrypt
from users.models import User


CHAT_API_PREFIX = '/chat/api'


def authenticate_chat_client(client: APIClient, access_token: str) -> str:
    response = client.post(
        f'{CHAT_API_PREFIX}/auth/anonymous',
        {'access_token': access_token},
        format='json',
    )
    payload = json.loads(response.content)
    token = payload['data']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    details = signing.loads(token)
    return details['chat_user_id']


class ChatAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="chat-int-admin",
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
        self.access = ApplicationAccessToken.objects.create(
            application=self.application,
            access_token='chat-api-token',
            is_active=True,
        )
        self.chat_user_id = authenticate_chat_client(self.client, self.access.access_token)

    def test_open_chat(self):
        response = self.client.get(
            f'{CHAT_API_PREFIX}/open',
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_historical_conversations(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Test Chat",
            chat_user_id=self.chat_user_id,
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        response = self.client.get(
            f'{CHAT_API_PREFIX}/historical_conversation',
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_historical_conversation_page(self):
        response = self.client.get(
            f'{CHAT_API_PREFIX}/historical_conversation/1/20',
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_historical_conversation(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Delete Chat",
            chat_user_id=self.chat_user_id,
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        response = self.client.delete(
            f'{CHAT_API_PREFIX}/historical_conversation/{chat.id}'
        )

        self.assertEqual(response.status_code, 200)

    def test_edit_historical_conversation_abstract(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Before Update",
            chat_user_id=self.chat_user_id,
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        response = self.client.put(
            f'{CHAT_API_PREFIX}/historical_conversation/{chat.id}',
            {'abstract': 'Updated Abstract'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertTrue(payload['data'])

        chat.refresh_from_db()
        self.assertEqual(chat.abstract, 'Updated Abstract')

    def test_chat_message_uses_online_source_for_anonymous_user(self):
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Message Chat",
            chat_user_id=self.chat_user_id,
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        with patch('chat.views.chat.ChatSerializers') as chat_serializers_cls:
            chat_serializer_instance = chat_serializers_cls.return_value
            chat_serializer_instance.chat.return_value = result.success({"ok": True})

            response = self.client.post(
                f'{CHAT_API_PREFIX}/chat_message/{chat.id}',
                {},
                format='json',
            )

        self.assertEqual(response.status_code, 200)
        chat_serializers_cls.assert_called_once()
        serializer_data = chat_serializers_cls.call_args.kwargs['data']
        self.assertEqual(serializer_data['chat_id'], str(chat.id))
        self.assertEqual(serializer_data['chat_user_id'], str(self.chat_user_id))
        self.assertEqual(str(serializer_data['application_id']), str(self.application.id))
        self.assertEqual(serializer_data['source']['type'], ChatSourceChoices.ONLINE.value)


class ChatRecordIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username="chat-record-admin",
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
        self.access = ApplicationAccessToken.objects.create(
            application=self.application,
            access_token='chat-record-token',
            is_active=True,
        )
        self.chat_user_id = authenticate_chat_client(self.client, self.access.access_token)
        self.chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="Test Chat",
            chat_user_id=self.chat_user_id,
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

    def test_get_chat_records(self):
        ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text="Hello",
            answer_text="Hi there!",
            index=0,
        )

        response = self.client.get(
            f'{CHAT_API_PREFIX}/historical_conversation_record/{self.chat.id}'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_chat_record_page(self):
        response = self.client.get(
            f'{CHAT_API_PREFIX}/historical_conversation_record/{self.chat.id}/1/20'
        )

        self.assertEqual(response.status_code, 200)

    def test_vote_chat_record(self):
        record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text="Question",
            answer_text="Answer",
            index=0,
        )

        response = self.client.post(
            f'{CHAT_API_PREFIX}/vote/chat/{self.chat.id}/chat_record/{record.id}',
            {"vote_status": "0", "vote_reason": "accurate"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_clear_historical_conversations(self):
        response = self.client.delete(
            f'{CHAT_API_PREFIX}/historical_conversation/clear',
            format="json",
        )

        self.assertEqual(response.status_code, 200)
