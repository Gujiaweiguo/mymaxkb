import uuid_utils.compat as uuid
from django.test import TestCase

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_api_key import ApplicationApiKey
from application.serializers.application_api_key import ApplicationKeySerializer
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import Workspace
from users.models import User


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
