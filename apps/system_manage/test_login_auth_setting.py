import json

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from system_manage.serializers.login_auth_setting import LoginAuthSettingSerializer
from users.models import User


ADMIN_API_PREFIX = '/admin/api'
AUTH_SETTING_URL = f'{ADMIN_API_PREFIX}/auth/setting'


def _make_admin():
    return User.objects.create(
        id=uuid.uuid7(),
        email='login-auth-admin@example.com',
        phone='',
        nick_name='Login Auth Admin',
        username='login-auth-admin',
        password=password_encrypt('Admin123!'),
        role='ADMIN',
        source='LOCAL',
        is_active=True,
    )


class LoginAuthSettingSerializerUnitTests(TestCase):
    def test_normalize_attempt_value_zero_returns_default(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_attempt_value(0, 5, 1),
            5,
        )

    def test_normalize_attempt_value_negative_returns_min(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_attempt_value(-3, 5, 1),
            1,
        )

    def test_normalize_attempt_value_non_int_returns_default(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_attempt_value('5', 5, 1),
            5,
        )

    def test_normalize_attempt_value_valid_passes_through(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_attempt_value(7, 5, 1),
            7,
        )

    def test_normalize_login_methods_non_list_returns_local(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_login_methods('LOCAL'),
            ['LOCAL'],
        )

    def test_normalize_login_methods_empty_list_returns_local(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_login_methods([]),
            ['LOCAL'],
        )

    def test_normalize_login_methods_filters_unsupported(self):
        self.assertEqual(
            LoginAuthSettingSerializer._normalize_login_methods(['LOCAL', 'OIDC', 'SAML']),
            ['LOCAL'],
        )

    def test_to_response_no_meta_returns_defaults(self):
        response = LoginAuthSettingSerializer._to_response(None)

        self.assertEqual(response['default_value'], 'LOCAL')
        self.assertEqual(response['max_attempts'], 1)
        self.assertEqual(response['failed_attempts'], 5)
        self.assertEqual(response['lock_time'], 10)
        self.assertEqual(response['role_id'], 'USER')
        self.assertEqual(response['workspace_id'], 'default')
        self.assertEqual(response['permission'], 'NOT_AUTH')
        self.assertEqual(response['login_methods'], ['LOCAL'])
        self.assertEqual(response['auth_types'], [{'label': 'LOCAL', 'value': 'LOCAL'}])
        self.assertEqual(response['system_options'], [{'label': 'LOCAL', 'value': 'LOCAL'}])

    def test_to_response_default_value_not_in_methods_is_corrected(self):
        response = LoginAuthSettingSerializer._to_response(
            {'default_value': 'OIDC', 'login_methods': ['LOCAL']}
        )

        self.assertEqual(response['default_value'], 'LOCAL')
        self.assertEqual(response['login_methods'], ['LOCAL'])


class LoginAuthSettingAdminAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = _make_admin()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='login-auth-user@example.com',
            phone='',
            nick_name='Login Auth User',
            username='login-auth-user',
            password=password_encrypt('User123!'),
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

    def test_admin_get_returns_default_shape_when_no_setting(self):
        response = self.client.get(AUTH_SETTING_URL)

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

    def test_admin_get_returns_persisted_values(self):
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

        response = self.client.get(AUTH_SETTING_URL)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['max_attempts'], 3)
        self.assertEqual(payload['data']['failed_attempts'], 8)
        self.assertEqual(payload['data']['lock_time'], 15)
        self.assertEqual(payload['data']['login_methods'], ['LOCAL'])

    def test_admin_put_creates_and_persists_normalized_login_auth_settings(self):
        response = self.client.put(
            AUTH_SETTING_URL,
            {
                'default_value': 'LOCAL',
                'login_methods': ['LOCAL'],
                'max_attempts': 3,
                'failed_attempts': 8,
                'lock_time': 15,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['max_attempts'], 3)
        self.assertEqual(payload['data']['failed_attempts'], 8)
        self.assertEqual(payload['data']['lock_time'], 15)
        self.assertEqual(payload['data']['login_methods'], ['LOCAL'])

        setting = SystemSetting.objects.get(type=SettingType.LOGIN_AUTH)
        self.assertEqual(setting.meta['max_attempts'], 3)
        self.assertEqual(setting.meta['failed_attempts'], 8)
        self.assertEqual(setting.meta['lock_time'], 15)

    def test_admin_put_updates_existing_login_auth_settings(self):
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

        response = self.client.put(
            AUTH_SETTING_URL,
            {
                'default_value': 'LOCAL',
                'login_methods': ['LOCAL'],
                'max_attempts': 0,
                'failed_attempts': -3,
                'lock_time': 0,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['max_attempts'], 1)
        self.assertEqual(payload['data']['failed_attempts'], -1)
        self.assertEqual(payload['data']['lock_time'], 10)

        setting = SystemSetting.objects.get(type=SettingType.LOGIN_AUTH)
        self.assertEqual(setting.meta['max_attempts'], 1)
        self.assertEqual(setting.meta['failed_attempts'], -1)
        self.assertEqual(setting.meta['lock_time'], 10)

    def test_non_admin_cannot_manage_login_auth_settings(self):
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

        get_response = self.client.get(AUTH_SETTING_URL)
        put_response = self.client.put(
            AUTH_SETTING_URL,
            {
                'default_value': 'LOCAL',
                'login_methods': ['LOCAL'],
                'max_attempts': 3,
                'failed_attempts': 8,
                'lock_time': 15,
            },
            format='json',
        )

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(put_response.status_code, 403)
