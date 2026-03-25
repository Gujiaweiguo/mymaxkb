import json
from types import SimpleNamespace

import uuid_utils.compat as uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationTypeChoices,
)
from application.views.application_access_token import AccessToken
from common.constants.permission_constants import (
    Permission,
    RoleConstants,
    Group,
    Operate,
    ResourcePermissionConst,
)
from common.utils.common import password_encrypt
from system_manage.models import Workspace
from users.models import User


class ApplicationAccessTokenTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@app-access-token.test",
            phone="",
            nick_name="admin-app-access-token",
            username="admin-app-access-token",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-app-access-token", name="workspace-app-access-token"
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-app-access-token",
            name="folder-app-access-token",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="app-display",
            desc="app-display",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[
                Permission(
                    group=Group.APPLICATION_OVERVIEW,
                    operate=Operate.ACCESS,
                    resource_path=f"/WORKSPACE/{self.workspace.id}/APPLICATION/{self.application.id}",
                ),
                Permission(
                    group=Group.APPLICATION,
                    operate=Operate.READ,
                    resource_path=f"/WORKSPACE/{self.workspace.id}/APPLICATION/{self.application.id}",
                ),
            ],
        )

    def test_access_token_get_includes_application_icon(self):
        request = self.factory.get(
            f"/workspace/{self.workspace.id}/application/{self.application.id}/access_token"
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = AccessToken.as_view()(
            request,
            workspace_id=self.workspace.id,
            application_id=str(self.application.id),
        )
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["icon"], "./favicon.ico")

    def test_access_token_edit_persists_application_icon(self):
        request = self.factory.put(
            f"/workspace/{self.workspace.id}/application/{self.application.id}/access_token",
            data={
                "show_source": True,
                "show_exec": True,
                "language": "en-US",
                "icon": SimpleUploadedFile(
                    "icon.png", b"icon-bytes", content_type="image/png"
                ),
            },
            format="multipart",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = AccessToken.as_view()(
            request,
            workspace_id=self.workspace.id,
            application_id=str(self.application.id),
        )
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["data"]["icon"].startswith("./oss/file/"))
        self.application.refresh_from_db()
        self.assertEqual(self.application.icon, payload["data"]["icon"])

        access_token = ApplicationAccessToken.objects.get(
            application_id=self.application.id
        )
        self.assertTrue(access_token.show_source)
        self.assertTrue(access_token.show_exec)
        self.assertEqual(access_token.language, "en-US")
