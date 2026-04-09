import json

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.handle.impl.user_token import get_auth
from common.constants.permission_constants import ResourceAuthType, ResourcePermission
from common.utils.common import password_encrypt
from system_manage.models import Workspace, WorkspaceUserResourcePermission
from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from models_provider.models import Model
from tools.models import Tool, ToolFolder, ToolScope, ToolType
from users.models import User


ADMIN_API_PREFIX = '/admin/api'


class PermissionHappyPathMixin:
    @staticmethod
    def create_admin_user(username_prefix='permission-admin'):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f'{username_prefix}@example.com',
            phone='',
            nick_name=username_prefix,
            username=username_prefix,
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )

    @staticmethod
    def create_ce_user(username_prefix='permission-user'):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f'{username_prefix}@example.com',
            phone='',
            nick_name=username_prefix,
            username=username_prefix,
            password=password_encrypt('User123!'),
            role='USER',
            source='LOCAL',
            is_active=True,
        )

    @staticmethod
    def create_workspace(name='permission-workspace'):
        return Workspace.objects.create(
            id=str(uuid.uuid7()),
            name=name,
        )

    @staticmethod
    def setup_authenticated_client(user):
        client = APIClient()
        client.force_authenticate(user=user, token=get_auth(user))
        return client


class UserAxisPermissionHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('user-axis-admin')
        self.target_user = PermissionHappyPathMixin.create_ce_user('user-axis-target')
        self.workspace = PermissionHappyPathMixin.create_workspace('user-axis-workspace')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        self.folder = ToolFolder.objects.create(
            id=str(uuid.uuid7()),
            name='User Axis Folder',
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            id=uuid.uuid7(),
            name='user-axis-tool',
            workspace_id=self.workspace.id,
            desc='user axis tool',
            code='print(1)',
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )

    def _endpoint(self):
        return (
            f'{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/'
            f'user/{self.target_user.id}/resource/TOOL'
        )

    def _seed_permission(self, permission_list=None, auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value):
        return WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
            auth_type=auth_type,
            permission_list=permission_list or [ResourcePermission.VIEW.value],
        )

    def test_admin_can_list_user_resource_permissions(self):
        self._seed_permission()

        response = self.client.get(self._endpoint(), {'name': self.tool.name})

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(len(payload['data']), 1)
        self.assertEqual(payload['data'][0]['auth_target_type'], 'TOOL')
        self.assertEqual(payload['data'][0]['permission'], 'VIEW')
        self.assertTrue(
            any(
                item['id'] == str(self.tool.id)
                and item['permission'] == 'VIEW'
                for item in payload['data']
            )
        )

    def test_admin_can_page_user_resource_permissions(self):
        self._seed_permission()

        response = self.client.get(f'{self._endpoint()}/1/20', {'name': self.tool.name})

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        self.assertEqual(payload['data']['records'][0]['permission'], 'VIEW')

    def test_admin_can_grant_view_permission_from_user_axis(self):
        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.tool.id), 'permission': 'VIEW'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [ResourcePermission.VIEW.value])

    def test_admin_can_grant_manage_permission_from_user_axis(self):
        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.tool.id), 'permission': 'MANAGE'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [
            ResourcePermission.MANAGE.value,
            ResourcePermission.VIEW.value,
        ])

    def test_admin_can_clear_permission_with_not_auth_from_user_axis(self):
        self._seed_permission()

        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.tool.id), 'permission': 'NOT_AUTH'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [])


class ApplicationUserAxisPermissionHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('app-user-axis-admin')
        self.target_user = PermissionHappyPathMixin.create_ce_user('app-user-axis-target')
        self.workspace = PermissionHappyPathMixin.create_workspace('app-user-axis-workspace')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        self.folder = ApplicationFolder.objects.create(
            id=str(uuid.uuid7()),
            name='App User Axis Folder',
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='app-user-axis-application',
            workspace_id=self.workspace.id,
            folder=self.folder,
            type=ApplicationTypeChoices.SIMPLE,
        )

    def _endpoint(self):
        return (
            f'{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/'
            f'user/{self.target_user.id}/resource/APPLICATION'
        )

    def _seed_permission(self, permission_list=None, auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value):
        return WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='APPLICATION',
            target=str(self.application.id),
            auth_type=auth_type,
            permission_list=permission_list or [ResourcePermission.VIEW.value],
        )

    def test_admin_can_grant_view_permission_for_application(self):
        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.application.id), 'permission': 'VIEW'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='APPLICATION',
            target=str(self.application.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [ResourcePermission.VIEW.value])

    def test_admin_can_clear_permission_with_not_auth_for_application(self):
        self._seed_permission()

        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.application.id), 'permission': 'NOT_AUTH'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='APPLICATION',
            target=str(self.application.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [])


class KnowledgeUserAxisPermissionHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('kb-user-axis-admin')
        self.target_user = PermissionHappyPathMixin.create_ce_user('kb-user-axis-target')
        self.workspace = PermissionHappyPathMixin.create_workspace('kb-user-axis-workspace')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        self.folder = KnowledgeFolder.objects.create(
            id=str(uuid.uuid7()),
            name='KB User Axis Folder',
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name='kb-user-axis-knowledge',
            workspace_id=self.workspace.id,
            folder=self.folder,
            type=KnowledgeType.BASE,
        )

    def _endpoint(self):
        return (
            f'{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/'
            f'user/{self.target_user.id}/resource/KNOWLEDGE'
        )

    def _seed_permission(self, permission_list=None, auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value):
        return WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='KNOWLEDGE',
            target=str(self.knowledge.id),
            auth_type=auth_type,
            permission_list=permission_list or [ResourcePermission.VIEW.value],
        )

    def test_admin_can_grant_view_permission_for_knowledge(self):
        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.knowledge.id), 'permission': 'VIEW'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='KNOWLEDGE',
            target=str(self.knowledge.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [ResourcePermission.VIEW.value])

    def test_admin_can_clear_permission_with_not_auth_for_knowledge(self):
        self._seed_permission()

        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.knowledge.id), 'permission': 'NOT_AUTH'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='KNOWLEDGE',
            target=str(self.knowledge.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [])


class ModelUserAxisPermissionHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('model-user-axis-admin')
        self.target_user = PermissionHappyPathMixin.create_ce_user('model-user-axis-target')
        self.workspace = PermissionHappyPathMixin.create_workspace('model-user-axis-workspace')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        self.model = Model.objects.create(
            id=uuid.uuid7(),
            name='model-user-axis-model',
            workspace_id=self.workspace.id,
            model_type='LLM',
            model_name='test-model',
            provider='test-provider',
            credential='{}',
        )

    def _endpoint(self):
        return (
            f'{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/user_resource_permission/'
            f'user/{self.target_user.id}/resource/MODEL'
        )

    def _seed_permission(self, permission_list=None, auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value):
        return WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='MODEL',
            target=str(self.model.id),
            auth_type=auth_type,
            permission_list=permission_list or [ResourcePermission.VIEW.value],
        )

    def test_admin_can_grant_view_permission_for_model(self):
        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.model.id), 'permission': 'VIEW'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='MODEL',
            target=str(self.model.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [ResourcePermission.VIEW.value])

    def test_admin_can_clear_permission_with_not_auth_for_model(self):
        self._seed_permission()

        response = self.client.put(
            self._endpoint(),
            [{'target_id': str(self.model.id), 'permission': 'NOT_AUTH'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='MODEL',
            target=str(self.model.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [])


class ResourceAxisPermissionHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('resource-axis-admin')
        self.target_user = PermissionHappyPathMixin.create_ce_user('resource-axis-target')
        self.workspace, _ = Workspace.objects.get_or_create(
            id='default',
            defaults={'name': 'default'},
        )
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        self.folder = ToolFolder.objects.create(
            id=str(uuid.uuid7()),
            name='Resource Axis Folder',
            user=self.admin,
            workspace_id=self.workspace.id,
        )
        self.tool = Tool.objects.create(
            id=uuid.uuid7(),
            name='resource-axis-tool',
            workspace_id=self.workspace.id,
            desc='resource axis tool',
            code='print(1)',
            scope=ToolScope.WORKSPACE,
            tool_type=ToolType.CUSTOM,
            folder=self.folder,
        )

    def _endpoint(self):
        return (
            f'{ADMIN_API_PREFIX}/workspace/{self.workspace.id}/resource_user_permission/'
            f'resource/{self.tool.id}/resource/TOOL'
        )

    def _seed_permission(self, permission_list=None, auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP.value):
        return WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
            auth_type=auth_type,
            permission_list=permission_list or [ResourcePermission.VIEW.value],
        )

    def test_admin_can_list_resource_user_permissions(self):
        self._seed_permission()

        response = self.client.get(self._endpoint(), {'username': self.target_user.username})

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(len(payload['data']), 1)
        self.assertEqual(payload['data'][0]['id'], str(self.target_user.id))
        self.assertEqual(payload['data'][0]['permission'], 'VIEW')

    def test_admin_can_page_resource_user_permissions(self):
        self._seed_permission()

        response = self.client.get(
            f'{self._endpoint()}/1/20',
            {'username': self.target_user.username},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        self.assertEqual(payload['data']['records'][0]['permission'], 'VIEW')

    def test_admin_can_grant_view_permission_from_resource_axis(self):
        response = self.client.put(
            self._endpoint(),
            [{'user_id': str(self.target_user.id), 'permission': 'VIEW'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [ResourcePermission.VIEW.value])

    def test_admin_can_clear_permission_with_not_auth_from_resource_axis(self):
        self._seed_permission()

        response = self.client.put(
            self._endpoint(),
            [{'user_id': str(self.target_user.id), 'permission': 'NOT_AUTH'}],
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)

        permission = WorkspaceUserResourcePermission.objects.get(
            workspace_id=self.workspace.id,
            user=self.target_user,
            auth_target_type='TOOL',
            target=str(self.tool.id),
        )
        self.assertEqual(permission.auth_type, ResourceAuthType.RESOURCE_PERMISSION_GROUP.value)
        self.assertEqual(permission.permission_list, [])


class WorkspaceRoleListHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('role-list-admin')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)

    def test_admin_can_retrieve_workspace_role_options(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/role_list/current_user')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], [
            {
                'id': 'USER',
                'name': 'USER',
                'type': 'USER',
            }
        ])


class WorkspaceRoleListDeniedTests(TestCase):
    def setUp(self):
        self.user = PermissionHappyPathMixin.create_ce_user('role-list-denied-user')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.user)

    def test_non_admin_cannot_access_role_list(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/role_list/current_user')

        self.assertEqual(response.status_code, 403)


class SystemRoleListHappyPathTests(TestCase):
    def setUp(self):
        self.admin = PermissionHappyPathMixin.create_admin_user('system-role-admin')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.admin)
        PermissionHappyPathMixin.create_ce_user('system-role-user')

    def test_admin_can_retrieve_system_role_list(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/system/role')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['custom_role'], [])
        self.assertEqual(
            [item['id'] for item in payload['data']['internal_role']],
            ['ADMIN', 'USER'],
        )
        self.assertEqual(
            payload['data']['internal_role'][0]['user_count'],
            User.objects.filter(role='ADMIN', is_active=True).count(),
        )
        self.assertEqual(
            payload['data']['internal_role'][1]['user_count'],
            User.objects.filter(role='USER', is_active=True).count(),
        )

    def test_admin_can_retrieve_system_role_permissions(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/system/role/ADMIN/permission')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'][0]['id'], 'ROLE')
        self.assertEqual(payload['data'][0]['children'][0]['id'], 'ROLE')
        self.assertEqual(
            [item['id'] for item in payload['data'][0]['children'][0]['permission']],
            [
                'ROLE:READ',
                'ROLE:READ+CREATE',
                'ROLE:READ+EDIT',
                'ROLE:READ+DELETE',
                'ROLE:READ+ADD_MEMBER',
                'ROLE:READ+REMOVE_MEMBER',
            ],
        )

    def test_admin_can_retrieve_system_role_members(self):
        response = self.client.get(
            f'{ADMIN_API_PREFIX}/system/role/USER/user_list/1/20',
            {'username': 'system-role-user'},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(payload['data']['records'][0]['username'], 'system-role-user')
        self.assertEqual(payload['data']['records'][0]['workspace_name'], '')


class SystemRoleListDeniedTests(TestCase):
    def setUp(self):
        self.user = PermissionHappyPathMixin.create_ce_user('system-role-denied-user')
        self.client = PermissionHappyPathMixin.setup_authenticated_client(self.user)

    def test_non_admin_cannot_access_system_role_list(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/system/role')

        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_system_role_permissions(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/system/role/ADMIN/permission')

        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_system_role_members(self):
        response = self.client.get(f'{ADMIN_API_PREFIX}/system/role/USER/user_list/1/20')

        self.assertEqual(response.status_code, 403)
