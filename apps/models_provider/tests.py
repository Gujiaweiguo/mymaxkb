from django.test import TestCase
from django.db import IntegrityError

from models_provider.models import Model, Status
from models_provider.tools import get_provider, get_model_default_params
from models_provider.constants.model_provider_constants import ModelProvideConstants


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


class ProviderConstantsTests(TestCase):
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
