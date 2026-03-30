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


class EmailSettingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email='email-admin@example.com',
            phone='',
            nick_name='Email Admin',
            username='email-admin',
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='email-user@example.com',
            phone='',
            nick_name='Email User',
            username='email-user',
            password=password_encrypt('User123!'),
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        self.payload = {
            'email_host': 'smtp.example.com',
            'email_port': 587,
            'email_host_user': 'sender@example.com',
            'email_host_password': 'password',
            'email_use_tls': True,
            'email_use_ssl': False,
            'from_email': 'sender@example.com',
        }

    def test_admin_get_returns_empty_email_settings_by_default(self):
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

        response = self.client.get(f'{ADMIN_API_PREFIX}/email_setting')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], {})

    @patch('system_manage.serializers.email_setting.EmailBackend.open', return_value=True)
    def test_admin_put_creates_and_persists_email_settings(self, _open_mock):
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

        response = self.client.put(
            f'{ADMIN_API_PREFIX}/email_setting',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], self.payload)

        setting = SystemSetting.objects.get(type=SettingType.EMAIL)
        self.assertEqual(setting.meta, self.payload)

    @patch('system_manage.serializers.email_setting.EmailBackend.open', return_value=True)
    def test_admin_put_overwrites_existing_email_settings(self, _open_mock):
        SystemSetting.objects.create(
            type=SettingType.EMAIL,
            meta={
                'email_host': 'old.example.com',
                'email_port': 25,
                'email_host_user': 'old@example.com',
                'email_host_password': 'old-password',
                'email_use_tls': False,
                'email_use_ssl': False,
                'from_email': 'old@example.com',
            },
        )
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

        response = self.client.put(
            f'{ADMIN_API_PREFIX}/email_setting',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        setting = SystemSetting.objects.get(type=SettingType.EMAIL)
        self.assertEqual(setting.meta, self.payload)

    @patch('system_manage.serializers.email_setting.EmailBackend.open', return_value=True)
    def test_admin_post_validates_email_settings_successfully(self, _open_mock):
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

        response = self.client.post(
            f'{ADMIN_API_PREFIX}/email_setting',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['message'], 'Success')

    def test_non_admin_cannot_manage_email_setting_endpoints(self):
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

        responses = [
            self.client.get(f'{ADMIN_API_PREFIX}/email_setting'),
            self.client.put(f'{ADMIN_API_PREFIX}/email_setting', self.payload, format='json'),
            self.client.post(f'{ADMIN_API_PREFIX}/email_setting', self.payload, format='json'),
        ]

        for response in responses:
            self.assertEqual(response.status_code, 403)
