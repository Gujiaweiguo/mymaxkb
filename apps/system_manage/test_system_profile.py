import json

from django.test import TestCase
from rest_framework.test import APIClient

from system_manage.serializers.system import SystemProfileSerializer


ADMIN_API_PREFIX = '/admin/api'


class SystemProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_public_get_profile_returns_serializer_backed_payload(self):
        expected = SystemProfileSerializer.profile()

        response = self.client.get(f'{ADMIN_API_PREFIX}/profile')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], expected)
        self.assertEqual(
            set(payload['data'].keys()),
            {'version', 'edition', 'license_is_valid', 'ras'},
        )
