import uuid
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import Group
from common.exception.app_exception import AppApiException
from common.utils.rsa_util import rsa_long_encrypt
from models_provider.models import Model, Status
from models_provider.tools import get_provider, get_model_default_params
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.serializers.model_serializer import ModelSerializer
from models_provider.views.model import SystemSharedModelSetting, SystemResourceModelView
from system_manage.models import Workspace
from system_manage.models.resource_mapping import ResourceMapping
from users.models import User


class StatusEnumTests(TestCase):
    def test_has_success(self):
        self.assertEqual(Status.SUCCESS.value, "SUCCESS")

    def test_has_error(self):
        self.assertEqual(Status.ERROR.value, "ERROR")

    def test_has_download(self):
        self.assertEqual(Status.DOWNLOAD.value, "DOWNLOAD")

    def test_has_pause_download(self):
        self.assertEqual(Status.PAUSE_DOWNLOAD.value, "PAUSE_DOWNLOAD")

    def test_choices_count(self):
        self.assertEqual(len(Status.choices), 4)


class ProviderConstantsTests(SimpleTestCase):
    def test_openai_provider_exists(self):
        provider = get_provider("model_openai_provider")
        self.assertIsNotNone(provider)

    def test_deepseek_provider_exists(self):
        provider = get_provider("model_deepseek_provider")
        self.assertIsNotNone(provider)

    def test_ollama_provider_exists(self):
        provider = get_provider("model_ollama_provider")
        self.assertIsNotNone(provider)

    def test_invalid_provider_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_provider("nonexistent_provider")

    def test_removed_local_provider_fails_fast(self):
        with self.assertRaises(AppApiException) as context:
            get_provider("model_local_provider")

        self.assertIn("model_local_provider", str(context.exception))

    def test_removed_local_provider_not_in_registry(self):
        self.assertNotIn("model_local_provider", ModelProvideConstants.__members__)


class LegacyLocalProviderStateTests(SimpleTestCase):
    def test_model_to_dict_fails_fast_for_removed_local_provider(self):
        model = SimpleNamespace(
            id=uuid.uuid4(),
            name="legacy-local-model",
            model_type="EMBEDDING",
            model_name="legacy-local-model",
            provider="model_local_provider",
            credential="encrypted-legacy-credential",
            workspace_id="default",
            status="SUCCESS",
            meta={},
            user=None,
        )

        with patch(
            'models_provider.serializers.model_serializer.rsa_long_decrypt',
            return_value=json.dumps({"cache_folder": "/tmp/models"}),
        ):
            with self.assertRaises(AppApiException) as context:
                ModelSerializer.model_to_dict(model)

        self.assertIn("model_local_provider", str(context.exception))

    def test_providers_have_get_model(self):
        for provider_enum in ModelProvideConstants:
            provider = provider_enum.value
            self.assertTrue(hasattr(provider, 'get_model'))
            self.assertTrue(hasattr(provider, 'get_model_type_list'))


class GetModelDefaultParamsTests(TestCase):
    def test_extracts_default_values(self):
        mock_model = type('MockModel', (), {
            'model_params_form': [
                {'field': 'max_tokens', 'default_value': '2048'},
                {'field': 'temperature', 'default_value': '0.7'},
            ]
        })()
        result = get_model_default_params(mock_model)
        self.assertEqual(result['max_tokens'], 2048)
        self.assertEqual(result['temperature'], '0.7')

    def test_skips_none_default_value(self):
        mock_model = type('MockModel', (), {
            'model_params_form': [
                {'field': 'temperature', 'default_value': None},
                {'field': 'max_tokens', 'default_value': '1024'},
            ]
        })()
        result = get_model_default_params(mock_model)
        self.assertNotIn('temperature', result)
        self.assertEqual(result['max_tokens'], 1024)

    def test_handles_empty_params_form(self):
        mock_model = type('MockModel', (), {'model_params_form': []})()
        result = get_model_default_params(mock_model)
        self.assertEqual(result, {})

    def test_non_numeric_string_stays_as_string(self):
        mock_model = type('MockModel', (), {
            'model_params_form': [
                {'field': 'api_base', 'default_value': 'https://api.example.com'},
            ]
        })()
        result = get_model_default_params(mock_model)
        self.assertEqual(result['api_base'], 'https://api.example.com')


class ModelUniqueConstraintTests(TestCase):
    def test_duplicate_name_same_workspace_rejected(self):
        Model.objects.create(
            name="test-model",
            model_type="LLM",
            model_name="gpt-4",
            provider="model_openai_provider",
            credential="encrypted",
            workspace_id="default"
        )
        with self.assertRaises(IntegrityError):
            Model.objects.create(
                name="test-model",
                model_type="LLM",
                model_name="gpt-4",
                provider="model_openai_provider",
                credential="encrypted",
                workspace_id="default"
            )

    def test_same_name_different_workspace_allowed(self):
        Model.objects.create(
            name="test-model",
            model_type="LLM",
            model_name="gpt-4",
            provider="model_openai_provider",
            credential="encrypted",
            workspace_id="workspace1"
        )
        model2 = Model.objects.create(
            name="test-model",
            model_type="LLM",
            model_name="gpt-4",
            provider="model_openai_provider",
            credential="encrypted",
            workspace_id="workspace2"
        )
        self.assertIsNotNone(model2.id)


class SystemSharedModelSettingTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        suffix = uuid.uuid4().hex[:8]
        self.admin = User.objects.create(
            id=uuid.uuid4(),
            email=f'shared-model-admin-{suffix}@example.com',
            phone='',
            nick_name=f'shared-model-admin-{suffix}',
            username=f'shared-model-admin-{suffix}',
            password='hashed',
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.owner = User.objects.create(
            id=uuid.uuid4(),
            email=f'shared-model-owner-{suffix}@example.com',
            phone='',
            nick_name=f'shared-model-owner-{suffix}',
            username=f'shared-model-owner-{suffix}',
            password='hashed',
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        self.auth_token = SimpleNamespace(role_list=['ADMIN'], permission_list=[])

    def test_admin_can_list_system_shared_models(self):
        model = Model.objects.create(
            name='shared-model',
            model_type='LLM',
            model_name='gpt-4',
            provider='model_openai_provider',
            credential='encrypted',
            workspace_id='workspace-a',
            user=self.owner,
        )
        request = self.factory.get('/system/shared/model')
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = SystemSharedModelSetting.as_view()(request)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        matching_models = [item for item in payload['data'] if item['id'] == str(model.id)]
        self.assertEqual(len(matching_models), 1)
        self.assertEqual(matching_models[0]['username'], self.owner.username)

    def test_non_admin_cannot_list_system_shared_models(self):
        request = self.factory.get('/system/shared/model')
        force_authenticate(
            request,
            user=self.owner,
            token=SimpleNamespace(role_list=['USER'], permission_list=[]),
        )

        response = SystemSharedModelSetting.as_view()(request)

        self.assertEqual(response.status_code, 403)


class SystemResourceModelViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        suffix = uuid.uuid4().hex[:8]
        self.admin = User.objects.create(
            id=uuid.uuid4(),
            email=f'resource-model-admin-{suffix}@example.com',
            phone='',
            nick_name=f'resource-model-admin-{suffix}',
            username=f'resource-model-admin-{suffix}',
            password='hashed',
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.owner = User.objects.create(
            id=uuid.uuid4(),
            email=f'resource-model-owner-{suffix}@example.com',
            phone='',
            nick_name=f'resource-model-owner-{suffix}',
            username=f'resource-model-owner-{suffix}',
            password='hashed',
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        self.admin_auth = SimpleNamespace(role_list=['ADMIN'], permission_list=[])
        self.user_auth = SimpleNamespace(role_list=['USER'], permission_list=[])
        Workspace.objects.get_or_create(id='workspace-a', defaults={'name': 'Workspace A'})
        Workspace.objects.get_or_create(id='workspace-b', defaults={'name': 'Workspace B'})

    def create_model(self, name: str, workspace_id: str, model_params_form=None):
        return Model.objects.create(
            name=name,
            model_type='LLM',
            model_name='gpt-4o-mini',
            provider='model_openai_provider',
            credential=rsa_long_encrypt(json.dumps({'api_key': 'secret-key'})),
            workspace_id=workspace_id,
            user=self.owner,
            model_params_form=model_params_form or [],
        )

    def test_admin_can_page_system_resource_models_with_workspace_metadata(self):
        model = self.create_model('workspace-model-a', 'workspace-a')
        self.create_model('workspace-model-b', 'workspace-b')
        self.create_model('shared-model', 'None')
        ResourceMapping.objects.create(
            source_type=Group.APPLICATION.value,
            target_type=Group.MODEL.value,
            source_id='application-1',
            target_id=str(model.id),
        )

        request = self.factory.get(
            '/system/resource/model/1/20',
            {'workspace_ids': json.dumps(['workspace-a'])},
        )
        force_authenticate(request, user=self.admin, token=self.admin_auth)

        response = SystemResourceModelView.Page.as_view()(request, current_page=1, page_size=20)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        record = payload['data']['records'][0]
        self.assertEqual(str(record['id']), str(model.id))
        self.assertEqual(record['workspace_id'], 'workspace-a')
        self.assertEqual(record['workspace_name'], 'Workspace A')
        self.assertEqual(record['resource_count'], 1)
        self.assertEqual(record['username'], self.owner.username)

    def test_non_admin_cannot_page_system_resource_models(self):
        request = self.factory.get('/system/resource/model/1/20')
        force_authenticate(request, user=self.owner, token=self.user_auth)

        response = SystemResourceModelView.Page.as_view()(request, current_page=1, page_size=20)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_and_delete_system_resource_model(self):
        model = self.create_model('workspace-model', 'workspace-a')

        get_request = self.factory.get(f'/system/resource/model/{model.id}')
        force_authenticate(get_request, user=self.admin, token=self.admin_auth)
        get_response = SystemResourceModelView.Operate.as_view()(get_request, model_id=str(model.id))

        self.assertEqual(get_response.status_code, 200)
        get_payload = json.loads(get_response.content)
        self.assertEqual(get_payload['data']['workspace_id'], 'workspace-a')
        self.assertEqual(get_payload['data']['credential']['api_key'], 'secr***************-key')

        meta_request = self.factory.get(f'/system/resource/model/{model.id}/meta')
        force_authenticate(meta_request, user=self.admin, token=self.admin_auth)
        meta_response = SystemResourceModelView.ModelMeta.as_view()(meta_request, model_id=str(model.id))

        self.assertEqual(meta_response.status_code, 200)
        meta_payload = json.loads(meta_response.content)
        self.assertEqual(meta_payload['data']['workspace_id'], 'workspace-a')
        self.assertEqual(meta_payload['data']['name'], 'workspace-model')
        self.assertNotIn('credential', meta_payload['data'])

        with patch(
            'models_provider.serializers.model_serializer.ModelSerializer.Operate.edit',
            return_value={'id': str(model.id), 'name': 'updated-model'},
        ) as edit_mock:
            put_request = self.factory.put(
                f'/system/resource/model/{model.id}',
                data={'name': 'updated-model'},
                format='json',
            )
            force_authenticate(put_request, user=self.admin, token=self.admin_auth)
            put_response = SystemResourceModelView.Operate.as_view()(put_request, model_id=str(model.id))

        self.assertEqual(put_response.status_code, 200)
        put_payload = json.loads(put_response.content)
        self.assertEqual(put_payload['data']['name'], 'updated-model')
        edit_mock.assert_called_once()

        delete_request = self.factory.delete(f'/system/resource/model/{model.id}')
        force_authenticate(delete_request, user=self.admin, token=self.admin_auth)
        delete_response = SystemResourceModelView.Operate.as_view()(delete_request, model_id=str(model.id))

        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Model.objects.filter(id=model.id).exists())

    def test_admin_cannot_edit_or_delete_shared_model_through_system_resource(self):
        model = self.create_model('shared-model', 'None')

        meta_request = self.factory.get(f'/system/resource/model/{model.id}/meta')
        force_authenticate(meta_request, user=self.admin, token=self.admin_auth)
        meta_response = SystemResourceModelView.ModelMeta.as_view()(meta_request, model_id=str(model.id))

        self.assertEqual(meta_response.status_code, 200)
        meta_payload = json.loads(meta_response.content)
        self.assertEqual(meta_payload['code'], 500)
        self.assertIn('Shared models cannot be deleted or modified', meta_payload['message'])

        get_request = self.factory.get(f'/system/resource/model/{model.id}')
        force_authenticate(get_request, user=self.admin, token=self.admin_auth)
        get_response = SystemResourceModelView.Operate.as_view()(get_request, model_id=str(model.id))

        self.assertEqual(get_response.status_code, 200)
        get_payload = json.loads(get_response.content)
        self.assertEqual(get_payload['code'], 500)
        self.assertIn('Shared models cannot be deleted or modified', get_payload['message'])

        put_request = self.factory.put(
            f'/system/resource/model/{model.id}',
            data={'name': 'should-not-update'},
            format='json',
        )
        force_authenticate(put_request, user=self.admin, token=self.admin_auth)
        put_response = SystemResourceModelView.Operate.as_view()(put_request, model_id=str(model.id))

        self.assertEqual(put_response.status_code, 200)
        put_payload = json.loads(put_response.content)
        self.assertEqual(put_payload['code'], 500)
        self.assertIn('Shared models cannot be deleted or modified', put_payload['message'])

        delete_request = self.factory.delete(f'/system/resource/model/{model.id}')
        force_authenticate(delete_request, user=self.admin, token=self.admin_auth)
        delete_response = SystemResourceModelView.Operate.as_view()(delete_request, model_id=str(model.id))

        self.assertEqual(delete_response.status_code, 200)
        delete_payload = json.loads(delete_response.content)
        self.assertEqual(delete_payload['code'], 500)
        self.assertIn('Shared models cannot be deleted or modified', delete_payload['message'])

    def test_admin_cannot_delete_model_with_related_resources(self):
        model = self.create_model('workspace-model-linked', 'workspace-a')
        ResourceMapping.objects.create(
            source_type=Group.APPLICATION.value,
            target_type=Group.MODEL.value,
            source_id='application-1',
            target_id=str(model.id),
        )

        delete_request = self.factory.delete(f'/system/resource/model/{model.id}')
        force_authenticate(delete_request, user=self.admin, token=self.admin_auth)
        delete_response = SystemResourceModelView.Operate.as_view()(delete_request, model_id=str(model.id))

        self.assertEqual(delete_response.status_code, 200)
        delete_payload = json.loads(delete_response.content)
        self.assertEqual(delete_payload['code'], 500)
        self.assertIn('associated with resources', delete_payload['message'])
        self.assertTrue(Model.objects.filter(id=model.id).exists())

    def test_admin_can_get_and_save_system_resource_model_params_form(self):
        model = self.create_model(
            'workspace-model',
            'workspace-a',
            model_params_form=[{'field': 'temperature', 'default_value': 0.7}],
        )

        get_request = self.factory.get(f'/system/resource/model/{model.id}/model_params_form')
        force_authenticate(get_request, user=self.admin, token=self.admin_auth)
        get_response = SystemResourceModelView.ModelParamsForm.as_view()(get_request, model_id=str(model.id))

        self.assertEqual(get_response.status_code, 200)
        get_payload = json.loads(get_response.content)
        self.assertEqual(get_payload['data'][0]['field'], 'temperature')

        put_request = self.factory.put(
            f'/system/resource/model/{model.id}/model_params_form',
            data=[{'field': 'max_tokens', 'default_value': 2048}],
            format='json',
        )
        force_authenticate(put_request, user=self.admin, token=self.admin_auth)
        put_response = SystemResourceModelView.ModelParamsForm.as_view()(put_request, model_id=str(model.id))

        self.assertEqual(put_response.status_code, 200)
        model.refresh_from_db()
        self.assertEqual(model.model_params_form, [{'field': 'max_tokens', 'default_value': 2048}])

    def test_admin_can_pause_system_resource_model_download(self):
        model = self.create_model('downloading-model', 'workspace-a')
        model.status = Status.DOWNLOAD
        model.save(update_fields=['status'])

        pause_request = self.factory.put(f'/system/resource/model/{model.id}/pause_download')
        force_authenticate(pause_request, user=self.admin, token=self.admin_auth)
        pause_response = SystemResourceModelView.PauseDownload.as_view()(pause_request, model_id=str(model.id))

        self.assertEqual(pause_response.status_code, 200)
        model.refresh_from_db()
        self.assertEqual(model.status, Status.PAUSE_DOWNLOAD)
