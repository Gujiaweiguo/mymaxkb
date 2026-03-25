# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： test_platform_integration.py
@date： 2026/3/24
@desc: Tests for platform integration endpoints
"""

import hashlib
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from application.models import Application, ApplicationAccessToken
from system_manage.models import SystemSetting, SettingType
from application.views.application_platform import (
    ApplicationPlatformStatusView,
    ApplicationPlatformConfigView
    ApplicationPlatformStatusView,
)
from application.serializers.application_platform import (
    ApplicationPlatformStatusResponseSerializer,
    ApplicationPlatformConfigRequestSerializer,
    ApplicationPlatformManageSerializer,
    SUPPORTED_PLATFORM_TYPES
)


class PlatformIntegrationTestCase(TestCase):
    """Base test case for platform integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test application
        self.application = Application.objects.create(
            id=uuid.uuid4(),
            workspace_id='test-workspace',
            name='Test Application',
            desc='Test Application Description'
        )
        self.application.save()
        
        # Create test application access token
        self.access_token = ApplicationAccessToken.objects.create(
            application=self.application,
            access_token=hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[8:24],
            is_active=True,
        )
        self.access_token.save()
        
        # Create system setting for platform source
        self.system_setting = SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                'wecom': {
                    'config': {
                        'corp_id': 'test_corp_id',
                        'agent_id': 'test_agent_id',
                        'app_secret': 'test_secret'
                    },
                    'token': 'test_token',
                    'encoding_aes_key': 'test_key',
                    'callback_url': 'http://test.com/callback/wecom'
                },
                'is_valid': True,
                'is_active': False
            },
            'dingtalk': {
                'config': {
                    'app_key': 'test_app_key',
                    'app_secret': 'test_secret'
                },
                'is_valid': True,
                'is_active': False
            },
            'lark': {
                'config': {
                    'app_id': 'test_app_id',
                    'app_secret': 'test_secret'
                },
                'is_valid': True,
                'is_active': False
            }
        }
        self.system_setting.meta = {
            'wecom': self.system_setting.meta['wecom'],
            'dingtalk': self.system_setting.meta['dingtalk'],
            'lark': self.system_setting.meta['lark']
        }
        self.system_setting.save()
    
    def test_get_platformStatus(self):
        """Test getting platform status"""
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/status'
        )
        
        # Initially no platform configs
        self.assertEqual(response.status_code, 200)
        
        # Verify response data structure
        self.assertIn('wecomBot', response.data)
        self.assertIn('wecom', response.data)
        self.assertIn('dingtalk', response.data)
        self.assertIn('lark', response.data)
        self.assertIn('wechat', response.data)
        self.assertIn('slack', response.data)
        
        # All should be inactive initially
        for platform_type in SUPPORTED_PLATFORM_TYPES:
            self.assertIn(platform_type, response.data[platform_type])
            self.assertEqual(response.data[platform_type][0], [False, False, False])
        
        # Now configure we
        self._configure_provider('wecom')
        self._configure_provider('dingtalk')
        self._configure_provider('lark')
        
        # Verify the status changes
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/status')
        )
        
        # Verify status is now active
        for platform_type in SUPPORTED_PLATFORM_TYPES:
            status = response.data[platform_type]
            self.assertTrue(status[8])  # active
            self.assertTrue(status[9])  # exists
            
            # Verify callback URLs
            self.assertIn('callback_url', response.data[platform_type])
            expected_callback = f'http://test.com/callback/{platform_type}/{self.application.id}'
            self.assertEqual(response.data[platform_type]['callback_url'], expected_callback)

    def test_get_platformConfig(self):
        """Test getting platform configuration"""
        self._configure_provider('wecom')
        
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/wecom')
        )
        
        # Verify response data
        self.assertEqual(response.status_code, 200)
        self.assertIn('corp_id', response.data)
        self.assertIn('agent_id', response.data)
        self.assertIn('app_secret', response.data)
        self.assertIn('token', response.data)
        self.assertIn('encoding_aes_key', response.data)
        self.assertIn('callback_url', response.data)
        
        # Verify the dingtalk config
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/dingtalk')
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('app_key', response.data)
        self.assertIn('app_secret', response.data)
        self.assertIn('callback_url', response.data)
        
        # Verify the lark config
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/lark')
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('app_id', response.data)
        self.assertIn('app_secret', response.data)
        self.assertIn('callback_url', response.data)
        
        # Test invalid platform type
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/invalid')
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_platform_config(self):
        """Test updating platform configuration"""
        self._configure_provider('wecom')
        
        # Update weCom config
        update_data = {
            'corp_id': 'updated_corp_id',
            'agent_id': 'updated_agent_id',
            'app_secret': 'updated_secret',
            'token': 'updated_token',
            'encoding_aes_key': 'updated_key',
        }
        
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/wecom'),
            update_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the update
        self.access_token.refresh_from_db()
        self.access_token = ApplicationAccessToken.objects.get(application=self.application)
        self.assertEqual(self.access_token.authentication_value['wecom'], update_data)
    
 def test_update_platform_status(self):
        """Test updating platform status"""
        self._configure_provider('wecom')
        
        # Activate valid platform
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.access_token.refresh_from_db()
        self.access_token = ApplicationAccessToken.objects.get(application=self.application)
        self.assertTrue(self.access_token.authentication_value['wecom']['is_active'])
        
        # Deactivate valid platform - should fail
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        
    def test_update_platform_status_blocked_when_invalid(self):
        """Test that updating platform status is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to activate without valid provider config
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot activate', response.data['message'])

    def test_update_platform_config_blocked_when_invalid(self):
        """Test that updating platform config is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to update with invalid provider config
        update_data = {
            'corp_id': 'updated_corp_id',
            'agent_id': 'updated_agent_id',
            'app_secret': 'updated_secret',
        }
        
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/wecom'),
            update_data
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot update', response.data['message'])

    def test_system_level_platform_source(self):
        """Test system-level platform source endpoints"""
        # Configure system-level provider
        self._configure_system_provider('wecom',        response = self.client.get('/platform/source')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        platform = response.data[0]
        
        self.assertEqual(platform['auth_type'], 'wecom')
        self.assertEqual(platform['config']['corp_id'], 'test_corp_id')
        self.assertEqual(platform['config']['agent_id'], 'test_agent_id')
        self.assertEqual(platform['config']['app_secret'], 'test_secret')
        self.assertEqual(platform['config']['token'], 'test_token')
        self.assertEqual(platform['config']['encoding_aes_key'], 'test_key')
        self.assertEqual(platform['config']['callback_url'], 'http://test.com/callback/wecom')
        self.assertEqual(platform['is_valid'], True)
        self.assertEqual(platform['is_active'], False)

    def test_chat_user_platform_source(self):
        """Test chat user-level platform source endpoints"""
        # Configure chat user provider
        self._configure_chat_user_provider('wecom')
        
        response = self.client.get('/chat_user/auth/platform/source')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        platform = response.data[0]
        
        self.assertEqual(platform['auth_type'], 'wecom')
        self.assertEqual(platform['config']['corp_id'], 'test_corp_id')
        self.assertEqual(platform['config']['agent_id'], 'test_agent_id')
        self.assertEqual(platform['config']['app_secret'], 'test_secret')
        self.assertEqual(platform['config']['token'], 'test_token')
        self.assertEqual(platform['config']['encoding_aes_key'], 'test_key')
        self.assertEqual(platform['config']['callback_url'], 'http://test.com/callback/wecom')
        self.assertEqual(platform['is_valid'], True)
        self.assertEqual(platform['is_active'], False)

    def test_chat_userPlatformSource_update(self):
        """Test updating chat user platform configuration"""
        self._configure_chat_user_provider('wecom')
        
        update_data = {
            'corp_id': 'updated_corp_id',
            'agent_id': 'updated_agent_id',
            'app_secret': 'updated_secret',
        }
        
        response = self.client.post(
            '/chat_user/auth/platform/source',
            update_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the update
        self.access_token.refresh_from_db()
        self.access_token = ApplicationAccessToken.objects.get(application=self.application)
        self.assertEqual(self.access_token.authentication_value['wecom'], update_data)

    def test_chat_userPlatformSource_validate(self):
        """Test validating chat user platform configuration"""
        self._configure_chat_user_provider('wecom')
        
        response = self.client.put(
            '/chat_user/auth/platform/source',
            data={'key': 'wecom', 'config': {}}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_valid'], True)

    def test_chatUserPlatformSource_update_blocked_when_invalid(self):
        """Test that updating chat user platform config is blocked when provider config is invalid"""
        self._configure_chat_user_provider('wecom')
        
        # Try to update with invalid provider config
        update_data = {
            'corp_id': 'updated_corp_id',
            'agent_id': 'updated_agent_id',
            'app_secret': 'updated_secret',
        }
        
        response = self.client.post(
            '/chat_user/auth/platform/source',
            update_data
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot update', response.data['message'])

    def _configure_chat_user_provider(self, platform_type, config):
        """Configure chat user provider for testing"""
        if platform_type not in SUPPORTED_PLATFORM_TYPES:
            raise ValueError(f'Unsupported platform type: {platform_type}')
        
        if not config:
            raise ValueError(f'Missing required fields: {missing_fields}')
        
        # Save config
        self._save_system_setting()
        self.system_setting = SystemSetting.objects.create(
            type=SettingType.CHAT_USER_PLATFORM_SOURCE,
            meta={
                platform_type: {
                    'config': config,
                    'is_valid': True,
                    'is_active': False
                }
            }
        )
        self.system_setting.save()
    
 def test_application_platform_views(self):
        """Test application platform views"""
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/status')
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn('wecomBot', response.data)
        self.assertIn('wecom', response.data)
        self.assertIn('dingtalk', response.data)
        self.assertIn('lark', response.data)
        self.assertIn('wechat', response.data)
        self.assertIn('slack', response.data)

        
        # Test callback URLs
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/wecom')
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('callback_url', response.data['wecom'])
        expected_callback = f'http://test.com/callback/wecom/{self.application.id}'
        self.assertEqual(response.data['wecom']['callback_url'], expected_callback)
        
 # Test weChat callback
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/wechat')
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('callback_url', response.data['wechat'])
        expected_callback = f'http://test.com/callback/wechat/{self.application.id}'
        
    def test_application_platform_views(self):
        """Test application platform views"""
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/status')
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn('wecomBot', response.data)
        self.assertIn('wecom', response.data)
        self.assertIn('dingtalk', response.data)
        self.assertIn('lark', response.data)
        self.assertIn('wechat', response.data)
        self.assertIn('slack', response.data)
        
        # Test callback URLs
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/dingtalk')
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('callback_url', response.data['dingtalk'])
        expected_callback = f'http://test.com/callback/dingtalk/{self.application.id}'
        
    def test_application_platform_views(self):
        """Test application platform views"""
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/lark')
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('callback_url', response.data['lark'])
        expected_callback = f'http://test.com/callback/lark/{self.application.id}'
        
    def test_activate_blocked_when_invalid(self):
        """Test that activating a platform is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to activate without valid provider config
        update_data = {
            'is_active': True
        }
        
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Cannot activate', response.data['message'])

    def test_activate_blocked_when_provider_valid(self):
        """Test that activating platform is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to activate with invalid provider
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('cannot activate', response.data['message'])

    def test_update_platform_status_blocked_when_provider_invalid(self):
        """Test that updating platform status is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to update with invalid provider config
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('cannot update status', response.data['message'])

    def test_system_resource_application_platform_views(self):
        """Test system resource application platform views"""
        response = self.client.get(
            reverse('system-resource-application', f'{self.application.id}/platform/status')
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains platform status
        self.assertIn('wecomBot', response.data)
        self.assertIn('wecom', response.data)
        self.assertIn('dingtalk', response.data)
        self.assertIn('lark', response.data)
        self.assertIn('wechat', response.data)
        self.assertIn('slack', response.data)
        
        # Test callback URLs
        for platform_type in response.data['wecom']['callback_url']:
            self.assertIn('callback_url', response.data['dingtalk'])
            expected_callback = f'http://test.com/callback/dingtalk/{self.application.id}'
            self.assertIn('callback_url', response.data['lark'])
            expected_callback = f'http://test.com/callback/lark/{self.application.id}')
            self.assertIn('callback_url', response.data['slack'])
            expected_callback = f'http://test.com/callback/slack/{self.application.id}'
            self.assertIn('callback_url', response.data['wechat'])
            expected_callback = f'http://test.com/callback/wechat/{self.application.id}')
            self.assertIn('callback_url', response.data['wecomBot'])
            expected_callback = f'http://test.com/callback/wecom-bot/{self.application.id}')
        
    def test_activate_blocked_when_provider_config_invalid(self):
        """Test that activating platform is blocked when provider config is invalid"""
        self._configure_provider('wecom')
        
        # Try to activate with invalid provider
        response = self.client.post(
            reverse('system-resource-application', f'{self.application.id}/platform/status'),
            data={'type': 'wecom', 'is_active': True}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('cannot activate', response.data['message'])
