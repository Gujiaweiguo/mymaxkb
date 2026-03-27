import uuid_utils.compat as uuid
from django.test import TestCase

from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationTypeChoices,
)
from application.serializers.application_platform import ALL_PLATFORM_TYPES
from common.utils.common import password_encrypt
from users.models import User


class PlatformIntegrationSmokeTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create(
            id=uuid.uuid7(),
            email='platform-owner@example.com',
            phone='',
            nick_name='platform-owner',
            username='platform-owner',
            password=password_encrypt('Secret1!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id='platform-folder',
            name='Platform Folder',
            user=self.owner,
            workspace_id='default',
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='Platform App',
            desc='Platform App Description',
            user=self.owner,
            folder=self.folder,
            workspace_id='default',
            type=ApplicationTypeChoices.SIMPLE,
            icon='./favicon.ico',
        )

    def test_supported_platform_types_are_exposed(self):
        self.assertIn('wecom', ALL_PLATFORM_TYPES)
        self.assertIn('dingtalk', ALL_PLATFORM_TYPES)
        self.assertIn('lark', ALL_PLATFORM_TYPES)

    def test_application_access_token_can_store_platform_auth_value(self):
        access_token = ApplicationAccessToken.objects.create(
            application=self.application,
            access_token='platform-access-token',
            is_active=True,
            authentication=True,
            authentication_value={
                'wecom': {
                    'is_active': False,
                    'is_valid': True,
                    'config': {'corp_id': 'corp-id'},
                }
            },
        )

        self.assertTrue(access_token.authentication)
        self.assertIn('wecom', access_token.authentication_value)
        self.assertTrue(access_token.authentication_value['wecom']['is_valid'])
