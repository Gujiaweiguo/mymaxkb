import json
from types import SimpleNamespace

import uuid_utils.compat as uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from system_manage.views.appearance_setting import (
    AppearanceSettingOperateView,
    AppearanceSettingView,
)
from users.models import User


class AppearanceSettingTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin-appearance@example.com",
            phone="",
            nick_name="admin-appearance",
            username="admin-appearance",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="user-appearance@example.com",
            phone="",
            nick_name="user-appearance",
            username="user-appearance",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.USER.name,
            source="LOCAL",
            is_active=True,
        )
        self.admin_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )
        self.user_token = SimpleNamespace(
            role_list=[RoleConstants.USER.value.__str__()],
            permission_list=[],
        )

    def test_appearance_setting_get_returns_defaults(self):
        request = self.factory.get("/display/info")
        response = AppearanceSettingView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["theme"], "#3370FF")
        self.assertEqual(payload["data"]["title"], "MaxKB")

    def test_appearance_setting_update_persists_values(self):
        request = self.factory.put(
            "/display/update",
            data={
                "theme": "#00B69D",
                "title": "Branded MaxKB",
                "slogan": "Custom slogan",
                "showForum": False,
                "icon": SimpleUploadedFile(
                    "icon.png", b"png-bytes", content_type="image/png"
                ),
            },
            format="multipart",
        )
        force_authenticate(request, user=self.admin, token=self.admin_token)

        response = AppearanceSettingOperateView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["theme"], "#00B69D")
        self.assertEqual(payload["data"]["title"], "Branded MaxKB")
        self.assertFalse(payload["data"]["showForum"])
        self.assertTrue(payload["data"]["icon"].startswith("./oss/file/"))

        setting = SystemSetting.objects.get(type=SettingType.APPEARANCE)
        self.assertEqual(setting.meta["title"], "Branded MaxKB")

    def test_appearance_setting_update_requires_admin_permission(self):
        request = self.factory.put(
            "/display/update",
            data={"title": "Nope"},
            format="multipart",
        )
        force_authenticate(request, user=self.user, token=self.user_token)

        response = AppearanceSettingOperateView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(payload["code"], 403)
