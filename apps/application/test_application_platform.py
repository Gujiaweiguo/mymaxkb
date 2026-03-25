import json
from types import SimpleNamespace

import uuid_utils.compat as uuid
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.views.application_platform import (
    SystemResourceApplicationPlatformConfigView,
    SystemResourceApplicationPlatformStatusView,
)
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting, Workspace
from users.models import User


class ApplicationPlatformTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-app-platform",
            username="admin-app-platform",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )
        self.workspace = Workspace.objects.create(
            id="workspace-app-platform", name="workspace-app-platform"
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-app-platform",
            name="folder-app-platform",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="external-app",
            desc="external-app",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_status_reports_provider_not_ready_until_system_validation(self):
        save_request = self.factory.post(
            f"/system/resource/application/{self.application.id}/platform/lark",
            data={
                "app_id": "app",
                "app_secret": "secret",
                "verification_token": "token",
            },
            format="json",
        )
        force_authenticate(save_request, user=self.admin, token=self.auth_token)
        save_response = SystemResourceApplicationPlatformConfigView.as_view()(
            save_request,
            application_id=str(self.application.id),
            platform_type="lark",
        )
        save_payload = json.loads(save_response.content)
        self.assertEqual(save_response.status_code, 200)
        self.assertFalse(save_payload["data"]["is_valid"])
        self.assertEqual(save_payload["data"]["state"], "failed")

        SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                "lark": {
                    "config": {
                        "app_key": "provider-app",
                        "app_secret": "provider-secret",
                    },
                    "is_valid": True,
                    "is_active": True,
                    "state": "enabled",
                    "failure_reason": "",
                }
            },
        )

        status_request = self.factory.get(
            f"/system/resource/application/{self.application.id}/platform/status"
        )
        force_authenticate(status_request, user=self.admin, token=self.auth_token)
        status_response = SystemResourceApplicationPlatformStatusView.as_view()(
            status_request,
            application_id=str(self.application.id),
        )
        status_payload = json.loads(status_response.content)
        self.assertTrue(status_payload["data"]["lark"]["is_valid"])
        self.assertEqual(status_payload["data"]["lark"]["state"], "ready")

    def test_activation_is_blocked_when_provider_not_ready(self):
        save_request = self.factory.post(
            f"/system/resource/application/{self.application.id}/platform/dingtalk",
            data={"client_id": "client", "client_secret": "secret"},
            format="json",
        )
        force_authenticate(save_request, user=self.admin, token=self.auth_token)
        SystemResourceApplicationPlatformConfigView.as_view()(
            save_request,
            application_id=str(self.application.id),
            platform_type="dingtalk",
        )

        toggle_request = self.factory.post(
            f"/system/resource/application/{self.application.id}/platform/status",
            data={"type": "dingtalk", "status": True},
            format="json",
        )
        force_authenticate(toggle_request, user=self.admin, token=self.auth_token)
        toggle_response = SystemResourceApplicationPlatformStatusView.as_view()(
            toggle_request,
            application_id=str(self.application.id),
        )
        toggle_payload = json.loads(toggle_response.content)
        self.assertEqual(toggle_response.status_code, 200)
        self.assertEqual(toggle_payload["code"], 500)

    def test_dingtalk_status_requires_callback_credentials_for_readiness(self):
        SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                "dingtalk": {
                    "config": {
                        "corp_id": "corp-id",
                        "app_key": "app-key",
                        "app_secret": "app-secret",
                    },
                    "is_valid": True,
                    "is_active": True,
                    "state": "enabled",
                    "failure_reason": "",
                }
            },
        )

        incomplete_request = self.factory.post(
            f"/system/resource/application/{self.application.id}/platform/dingtalk",
            data={"client_id": "client", "client_secret": "secret"},
            format="json",
        )
        force_authenticate(incomplete_request, user=self.admin, token=self.auth_token)
        incomplete_response = SystemResourceApplicationPlatformConfigView.as_view()(
            incomplete_request,
            application_id=str(self.application.id),
            platform_type="dingtalk",
        )
        incomplete_payload = json.loads(incomplete_response.content)

        self.assertEqual(incomplete_response.status_code, 200)
        self.assertFalse(incomplete_payload["data"]["is_valid"])
        self.assertIn("token", incomplete_payload["data"]["failure_reason"].lower())
        self.assertIn("encoding_aes_key", incomplete_payload["data"]["failure_reason"])

        complete_request = self.factory.post(
            f"/system/resource/application/{self.application.id}/platform/dingtalk",
            data={
                "client_id": "client",
                "client_secret": "secret",
                "token": "callback-token",
                "encoding_aes_key": "callback-aes-key",
            },
            format="json",
        )
        force_authenticate(complete_request, user=self.admin, token=self.auth_token)
        complete_response = SystemResourceApplicationPlatformConfigView.as_view()(
            complete_request,
            application_id=str(self.application.id),
            platform_type="dingtalk",
        )
        complete_payload = json.loads(complete_response.content)

        self.assertEqual(complete_response.status_code, 200)
        self.assertTrue(complete_payload["data"]["is_valid"])
        self.assertEqual(complete_payload["data"]["state"], "ready")
