import json
import uuid_utils.compat as uuid
from unittest.mock import patch

from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, StreamingHttpResponse
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from application.models import Application, ApplicationAccessToken, ApplicationFolder, ApplicationTypeChoices, ApplicationVersion, Chat, ChatRecord
from application.serializers.application import ApplicationOperateSerializer
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from knowledge.models import Document, Knowledge, Paragraph
from maxkb.const import CONFIG
from models_provider.models import Model
from users.models import User


def set_system_user_auth(client: APIClient, user: User):
    token = signing.dumps(
        {
            "username": user.username,
            "id": str(user.id),
            "email": user.email,
            "type": AuthenticationType.SYSTEM_USER.value,
        }
    )
    version, get_key = Cache_Version.TOKEN.value
    cache.set(get_key(token), user, timeout=CONFIG.get_session_timeout(), version=version)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class ApplicationOperateSerializerMediaValidationTests(SimpleTestCase):
    @patch('application.serializers.application.QuerySet')
    def test_speech_to_text_raises_when_stt_disabled(self, mock_queryset):
        application = type('ApplicationStub', (), {
            'stt_model_enable': False,
        })()
        mock_queryset.return_value.filter.return_value.first.return_value = application
        serializer = ApplicationOperateSerializer(
            instance={
                'application_id': str(uuid.uuid7()),
                'workspace_id': 'default',
                'user_id': str(uuid.uuid7()),
            }
        )

        with self.assertRaises(AppApiException) as cm:
            serializer.speech_to_text({'file': object()}, with_valid=False)

        self.assertEqual(cm.exception.code, 500)
        self.assertEqual(str(cm.exception.message), 'Speech recognition is not enabled')

    @patch('application.serializers.application.QuerySet')
    def test_text_to_speech_raises_when_tts_disabled(self, mock_queryset):
        application = type('ApplicationStub', (), {
            'tts_model_enable': False,
        })()
        mock_queryset.return_value.filter.return_value.first.return_value = application
        serializer = ApplicationOperateSerializer(
            instance={
                'application_id': str(uuid.uuid7()),
                'workspace_id': 'default',
                'user_id': str(uuid.uuid7()),
            }
        )

        with self.assertRaises(AppApiException) as cm:
            serializer.text_to_speech({'text': 'hello world'}, with_valid=False)

        self.assertEqual(cm.exception.code, 500)
        self.assertEqual(str(cm.exception.message), 'Speech synthesis is not enabled')

    @patch('application.serializers.application.QuerySet')
    def test_speech_to_text_raises_when_stt_disabled_in_version_mode(self, mock_queryset):
        application_version = type('ApplicationVersionStub', (), {
            'stt_model_enable': False,
        })()
        mock_queryset.return_value.filter.return_value.order_by.return_value.first.return_value = application_version
        serializer = ApplicationOperateSerializer(
            instance={
                'application_id': str(uuid.uuid7()),
                'workspace_id': 'default',
                'user_id': str(uuid.uuid7()),
            }
        )

        with self.assertRaises(AppApiException) as cm:
            serializer.speech_to_text({'file': object()}, debug=False, with_valid=False)

        self.assertEqual(cm.exception.code, 500)
        self.assertEqual(str(cm.exception.message), 'Speech recognition is not enabled')

    @patch('application.serializers.application.QuerySet')
    def test_text_to_speech_raises_when_tts_disabled_in_version_mode(self, mock_queryset):
        application_version = type('ApplicationVersionStub', (), {
            'tts_model_enable': False,
        })()
        mock_queryset.return_value.filter.return_value.order_by.return_value.first.return_value = application_version
        serializer = ApplicationOperateSerializer(
            instance={
                'application_id': str(uuid.uuid7()),
                'workspace_id': 'default',
                'user_id': str(uuid.uuid7()),
            }
        )

        with self.assertRaises(AppApiException) as cm:
            serializer.text_to_speech({'text': 'hello world'}, debug=False, with_valid=False)

        self.assertEqual(cm.exception.code, 500)
        self.assertEqual(str(cm.exception.message), 'Speech synthesis is not enabled')


class ApplicationAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="app-test-admin@example.com",
            phone="",
            nick_name="App Test Admin",
            username="app-test-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id="test-folder",
            name="Test Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        set_system_user_auth(self.client, self.admin_user)

    def test_create_application(self):
        response = self.client.post(
            "/admin/api/workspace/default/application",
            {
                "name": "Test App",
                "desc": "Test Description",
                "folder_id": str(self.folder.id),
                "type": ApplicationTypeChoices.SIMPLE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_application_list(self):
        Application.objects.create(
            id=uuid.uuid7(),
            name="List App",
            desc="List Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.get("/admin/api/workspace/default/application")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_application_detail(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Detail App",
            desc="Detail Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.get(
            f"/admin/api/workspace/default/application/{app.id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["name"], "Detail App")

    def test_update_application(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Update App",
            desc="Update Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.put(
            f"/admin/api/workspace/default/application/{app.id}",
            {"name": "Updated App Name"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_application(self):
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Delete App",
            desc="Delete Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        response = self.client.delete(
            f"/admin/api/workspace/default/application/{app.id}"
        )

        self.assertEqual(response.status_code, 200)


class SystemResourceApplicationAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="system-resource-admin@example.com",
            phone="",
            nick_name="System Resource Admin",
            username="system-resource-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id="system-resource-folder",
            name="System Resource Folder",
            user=self.admin_user,
            workspace_id="default",
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="System Resource App",
            desc="System Resource Description",
            user=self.admin_user,
            folder=self.folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.application_version = ApplicationVersion.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            workspace_id='default',
            name='v1',
            publish_user_id=self.admin_user.id,
            publish_user_name=self.admin_user.username,
            application_name=self.application.name,
            desc=self.application.desc,
            user=self.admin_user,
            type=self.application.type,
            icon=self.application.icon,
            work_flow={},
        )
        self.embedding_model = Model.objects.create(
            id=uuid.uuid7(),
            name='system-resource-embedding-model',
            workspace_id='default',
            model_type='EMBEDDING',
            model_name='test-embedding-model',
            provider='openai',
            credential='{}',
            user=self.admin_user,
        )
        ApplicationAccessToken.objects.create(
            application=self.application,
            access_token="system-resource-token",
        )
        self.chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract="System Resource Chat",
            chat_user_id=str(uuid.uuid7()),
            chat_user_type="ANONYMOUS_USER",
            chat_record_count=1,
            asker={"username": "visitor"},
        )
        self.chat_record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text="hello",
            answer_text="world",
            details={"start-node": {"type": "start-node"}},
            index=1,
        )
        self.knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='system-resource-knowledge',
            user=self.admin_user,
            workspace_id='default',
            embedding_model_id=str(self.embedding_model.id),
        )
        self.document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=self.knowledge,
            name='system-resource-document',
            char_length=0,
        )
        set_system_user_auth(self.client, self.admin_user)

    def test_system_resource_get_access_token(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/access_token"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(str(data["data"]["application_id"]), str(self.application.id))
        self.assertTrue(data["data"]["access_token"])

    def test_system_resource_get_all_applications(self):
        response = self.client.get("/admin/api/system/resource/application")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["id"], str(self.application.id))

    def test_system_resource_get_application_versions(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/application_version"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1)
        self.assertEqual(response.json()['data'][0]['id'], str(self.application_version.id))

    def test_system_resource_get_application_version_detail(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/application_version/{self.application_version.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['id'], str(self.application_version.id))
        self.assertEqual(response.json()['data']['name'], 'v1')

    def test_system_resource_put_application_version(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/application_version/{self.application_version.id}",
            {'name': 'release-1'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['name'], 'release-1')
        self.application_version.refresh_from_db()
        self.assertEqual(self.application_version.name, 'release-1')

    def test_system_resource_put_access_token(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/access_token",
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["data"]["is_active"])

        token = ApplicationAccessToken.objects.get(application_id=self.application.id)
        self.assertFalse(token.is_active)

    def test_system_resource_open_application(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/open"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIsInstance(data, str)
        self.assertTrue(data)

    @patch('application.views.system_resource_application.ApplicationOperateSerializer.play_demo_text')
    def test_system_resource_play_demo_text(self, mock_play_demo_text):
        mock_play_demo_text.return_value = b'audio-bytes'
        tts_model_id = str(uuid.uuid7())

        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/play_demo_text",
            {'tts_model_id': tts_model_id},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'audio/mp3')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="abc.mp3"')
        self.assertEqual(response.content, b'audio-bytes')
        mock_play_demo_text.assert_called_once_with({'tts_model_id': tts_model_id})

    @patch('application.views.system_resource_application.ApplicationOperateSerializer.text_to_speech')
    def test_system_resource_text_to_speech(self, mock_text_to_speech):
        mock_text_to_speech.return_value = b'audio-bytes'

        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/text_to_speech",
            {'text': 'hello world'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'audio/mp3')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="abc.mp3"')
        self.assertEqual(response.content, b'audio-bytes')
        mock_text_to_speech.assert_called_once_with({'text': 'hello world'})

    @patch('application.views.system_resource_application.ApplicationOperateSerializer.speech_to_text')
    def test_system_resource_speech_to_text(self, mock_speech_to_text):
        mock_speech_to_text.return_value = 'hello world'
        audio_file = SimpleUploadedFile('speech.mp3', b'audio-bytes', content_type='audio/mp3')

        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/speech_to_text",
            {'file': audio_file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], 'hello world')
        mock_speech_to_text.assert_called_once()
        self.assertEqual(mock_speech_to_text.call_args[0][0]['file'].name, 'speech.mp3')

    @patch('application.views.system_resource_application.ApplicationOperateSerializer.get_mcp_servers')
    def test_system_resource_get_mcp_tools(self, mock_get_mcp_servers):
        mock_get_mcp_servers.return_value = [
            {
                'server': 'test',
                'name': 'tool-1',
                'description': 'desc',
                'args_schema': {},
            }
        ]

        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/mcp_tools",
            {
                'mcp_servers': '{"test": {"url": "https://example.com/sse", "transport": "sse"}}',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'][0]['name'], 'tool-1')
        mock_get_mcp_servers.assert_called_once_with(
            {'mcp_servers': '{"test": {"url": "https://example.com/sse", "transport": "sse"}}'}
        )

    @patch("application.views.system_resource_application.PromptGenerateSerializer.generate_prompt")
    def test_system_resource_prompt_generate(self, mock_generate_prompt):
        mock_generate_prompt.return_value = StreamingHttpResponse(
            [b'data: {"content": "ok"}\n\n'],
            content_type="text/event-stream;charset=utf-8",
        )

        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/model/test-model/prompt_generate",
            {
                "messages": [{"role": "user", "content": "hello"}],
                "prompt": "{userInput}",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream;charset=utf-8")
        self.assertEqual(b"".join(response.streaming_content), b'data: {"content": "ok"}\n\n')
        mock_generate_prompt.assert_called_once_with(
            instance={
                "messages": [{"role": "user", "content": "hello"}],
                "prompt": "{userInput}",
            }
        )

    def test_system_resource_get_setting(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/setting"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(str(data["application_id"]), str(self.application.id))
        self.assertEqual(data["access_token"], "system-resource-token")

    def test_system_resource_put_setting(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/setting",
            {"show_source": False, "show_exec": True, "language": "en-US"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertFalse(data["show_source"])
        self.assertTrue(data["show_exec"])
        self.assertEqual(data["language"], "en-US")

        token = ApplicationAccessToken.objects.get(application_id=self.application.id)
        self.assertFalse(token.show_source)
        self.assertTrue(token.show_exec)
        self.assertEqual(token.language, "en-US")

    def test_system_resource_put_clear_strategy(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}",
            {"clean_time": 30, "file_clean_time": 7},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["clean_time"], 30)
        self.assertEqual(data["file_clean_time"], 7)

        self.application.refresh_from_db()
        self.assertEqual(self.application.clean_time, 30)
        self.assertEqual(self.application.file_clean_time, 7)

    def test_system_resource_export_application(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/export"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])

    def test_system_resource_get_application_detail(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["id"], str(self.application.id))
        self.assertEqual(response.json()["data"]["name"], self.application.name)

    def test_system_resource_put_application_detail(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}",
            {"name": "Updated System Resource App", "desc": "Updated Description"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["name"], "Updated System Resource App")
        self.assertEqual(response.json()["data"]["desc"], "Updated Description")

        self.application.refresh_from_db()
        self.assertEqual(self.application.name, "Updated System Resource App")
        self.assertEqual(self.application.desc, "Updated Description")

    def test_system_resource_publish_application(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/publish",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["data"]["is_publish"])

        self.application.refresh_from_db()
        self.assertTrue(self.application.is_publish)
        self.assertIsNotNone(self.application.publish_time)

    def test_system_resource_application_stats_endpoints(self):
        params = {
            "start_time": "2026-01-01",
            "end_time": "2026-01-07",
        }

        stats_response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/application_stats",
            params,
        )
        token_usage_response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/application_token_usage",
            params,
        )
        top_questions_response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/top_questions",
            params,
        )

        self.assertEqual(stats_response.status_code, 200)
        self.assertIsInstance(stats_response.json()["data"], list)
        self.assertEqual(token_usage_response.status_code, 200)
        self.assertIsInstance(token_usage_response.json()["data"], list)
        self.assertEqual(top_questions_response.status_code, 200)
        self.assertIsInstance(top_questions_response.json()["data"], list)

    def test_system_resource_delete_application(self):
        response = self.client.delete(
            f"/admin/api/system/resource/application/{self.application.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(id=self.application.id).exists())

    def test_system_resource_get_chat_log_page(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/chat/1/20",
            {
                "start_time": "2026-01-01",
                "end_time": "2026-12-31",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["total"], 1)
        self.assertEqual(response.json()["data"]["records"][0]["id"], str(self.chat.id))

    def test_system_resource_export_chat_log(self):
        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/chat/export?start_time=2026-01-01&end_time=2026-01-07",
            {"select_ids": [str(self.chat.id)]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_system_resource_get_chat_record_page(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/chat/{self.chat.id}/chat_record/1/20",
            {"order_asc": True},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["total"], 1)
        self.assertEqual(response.json()["data"]["records"][0]["id"], str(self.chat_record.id))

    def test_system_resource_get_chat_record_detail(self):
        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/chat/{self.chat.id}/chat_record/{self.chat_record.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["id"], str(self.chat_record.id))
        self.assertEqual(response.json()["data"]["problem_text"], self.chat_record.problem_text)

    @patch('application.serializers.application_chat_record.embedding_by_paragraph_list')
    def test_system_resource_add_chat_log_to_knowledge(self, embedding_by_paragraph_list_mock):
        response = self.client.post(
            f"/admin/api/system/resource/application/{self.application.id}/add_knowledge",
            {
                "knowledge_id": str(self.knowledge.id),
                "document_id": str(self.document.id),
                "chat_ids": [str(self.chat.id)],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["data"])
        self.assertTrue(
            QuerySet(Paragraph).filter(knowledge_id=self.knowledge.id, document_id=self.document.id).exists()
        )
        embedding_by_paragraph_list_mock.assert_called_once()

    def test_system_resource_get_chat_record_improve_list(self):
        paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            document=self.document,
            knowledge=self.knowledge,
            content='improved answer',
            title='hello',
            position=1,
        )
        self.chat_record.improve_paragraph_id_list = [paragraph.id]
        self.chat_record.save(update_fields=['improve_paragraph_id_list'])

        response = self.client.get(
            f"/admin/api/system/resource/application/{self.application.id}/chat/{self.chat.id}/chat_record/{self.chat_record.id}/improve"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["data"][0]["id"], str(paragraph.id))

    def test_system_resource_delete_chat_record_improve(self):
        paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            document=self.document,
            knowledge=self.knowledge,
            content='improved answer',
            title='hello',
            position=1,
        )
        self.chat_record.improve_paragraph_id_list = [paragraph.id]
        self.chat_record.save(update_fields=['improve_paragraph_id_list'])

        response = self.client.delete(
            f"/admin/api/system/resource/application/{self.application.id}/chat/{self.chat.id}/chat_record/{self.chat_record.id}/knowledge/{self.knowledge.id}/document/{self.document.id}/paragraph/{paragraph.id}/improve"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuerySet(Paragraph).filter(id=paragraph.id).exists())
        self.chat_record.refresh_from_db()
        self.assertEqual(self.chat_record.improve_paragraph_id_list, [])

    def test_system_resource_put_chat_record_improve(self):
        response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/chat/{self.chat.id}/chat_record/{self.chat_record.id}/knowledge/{self.knowledge.id}/document/{self.document.id}/improve",
            {
                'title': 'hello',
                'content': 'annotated answer',
                'problem_text': 'hello',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.chat_record.refresh_from_db()
        self.assertEqual(len(self.chat_record.improve_paragraph_id_list), 1)
        paragraph_id = self.chat_record.improve_paragraph_id_list[0]
        paragraph = QuerySet(Paragraph).filter(id=paragraph_id).first()
        self.assertIsNotNone(paragraph)
        self.assertEqual(paragraph.document_id, self.document.id)
        self.assertEqual(paragraph.knowledge_id, self.knowledge.id)
        self.assertEqual(paragraph.content, 'annotated answer')


class ApplicationFolderIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="folder-test-admin@example.com",
            phone="",
            nick_name="Folder Test Admin",
            username="folder-test-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        set_system_user_auth(self.client, self.admin_user)

    def test_create_folder(self):
        response = self.client.post(
            "/admin/api/workspace/default/APPLICATION/folder",
            {"name": "New Folder", "workspace_id": "default"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_folder_list(self):
        response = self.client.get("/admin/api/workspace/default/APPLICATION/folder")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_delete_folder(self):
        folder = ApplicationFolder.objects.create(
            id="delete-folder",
            name="Delete Folder",
            user=self.admin_user,
            workspace_id="default",
        )

        response = self.client.delete(
            f"/admin/api/workspace/default/APPLICATION/folder/{folder.id}"
        )

        self.assertEqual(response.status_code, 200)
