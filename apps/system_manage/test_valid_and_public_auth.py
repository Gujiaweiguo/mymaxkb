import json
from unittest.mock import patch

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from users.models import User


ADMIN_API_PREFIX = '/admin/api'


class ValidAndPublicAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email='valid-admin@example.com',
            phone='',
            nick_name='Valid Admin',
            username='valid-admin',
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )

    def test_authenticated_actor_can_validate_application_count_allowance(self):
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

        response = self.client.get(f'{ADMIN_API_PREFIX}/valid/application/5')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertTrue(payload['data'])

    def test_authenticated_actor_gets_business_error_for_non_matching_application_count(self):
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

        response = self.client.get(f'{ADMIN_API_PREFIX}/valid/application/3')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 400)

    @patch('system_manage.serializers.valid_serializers.cache.get', return_value=False)
    @patch('system_manage.serializers.valid_serializers.QuerySet.count', return_value=5)
    def test_authenticated_actor_gets_business_error_when_application_quota_is_exhausted(
        self, _count_mock, _cache_mock
    ):
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

        response = self.client.get(f'{ADMIN_API_PREFIX}/valid/application/5')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 400)

    @patch('system_manage.serializers.valid_serializers.cache.get', return_value=True)
    def test_valid_license_bypasses_ce_application_limit_enforcement(self, _cache_mock):
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

        response = self.client.get(f'{ADMIN_API_PREFIX}/valid/application/999')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertTrue(payload['data'])

    def test_unauthenticated_actor_cannot_access_valid_endpoint(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/valid/application/5')

        self.assertEqual(response.status_code, 401)

    def test_public_login_auth_endpoint_returns_default_values(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/login/auth/setting')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['default_value'], 'LOCAL')
        self.assertEqual(payload['data']['max_attempts'], 1)
        self.assertEqual(payload['data']['failed_attempts'], 5)
        self.assertEqual(payload['data']['lock_time'], 10)
        self.assertEqual(payload['data']['role_id'], 'USER')
        self.assertEqual(payload['data']['workspace_id'], 'default')
        self.assertEqual(payload['data']['permission'], 'NOT_AUTH')
        self.assertEqual(payload['data']['login_methods'], ['LOCAL'])
        self.assertEqual(payload['data']['auth_types'], [{'label': 'LOCAL', 'value': 'LOCAL'}])
        self.assertEqual(payload['data']['system_options'], [{'label': 'LOCAL', 'value': 'LOCAL'}])

    def test_public_login_auth_endpoint_returns_persisted_values(self):
        SystemSetting.objects.create(
            type=SettingType.LOGIN_AUTH,
            meta={
                'default_value': 'LOCAL',
                'max_attempts': 3,
                'failed_attempts': 8,
                'lock_time': 15,
                'role_id': 'USER',
                'workspace_id': 'default',
                'permission': 'NOT_AUTH',
                'login_methods': ['LOCAL'],
            },
        )

        response = self.client.get(f'{ADMIN_API_PREFIX}/login/auth/setting')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['max_attempts'], 3)
        self.assertEqual(payload['data']['failed_attempts'], 8)
        self.assertEqual(payload['data']['lock_time'], 15)
        self.assertEqual(payload['data']['login_methods'], ['LOCAL'])
