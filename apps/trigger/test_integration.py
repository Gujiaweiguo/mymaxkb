import json
from unittest.mock import patch

import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.utils.common import password_encrypt
from maxkb.const import CONFIG
from trigger.models import Trigger, TriggerTask
from users.models import User


def set_system_user_auth(client: APIClient, user: User):
    token = signing.dumps(
        {
            'username': user.username,
            'id': str(user.id),
            'email': user.email,
            'type': AuthenticationType.SYSTEM_USER.value,
        }
    )
    version, get_key = Cache_Version.TOKEN.value
    cache.set(get_key(token), user, timeout=CONFIG.get_session_timeout(), version=version)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class SystemResourceTriggerIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email='system-trigger-admin@example.com',
            phone='',
            nick_name='System Trigger Admin',
            username='system-trigger-admin',
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id='system-trigger-folder',
            name='System Trigger Folder',
            user=self.admin_user,
            workspace_id='default',
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='System Trigger App',
            desc='System Trigger Description',
            user=self.admin_user,
            folder=self.folder,
            workspace_id='default',
            type=ApplicationTypeChoices.SIMPLE,
            icon='./favicon.ico',
            is_publish=True,
        )
        self.trigger_id = str(uuid.uuid7())
        set_system_user_auth(self.client, self.admin_user)

    def create_payload(self):
        return {
            'id': self.trigger_id,
            'name': 'System Trigger',
            'desc': 'system resource trigger',
            'trigger_type': 'SCHEDULED',
            'trigger_setting': {
                'schedule_type': 'daily',
                'time': ['09:00'],
            },
            'is_active': True,
            'trigger_task': [
                {
                    'source_type': 'APPLICATION',
                    'source_id': str(self.application.id),
                    'parameter': {
                        'question': {
                            'source': 'custom',
                            'value': 'hello',
                        }
                    },
                    'meta': {},
                }
            ],
        }

    @patch('trigger.handler.simple_tools.undeploy')
    @patch('trigger.handler.simple_tools.deploy')
    def test_system_resource_trigger_crud(self, mock_deploy, mock_undeploy):
        create_response = self.client.post(
            f'/admin/api/system/resource/APPLICATION/{self.application.id}/trigger',
            self.create_payload(),
            format='json',
        )

        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(Trigger.objects.filter(id=self.trigger_id).exists())
        self.assertTrue(
            TriggerTask.objects.filter(
                trigger_id=self.trigger_id,
                source_type='APPLICATION',
                source_id=self.application.id,
            ).exists()
        )

        list_response = self.client.get(
            f'/admin/api/system/resource/APPLICATION/{self.application.id}/trigger'
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(json.loads(list_response.content)['data']), 1)

        detail_response = self.client.get(
            f'/admin/api/system/resource/APPLICATION/{self.application.id}/trigger/{self.trigger_id}'
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['data']['id'], self.trigger_id)

        edit_response = self.client.put(
            f'/admin/api/system/resource/APPLICATION/{self.application.id}/trigger/{self.trigger_id}',
            {'name': 'Updated System Trigger'},
            format='json',
        )
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(edit_response.json()['data']['name'], 'Updated System Trigger')

        delete_response = self.client.delete(
            f'/admin/api/system/resource/APPLICATION/{self.application.id}/trigger/{self.trigger_id}'
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Trigger.objects.filter(id=self.trigger_id).exists())
