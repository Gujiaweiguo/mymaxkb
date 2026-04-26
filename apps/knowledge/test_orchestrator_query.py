# pyright: reportAttributeAccessIssue=false, reportIndexIssue=false, reportImplicitRelativeImport=false, reportUninitializedInstanceVariable=false, reportArgumentType=false

import uuid_utils.compat as uuid
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.http import HttpResponse
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from maxkb.test_runner import MaxKBDiscoverRunner
from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.models import Application, ApplicationFolder, ApplicationTypeChoices, ApplicationVersion, Chat
from application.models.application_api_key import ApplicationApiKey
from common.utils.common import password_encrypt
from knowledge.models import Document, Knowledge, Paragraph
from system_manage.models import Workspace
from system_manage.models.resource_mapping import ResourceMapping
from users.models import User

from knowledge.services.orchestrator_session import get_session_cache_key


class OrchestratorQueryContractTests(SimpleTestCase):
    client: APIClient
    url: str = ''
    error_codes: set[str] = set()

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/knowledge/query'
        self.error_codes = {
            'INVALID_REQUEST',
            'UNAUTHORIZED',
            'SESSION_MISMATCH',
            'KNOWLEDGE_SCOPE_INVALID',
            'INTERNAL_ERROR',
        }

    def test_query_route_registered(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertIsInstance(response, HttpResponse)

        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_invalid_request_returns_structured_error(self):
        response = self.client.post(self.url, {}, format='json')  # pyright: ignore[reportAssignmentType]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_code'], 'INVALID_REQUEST')
        self.assertIn('question', response.json()['message'])

    def test_preview_path_excludes_answer_fields(self):
        mock_app = type('MockApp', (), {'id': '00000000-0000-0000-0000-000000000000', 'knowledge_setting': {}})()
        mock_rm_qs = MagicMock()
        mock_rm_qs.filter.return_value = []
        with patch(
            'knowledge.views.orchestrator_query.OrchestratorQueryView._authenticate_application',
            return_value=(object(), mock_app),
        ), patch(
            'knowledge.views.orchestrator_query.ResourceMapping.objects',
            mock_rm_qs,
        ):
            response = self.client.post(
                self.url,
                {
                    'question': 'What can I configure?',
                    'params': {'_param_preview': True},
                },
                format='json',
            )  # pyright: ignore[reportAssignmentType]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json().keys()), {'param_schema'})

    def test_error_codes_are_stable_set(self):
        response = self.client.post(self.url, {}, format='json')  # pyright: ignore[reportAssignmentType]

        self.assertIn(response.json()['error_code'], self.error_codes)

    def test_runner_expands_apps_prefixed_labels_to_test_modules(self):
        labels = MaxKBDiscoverRunner._expand_test_labels(['apps.application', 'apps.knowledge'])

        self.assertIn('application.tests', labels)
        self.assertIn('application.test_integration', labels)
        self.assertIn('knowledge.tests', labels)
        self.assertIn('knowledge.test_orchestrator_query', labels)
        self.assertNotIn('apps.application.models', labels)
        self.assertNotIn('apps.knowledge.models', labels)


class OrchestratorQuerySessionTestsMixin:
    client: APIClient
    url: str
    application: Application
    api_key: ApplicationApiKey

    def setUp(self):
        super().setUp()
        cache.clear()
        self.client = APIClient()
        self.url = '/api/knowledge/query'
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='orchestrator-query@test.local',
            phone='',
            nick_name='orchestrator-query',
            username='orchestrator-query',
            password=password_encrypt('Secret1!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id='workspace-orchestrator-query',
            name='workspace-orchestrator-query',
        )
        self.folder = ApplicationFolder.objects.create(
            id='folder-orchestrator-query',
            name='folder-orchestrator-query',
            workspace_id=self.workspace.id,
            user=self.user,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='orchestrator-query-app',
            desc='orchestrator-query-app',
            user=self.user,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
        )
        self.api_key = ApplicationApiKey.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            workspace_id=self.workspace.id,
            secret_key='agent-orchestrator-query-secret',
            is_active=True,
            is_permanent=True,
        )
        self.application_version = ApplicationVersion.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            workspace_id=self.workspace.id,
            name='v1',
            publish_user_id=self.user.id,
            publish_user_name=self.user.username,
            application_name=self.application.name,
            desc=self.application.desc,
            user=self.user,
            type=self.application.type,
            icon=self.application.icon,
            knowledge_setting=self.application.knowledge_setting,
            model_setting={},
            work_flow={},
        )

    def _auth_headers(self, secret_key: str | None = None) -> dict[str, str]:
        return {'HTTP_AUTHORIZATION': f'Bearer {secret_key or self.api_key.secret_key}'}

    def _post(self, payload: dict[str, object], secret_key: str | None = None):
        self.client.credentials(**self._auth_headers(secret_key))
        return self.client.post(self.url, payload, format='json')

    def _payload(self, **overrides):
        payload = {
            'question': 'How do I bind a session?',
            'session_id': 'session-001',
            'context': {
                'user_id': 'user-1',
                'role_code': 'developer',
                'project_id': 'project-1',
                'source': 'orchestrator',
            },
        }
        payload.update(overrides)
        return payload


class OrchestratorQuerySessionTests(OrchestratorQuerySessionTestsMixin, TestCase):
    @staticmethod
    def _fake_execute_block(answer: str):
        def _execute_block(
            step,
            message_list,
            chat_id,
            problem_text,
            post_response_handler,
            chat_model,
            paragraph_list,
            manage,
            padding_problem_text,
            chat_user_id,
            chat_user_type,
            no_references_setting,
            model_setting,
            mcp_tool_ids,
            mcp_servers,
            mcp_source,
            tool_ids,
            application_ids,
            skill_tool_ids,
            workspace_id,
            mcp_output_enable,
        ):
            prompt_tokens = 1
            completion_tokens = 2
            chat_record_id = str(uuid.uuid7())
            step.context['message_tokens'] = prompt_tokens
            step.context['answer_tokens'] = completion_tokens
            step.context['answer_text'] = answer
            step.context['run_time'] = 0
            manage.context['message_tokens'] = prompt_tokens
            manage.context['answer_tokens'] = completion_tokens
            manage.context['run_time'] = 0
            post_response_handler.handler(
                chat_id,
                chat_record_id,
                paragraph_list or [],
                problem_text,
                answer,
                manage,
                step,
                padding_problem_text,
                reasoning_content='',
            )
            return manage.get_base_to_response().to_block_response(
                str(chat_id),
                chat_record_id,
                answer,
                True,
                prompt_tokens,
                completion_tokens,
                {'answer_list': [{'content': answer, 'reasoning_content': ''}]},
            )

        return _execute_block

    def test_same_session_reuses_chat_binding(self):
        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            return_value=[],
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('session answer'),
        ):
            first_response = self._post(self._payload())
            second_response = self._post(self._payload(question='Follow-up question'))

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.json()['meta']['chat_id'], second_response.json()['meta']['chat_id'])
        self.assertEqual(Chat.objects.count(), 1)

        session_binding = cache.get(get_session_cache_key('session-001'))
        self.assertIsNotNone(session_binding)
        self.assertEqual(session_binding['chat_id'], first_response.json()['meta']['chat_id'])
        self.assertGreaterEqual(session_binding['last_seen_at'], session_binding['created_at'])

    def test_session_reuse_across_different_binding_rejected(self):
        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            return_value=[],
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('session answer'),
        ):
            first_response = self._post(self._payload())
            second_response = self._post(
                self._payload(
                    context={
                        'user_id': 'user-2',
                        'role_code': 'developer',
                        'project_id': 'project-1',
                        'source': 'orchestrator',
                    }
                )
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 409)
        self.assertEqual(second_response.json()['error_code'], 'SESSION_MISMATCH')
        self.assertEqual(Chat.objects.count(), 1)

    def test_invalid_api_key_returns_unauthorized(self):
        response = self._post(self._payload(), 'bad-secret')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error_code'], 'UNAUTHORIZED')

    def test_preview_does_not_mutate_session(self):
        response = self._post(self._payload(params={'_param_preview': True}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json().keys()), {'param_schema'})
        self.assertIsNone(cache.get(get_session_cache_key('session-001')))
        self.assertEqual(Chat.objects.count(), 0)


class OrchestratorQueryExecutionTestsMixin(OrchestratorQuerySessionTestsMixin):
    def setUp(self):
        super().setUp()
        self.application.knowledge_setting = {'top_n': 6, 'similarity': 0.73}
        self.application.save(update_fields=['knowledge_setting'])
        self.application_version.knowledge_setting = {'top_n': 6, 'similarity': 0.73}
        self.application_version.save(update_fields=['knowledge_setting'])
        self.primary_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Primary Knowledge',
            desc='Primary Knowledge',
            user=self.user,
            workspace_id=self.workspace.id,
        )
        self.secondary_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='Secondary Knowledge',
            desc='Secondary Knowledge',
            user=self.user,
            workspace_id=self.workspace.id,
        )
        self.primary_document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=self.primary_knowledge,
            name='Primary Document',
            char_length=120,
        )
        self.primary_paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            knowledge=self.primary_knowledge,
            document=self.primary_document,
            title='Primary Paragraph',
            content='Primary knowledge paragraph content',
            position=1,
        )
        self.secondary_document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=self.secondary_knowledge,
            name='Secondary Document',
            char_length=80,
        )
        self.secondary_paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            knowledge=self.secondary_knowledge,
            document=self.secondary_document,
            title='Secondary Paragraph',
            content='Secondary knowledge paragraph content',
            position=1,
        )
        ResourceMapping.objects.create(
            source_type='APPLICATION',
            target_type='KNOWLEDGE',
            source_id=str(self.application.id),
            target_id=str(self.primary_knowledge.id),
        )
        ResourceMapping.objects.create(
            source_type='APPLICATION',
            target_type='KNOWLEDGE',
            source_id=str(self.application.id),
            target_id=str(self.secondary_knowledge.id),
        )

    def _payload(self, **overrides):
        payload = super()._payload(**overrides)
        context = payload.setdefault('context', {})
        if 'kb_scope' not in context:
            context['kb_scope'] = [str(self.primary_knowledge.id)]
        return payload

    @staticmethod
    def _paragraph_result(paragraph: Paragraph):
        return (
            ParagraphPipelineModel.builder()
            .add_paragraph(paragraph)
            .add_similarity(0.91)
            .add_comprehensive_score(0.93)
            .add_knowledge_name(paragraph.knowledge.name)
            .add_knowledge_type(paragraph.knowledge.type)
            .add_document_name(paragraph.document.name)
            .add_hit_handling_method('optimization')
            .add_meta({})
            .build()
        )

    @staticmethod
    def _fake_execute_block(answer: str):
        def _execute_block(
            step,
            message_list,
            chat_id,
            problem_text,
            post_response_handler,
            chat_model,
            paragraph_list,
            manage,
            padding_problem_text,
            chat_user_id,
            chat_user_type,
            no_references_setting,
            model_setting,
            mcp_tool_ids,
            mcp_servers,
            mcp_source,
            tool_ids,
            application_ids,
            skill_tool_ids,
            workspace_id,
            mcp_output_enable,
        ):
            prompt_tokens = 4
            completion_tokens = 9
            chat_record_id = str(uuid.uuid7())
            step.context['message_tokens'] = prompt_tokens
            step.context['answer_tokens'] = completion_tokens
            step.context['answer_text'] = answer
            step.context['run_time'] = 0
            manage.context['message_tokens'] = prompt_tokens
            manage.context['answer_tokens'] = completion_tokens
            manage.context['run_time'] = 0
            post_response_handler.handler(
                chat_id,
                chat_record_id,
                paragraph_list or [],
                problem_text,
                answer,
                manage,
                step,
                padding_problem_text,
                reasoning_content='',
            )
            return manage.get_base_to_response().to_block_response(
                str(chat_id),
                chat_record_id,
                answer,
                True,
                prompt_tokens,
                completion_tokens,
                {'answer_list': [{'content': answer, 'reasoning_content': ''}]},
            )

        return _execute_block


class OrchestratorQueryExecutionTests(OrchestratorQueryExecutionTestsMixin, TestCase):
    def test_query_returns_answer_via_simple_pipeline(self):
        search_call = {}

        def fake_search(
            step,
            problem_text,
            knowledge_id_list,
            exclude_document_id_list,
            exclude_paragraph_id_list,
            top_n,
            similarity,
            padding_problem_text=None,
            search_mode=None,
            workspace_id=None,
            manage=None,
            **kwargs,
        ):
            search_call['problem_text'] = problem_text
            search_call['knowledge_id_list'] = knowledge_id_list
            search_call['top_n'] = top_n
            search_call['similarity'] = similarity
            return [self._paragraph_result(self.primary_paragraph)]

        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            side_effect=fake_search,
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('Deterministic orchestrator answer'),
        ):
            response = self._post(
                self._payload(
                    question='What is in the primary knowledge base?',
                    params={'top_n': 9, 'similarity': 0.82},
                )
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['text'], 'Deterministic orchestrator answer')
        self.assertEqual(payload['suggestions'], [])
        self.assertEqual(payload['cards'], [])
        self.assertEqual(payload['meta']['hit_paragraph_count'], 1)
        self.assertEqual(payload['meta']['tokens_used'], 13)
        self.assertTrue(payload['meta']['chat_id'])
        self.assertEqual(search_call['problem_text'], 'What is in the primary knowledge base?')
        self.assertEqual(search_call['knowledge_id_list'], [str(self.primary_knowledge.id)])
        self.assertEqual(search_call['top_n'], 9)
        self.assertEqual(search_call['similarity'], 0.82)

        refs = payload['references']
        self.assertEqual(len(refs), 1)
        ref = refs[0]
        self.assertEqual(ref['title'], 'Primary Document')
        self.assertEqual(ref['snippet'], 'Primary knowledge paragraph content')
        self.assertEqual(ref['document_id'], str(self.primary_paragraph.document_id))
        self.assertEqual(ref['paragraph_id'], str(self.primary_paragraph.id))
        self.assertEqual(ref['knowledge_name'], 'Primary Knowledge')
        self.assertEqual(ref['confidence'], 0.93)

    def test_invalid_kb_scope_returns_structured_error(self):
        response = self._post(
            self._payload(
                context={
                    'user_id': 'user-1',
                    'role_code': 'developer',
                    'project_id': 'project-1',
                    'source': 'orchestrator',
                    'kb_scope': ['unknown-knowledge'],
                }
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error_code'], 'KNOWLEDGE_SCOPE_INVALID')
        self.assertEqual(Chat.objects.count(), 0)

    def test_no_hits_returns_valid_normal_contract(self):
        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            return_value=[],
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('No references answer'),
        ):
            response = self._post(self._payload(question='No matching paragraph question'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['text'], 'No references answer')
        self.assertEqual(payload['references'], [])
        self.assertEqual(payload['suggestions'], [])
        self.assertEqual(payload['cards'], [])
        self.assertEqual(payload['meta']['hit_paragraph_count'], 0)
        self.assertTrue(payload['meta']['chat_id'])


class OrchestratorParamPreviewTests(OrchestratorQueryExecutionTestsMixin, TestCase):
    def test_preview_returns_param_schema_only(self):
        response = self._post(self._payload(params={'_param_preview': True}))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {'param_schema'})

        schema = body['param_schema']

        self.assertIn('kb_scope', schema)
        kb_scope = schema['kb_scope']
        self.assertEqual(kb_scope['type'], 'array')
        self.assertEqual(kb_scope['items'], {'type': 'string'})
        self.assertEqual(len(kb_scope['options']), 2)
        option_labels = {opt['label'] for opt in kb_scope['options']}
        option_values = {opt['value'] for opt in kb_scope['options']}
        self.assertIn('Primary Knowledge', option_labels)
        self.assertIn('Secondary Knowledge', option_labels)
        self.assertEqual(option_values, {str(self.primary_knowledge.id), str(self.secondary_knowledge.id)})
        for opt in kb_scope['options']:
            self.assertIn('label', opt)
            self.assertIn('value', opt)

        self.assertIn('top_n', schema)
        top_n = schema['top_n']
        self.assertEqual(top_n['type'], 'integer')
        self.assertEqual(top_n['default'], 6)
        self.assertEqual(top_n['minimum'], 1)
        self.assertEqual(top_n['maximum'], 100)
        self.assertEqual(top_n['step'], 1)

        self.assertIn('similarity', schema)
        similarity = schema['similarity']
        self.assertEqual(similarity['type'], 'number')
        self.assertAlmostEqual(similarity['default'], 0.73)
        self.assertEqual(similarity['minimum'], 0.0)
        self.assertEqual(similarity['maximum'], 1.0)
        self.assertAlmostEqual(similarity['step'], 0.01)

    def test_preview_mode_does_not_create_chat_or_cache_binding(self):
        chat_count_before = Chat.objects.count()
        self._post(self._payload(params={'_param_preview': True}))
        self.assertEqual(Chat.objects.count(), chat_count_before)
        self.assertIsNone(cache.get(get_session_cache_key('session-001')))


class OrchestratorQueryResponseTests(OrchestratorQueryExecutionTestsMixin, TestCase):
    def test_response_includes_grounded_references_and_meta(self):
        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            return_value=[self._paragraph_result(self.primary_paragraph)],
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('Grounded answer'),
        ):
            response = self._post(
                self._payload(question='Tell me about primary knowledge')
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        refs = payload['references']
        self.assertEqual(len(refs), 1)
        ref = refs[0]
        self.assertIn('title', ref)
        self.assertIn('snippet', ref)
        self.assertIn('confidence', ref)
        self.assertEqual(ref['title'], 'Primary Document')
        self.assertTrue(len(ref['snippet']) > 0)
        self.assertIsNotNone(ref['confidence'])
        self.assertEqual(ref['document_id'], str(self.primary_paragraph.document_id))
        self.assertEqual(ref['paragraph_id'], str(self.primary_paragraph.id))
        self.assertEqual(ref['knowledge_name'], 'Primary Knowledge')

        meta = payload['meta']
        self.assertEqual(meta['hit_paragraph_count'], 1)
        self.assertTrue(meta['chat_id'])
        self.assertIsInstance(meta['tokens_used'], int)

    def test_low_confidence_returns_empty_suggestions_not_templates(self):
        with patch(
            'application.chat_pipeline.step.search_dataset_step.impl.base_search_dataset_step.BaseSearchDatasetStep.execute',
            autospec=True,
            return_value=[self._paragraph_result(self.primary_paragraph)],
        ), patch(
            'application.chat_pipeline.step.chat_step.impl.base_chat_step.BaseChatStep.execute_block',
            new=self._fake_execute_block('Low confidence answer'),
        ):
            response = self._post(
                self._payload(question='Tell me about primary knowledge')
            )

        self.assertEqual(response.status_code, 200)
        suggestions = response.json()['suggestions']
        self.assertIsInstance(suggestions, list)
        self.assertEqual(suggestions, [])
        for s in suggestions:
            self.assertNotIn('还想', s)
            self.assertNotIn('帮助', s)
