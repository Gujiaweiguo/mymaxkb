import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_api_key import ApplicationApiKey
from application.serializers.application_api_key import ApplicationKeySerializer
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from maxkb.const import CONFIG
from system_manage.models import Workspace
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


class ApplicationApiKeyMaskingTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@app-api-key-mask.test",
            phone="",
            nick_name="admin-app-api-key-mask",
            username="admin-app-api-key-mask",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-app-api-key-mask",
            name="workspace-app-api-key-mask",
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-app-api-key-mask",
            name="folder-app-api-key-mask",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="app-api-key-mask",
            desc="app-api-key-mask",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
        )

    def _serializer(self):
        return ApplicationKeySerializer(data={"application_id": str(self.application.id)})

    def test_generate_returns_full_secret_key_once(self):
        result = self._serializer().generate()

        self.assertTrue(result["secret_key"].startswith("agent-"))
        self.assertNotIn("******", result["secret_key"])
        self.assertEqual(len(result["secret_key"]), len("agent-") + 32)

    def test_page_masks_application_secret_key_after_creation(self):
        created = self._serializer().generate()

        page = self._serializer().page(1, 20)

        self.assertEqual(page["total"], 1)
        record = page["records"][0]
        self.assertEqual(record["id"], created["id"])
        self.assertNotEqual(record["secret_key"], created["secret_key"])
        self.assertIn("******", record["secret_key"])
        self.assertEqual(
            record["secret_key"],
            f"{created['secret_key'][:8]}******{created['secret_key'][-4:]}",
        )

        stored = ApplicationApiKey.objects.get(id=created["id"])
        self.assertEqual(stored.secret_key, created["secret_key"])


class SystemResourceApplicationApiKeyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email='admin@app-api-key-system-resource.test',
            phone='',
            nick_name='admin-app-api-key-system-resource',
            username='admin-app-api-key-system-resource',
            password=password_encrypt('Secret1!'),
            role=RoleConstants.ADMIN.name,
            source='LOCAL',
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id='workspace-app-api-key-system-resource',
            name='workspace-app-api-key-system-resource',
        )
        self.folder = ApplicationFolder.objects.create(
            id='folder-app-api-key-system-resource',
            name='folder-app-api-key-system-resource',
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='app-api-key-system-resource',
            desc='app-api-key-system-resource',
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
        )
        set_system_user_auth(self.client, self.admin)

    def test_system_resource_create_and_page_application_key(self):
        create_response = self.client.post(
            f'/admin/api/system/resource/application/{self.application.id}/application_key'
        )

        self.assertEqual(create_response.status_code, 200)
        created = create_response.json()['data']
        self.assertTrue(created['secret_key'].startswith('agent-'))

        page_response = self.client.get(
            f'/admin/api/system/resource/application/{self.application.id}/application_key/1/20'
        )

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_response.json()['data']['total'], 1)
        record = page_response.json()['data']['records'][0]
        self.assertEqual(record['id'], created['id'])
        self.assertIn('******', record['secret_key'])

    def test_system_resource_edit_and_delete_application_key(self):
        created = self.client.post(
            f'/admin/api/system/resource/application/{self.application.id}/application_key'
        ).json()['data']

        edit_response = self.client.put(
            f"/admin/api/system/resource/application/{self.application.id}/application_key/{created['id']}",
            {'is_active': False},
            format='json',
        )

        self.assertEqual(edit_response.status_code, 200)
        api_key = ApplicationApiKey.objects.get(id=created['id'])
        self.assertFalse(api_key.is_active)

        delete_response = self.client.delete(
            f"/admin/api/system/resource/application/{self.application.id}/application_key/{created['id']}"
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(ApplicationApiKey.objects.filter(id=created['id']).exists())
