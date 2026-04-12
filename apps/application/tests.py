import uuid_utils.compat as uuid
import importlib.util
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_chat import Chat, ChatRecord, ChatSourceChoices, VoteChoices
from application.models.application_api_key import ApplicationApiKey
from application.serializers.application_chat import (
    ApplicationChatQuerySerializers,
    ChatCountSerializer,
    get_source_display,
)
from application.serializers.application_api_key import ApplicationKeySerializer
from application.serializers.system_resource_application import (
    SystemResourceApplicationQuerySerializer,
)
from common.utils.common import password_encrypt
from system_manage.models import Workspace
from users.models import User


class SystemResourceApplicationQueryTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_workspace(self, workspace_id: str, name: str):
        workspace, _ = Workspace.objects.get_or_create(
            id=workspace_id,
            defaults={"name": name},
        )
        return workspace

    def create_folder(self, folder_id: str, workspace_id: str, user):
        return ApplicationFolder.objects.create(
            id=folder_id,
            name=f"{folder_id}-folder",
            user=user,
            workspace_id=workspace_id,
        )

    def create_application(self, name: str, workspace_id: str, user, folder):
        return Application.objects.create(
            id=uuid.uuid7(),
            name=name,
            desc=f"{name}-desc",
            user=user,
            folder=folder,
            workspace_id=workspace_id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_page_filters_applications_by_workspace_ids(self):
        user = self.create_user("resource-admin")
        self.create_workspace("default", "default")
        self.create_workspace("workspace-a", "workspace-a")
        self.create_workspace("workspace-b", "workspace-b")
        folder_a = self.create_folder("folder-a", "workspace-a", user)
        folder_b = self.create_folder("folder-b", "workspace-b", user)
        app_a = self.create_application("app-a", "workspace-a", user, folder_a)
        self.create_application("app-b", "workspace-b", user, folder_b)

        page = SystemResourceApplicationQuerySerializer(
            data={"workspace_ids": '["workspace-a"]'}
        ).page(1, 20)

        self.assertEqual(page["total"], 1)
        self.assertEqual(page["records"][0]["id"], app_a.id)
        self.assertEqual(page["records"][0]["workspace_id"], "workspace-a")


class ApplicationModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_application_creation(self):
        user = self.create_user("app-creator")
        folder = ApplicationFolder.objects.create(
            id="test-folder",
            name="Test Folder",
            user=user,
            workspace_id="default",
        )
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Test App",
            desc="Test Description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(app.name, "Test App")
        self.assertEqual(app.type, ApplicationTypeChoices.SIMPLE)
        self.assertEqual(app.workspace_id, "default")

    def test_application_str_representation(self):
        user = self.create_user("str-user")
        folder = ApplicationFolder.objects.create(
            id="str-folder",
            name="Str Folder",
            user=user,
            workspace_id="default",
        )
        app = Application.objects.create(
            id=uuid.uuid7(),
            name="Str App",
            desc="Desc",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(str(app), "Str App")


class ApplicationFolderModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_folder_creation(self):
        user = self.create_user("folder-user")
        folder = ApplicationFolder.objects.create(
            id="new-folder",
            name="New Folder",
            user=user,
            workspace_id="default",
        )

        self.assertEqual(folder.name, "New Folder")
        self.assertEqual(folder.user, user)

    def test_folder_with_applications(self):
        user = self.create_user("folder-app-user")
        folder = ApplicationFolder.objects.create(
            id="app-folder",
            name="App Folder",
            user=user,
            workspace_id="default",
        )
        Application.objects.create(
            id=uuid.uuid7(),
            name="App 1",
            desc="Desc 1",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        Application.objects.create(
            id=uuid.uuid7(),
            name="App 2",
            desc="Desc 2",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

        self.assertEqual(folder.application_set.count(), 2)


class ApplicationApiKeyMaskingTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_application(self):
        user = self.create_user("app-key-user")
        folder = ApplicationFolder.objects.create(
            id="app-key-folder",
            name="App Key Folder",
            user=user,
            workspace_id="default",
        )
        return Application.objects.create(
            id=uuid.uuid7(),
            name="App Key App",
            desc="App key description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_generate_returns_full_secret_key_once(self):
        application = self.create_application()

        result = ApplicationKeySerializer(data={"application_id": application.id}).generate()

        self.assertTrue(result["secret_key"].startswith("agent-"))
        self.assertNotIn("******", result["secret_key"])
        self.assertEqual(len(result["secret_key"]), len("agent-") + 32)

    def test_page_masks_application_secret_key_after_creation(self):
        application = self.create_application()
        created = ApplicationKeySerializer(data={"application_id": application.id}).generate()

        page = ApplicationKeySerializer(data={"application_id": application.id}).page(1, 20)

        self.assertEqual(page["total"], 1)
        record = page["records"][0]
        self.assertEqual(record["id"], created["id"])
        self.assertNotEqual(record["secret_key"], created["secret_key"])
        self.assertIn("******", record["secret_key"])
        self.assertEqual(record["secret_key"], f"{created['secret_key'][:8]}******{created['secret_key'][-4:]}")

        stored = ApplicationApiKey.objects.get(id=created["id"])
        self.assertEqual(stored.secret_key, created["secret_key"])


class _PipelineStepSerializer(serializers.Serializer):
    problem_text = serializers.CharField(required=True)


class _CollectingStep(IBaseChatPipelineStep):
    def get_step_serializer(self, manage):
        return _PipelineStepSerializer

    def _run(self, manage):
        problem_text = self.context['step_args']['problem_text']
        manage.context.setdefault('executed_steps', []).append(problem_text)
        self.context['detail'] = {
            'step_type': 'collect',
            'type': 'question-node',
            'answer': f'handled:{problem_text}',
        }

    def get_details(self, manage, **kwargs):
        return self.context.get('detail')


class _SecondCollectingStep(_CollectingStep):
    def _run(self, manage):
        super()._run(manage)
        self.context['detail'] = {
            'step_type': 'search_step',
            'type': 'search-dataset-node',
            'paragraph_list': [{'title': 'Doc', 'content': 'Paragraph'}],
        }


class PipelineManageTests(TestCase):
    def test_run_merges_context_and_executes_steps_in_order(self):
        manage = PipelineManage.builder().append_step(_CollectingStep).append_step(_SecondCollectingStep).build()

        manage.run({'problem_text': 'How are you?'})

        self.assertEqual(manage.context['problem_text'], 'How are you?')
        self.assertEqual(manage.context['executed_steps'], ['How are you?', 'How are you?'])
        self.assertEqual(len(manage.run_step_list), 2)
        self.assertIn('start_time', manage.context)

    def test_get_details_aggregates_step_details_by_step_type(self):
        manage = PipelineManage.builder().append_step(_CollectingStep).append_step(_SecondCollectingStep).build()

        manage.run({'problem_text': 'What changed?'})

        details = manage.get_details()

        self.assertEqual(details['collect']['answer'], 'handled:What changed?')
        self.assertEqual(details['search_step']['paragraph_list'][0]['title'], 'Doc')


class ApplicationChatSerializerUtilityTests(TestCase):
    def test_get_source_display_returns_dash_for_missing_source(self):
        self.assertEqual(get_source_display(None), '-')
        self.assertEqual(get_source_display({}), '-')

    def test_get_source_display_maps_known_source_types(self):
        self.assertEqual(
            get_source_display({'type': ChatSourceChoices.ONLINE.value}),
            'Online Usage',
        )
        self.assertEqual(
            get_source_display({'type': ChatSourceChoices.DINGTALK.value}),
            'DingTalk',
        )

    def test_to_row_formats_details_feedback_and_source(self):
        row = ApplicationChatQuerySerializers.to_row(
            {
                'chat_id': uuid.uuid7(),
                'abstract': 'Conversation summary',
                'problem_text': 'Original problem',
                'answer_text': 'Resolved answer',
                'vote_status': '0',
                'vote_reason': 'accurate',
                'vote_other_content': 'n/a',
                'details': {
                    'question-step': {
                        'type': 'question-node',
                        'answer': 'Refined question',
                    },
                    'search_step': {
                        'step_type': 'search_step',
                        'paragraph_list': [{'title': 'Reference', 'content': 'Reference content'}],
                    },
                },
                'improve_paragraph_list': [{'title': 'Improved', 'content': 'Improved content'}],
                'asker': {'username': 'qa-user'},
                'message_tokens': 12,
                'answer_tokens': 20,
                'ip_address': '127.0.0.1',
                'source': {'type': ChatSourceChoices.API_CALL.value},
                'run_time': 1.5,
                'create_time': timezone.now(),
            }
        )

        self.assertEqual(row[0].count('-'), 4)
        self.assertEqual(row[2], 'Original problem')
        self.assertEqual(row[3], 'Refined question')
        self.assertEqual(row[5], '赞同')
        self.assertEqual(row[6], 'accurate')
        self.assertEqual(row[8], '1')
        self.assertIn('Reference:\nReference content', row[9])
        self.assertEqual(row[10], 'Improved\nImproved content')
        self.assertEqual(row[14], 'API Call')
        self.assertEqual(row[15], 1.5)


class ChatCountSerializerTests(TestCase):
    def create_chat(self):
        user = User.objects.create(
            id=uuid.uuid7(),
            email='chat-count@example.com',
            phone='',
            nick_name='chat-count-nick',
            username='chat-count-user',
            password=password_encrypt('Secret1!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        folder = ApplicationFolder.objects.create(
            id='chat-count-folder',
            name='Chat Count Folder',
            user=user,
            workspace_id='default',
        )
        application = Application.objects.create(
            id=uuid.uuid7(),
            name='Chat Count App',
            desc='Chat count description',
            user=user,
            folder=folder,
            workspace_id='default',
            type=ApplicationTypeChoices.SIMPLE,
            icon='./favicon.ico',
        )
        return Chat.objects.create(
            id=uuid.uuid7(),
            application=application,
            abstract='Count me',
            chat_user_id='anonymous',
            source={'type': ChatSourceChoices.ONLINE.value},
        )

    def test_update_chat_uses_aggregated_counts_with_zero_fallback(self):
        chat = self.create_chat()
        ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=chat,
            vote_status=VoteChoices.STAR,
            vote_reason='accurate',
            problem_text='Problem 1',
            answer_text='Answer 1',
            improve_paragraph_id_list=[uuid.uuid7(), uuid.uuid7()],
            index=1,
            source={'type': ChatSourceChoices.ONLINE.value},
        )
        ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=chat,
            vote_status=VoteChoices.TRAMPLE,
            vote_reason='inaccurate',
            problem_text='Problem 2',
            answer_text='Answer 2',
            improve_paragraph_id_list=[],
            index=2,
            source={'type': ChatSourceChoices.API_CALL.value},
        )

        serializer = ChatCountSerializer(data={'chat_id': chat.id})

        serializer.update_chat()
        chat.refresh_from_db()

        self.assertEqual(chat.star_num, 1)
        self.assertEqual(chat.trample_num, 1)
        self.assertEqual(chat.chat_record_count, 2)
        self.assertEqual(chat.mark_sum, 2)


_platform_test_path = Path(__file__).with_name('tests').joinpath('test_platform_integration.py')
if _platform_test_path.exists():
    _platform_spec = importlib.util.spec_from_file_location(
        'application.tests.test_platform_integration',
        _platform_test_path,
    )
    if _platform_spec and _platform_spec.loader:
        test_platform_integration = importlib.util.module_from_spec(_platform_spec)
        _platform_spec.loader.exec_module(test_platform_integration)
