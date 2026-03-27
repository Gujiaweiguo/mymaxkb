from unittest.mock import patch

import uuid_utils.compat as uuid
from django.core.cache import cache
from django.test import TestCase

from common.auth.handle.impl.user_token import get_auth
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SystemSetting, SettingType
from users.models import User
from users.serializers.login import LoginSerializer
from users.serializers.user import get_community_user_manage_response


class CommunityEditionAuthFallbackTests(TestCase):
    def setUp(self):
        cache.clear()

    def create_user(self, role: str, username: str) -> User:
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role=role,
            source="LOCAL",
            is_active=True,
        )

    @patch(
        "common.auth.handle.impl.user_token.DatabaseModelManage.get_model",
        return_value=None,
    )
    def test_ce_user_get_auth_includes_default_system_and_workspace_permissions(
        self, _get_model
    ):
        user = self.create_user(RoleConstants.USER.name, "ce-user")

        auth = get_auth(user)

        self.assertIn(RoleConstants.USER.name, auth.role_list)
        self.assertIn("USER:/WORKSPACE/default", auth.role_list)
        self.assertIn(
            PermissionConstants.USER_READ.value.__str__(), auth.permission_list
        )
        self.assertIn(
            f"{PermissionConstants.APPLICATION_READ.value}:/WORKSPACE/default",
            auth.permission_list,
        )
        self.assertNotIn(
            PermissionConstants.USER_CREATE.value.__str__(), auth.permission_list
        )

    @patch(
        "common.auth.handle.impl.user_token.DatabaseModelManage.get_model",
        return_value=None,
    )
    def test_ce_admin_get_auth_includes_admin_system_permissions(self, _get_model):
        user = self.create_user(RoleConstants.ADMIN.name, "ce-admin")

        auth = get_auth(user)

        self.assertIn(RoleConstants.ADMIN.name, auth.role_list)
        self.assertIn("WORKSPACE_MANAGE:/WORKSPACE/default", auth.role_list)
        self.assertIn(
            PermissionConstants.USER_CREATE.value.__str__(), auth.permission_list
        )
        self.assertIn(
            PermissionConstants.ROLE_READ.value.__str__(), auth.permission_list
        )

    @patch(
        "users.serializers.login.DatabaseModelManage.get_model",
        return_value=None,
    )
    def test_login_serializer_reads_ce_login_auth_setting_from_system_setting(
        self, _get_model
    ):
        SystemSetting.objects.create(
            type=SettingType.LOGIN_AUTH,
            meta={
                "default_value": "LOCAL",
                "login_methods": ["LOCAL"],
                "max_attempts": 3,
                "failed_attempts": 6,
                "lock_time": 15,
            },
        )

        auth_setting = LoginSerializer.get_auth_setting()

        self.assertEqual(auth_setting.get("default_value"), "LOCAL")
        self.assertEqual(auth_setting.get("login_methods"), ["LOCAL"])
        self.assertEqual(auth_setting.get("max_attempts"), 3)

    def test_ce_user_manage_response_includes_stable_role_metadata(self):
        user = self.create_user(RoleConstants.USER.name, "ce-user-manage")

        response = get_community_user_manage_response(user)

        self.assertEqual(response.get("role_name"), [RoleConstants.USER.name])
        self.assertEqual(
            response.get("role_setting"),
            [{"role_id": RoleConstants.USER.name, "workspace_ids": ["default"]}],
        )
        self.assertEqual(
            response.get("role_workspace"),
            {RoleConstants.USER.name: ["default"]},
        )

    def test_ce_admin_manage_response_marks_admin_workspace_scope_consistently(self):
        user = self.create_user(RoleConstants.ADMIN.name, "ce-admin-manage")

        response = get_community_user_manage_response(user)

        self.assertEqual(response.get("role_name"), [RoleConstants.ADMIN.name])
        self.assertEqual(
            response.get("role_setting"),
            [{"role_id": RoleConstants.ADMIN.name, "workspace_ids": ["None"]}],
        )
        self.assertEqual(
            response.get("role_workspace"),
            {RoleConstants.ADMIN.name: ["None"]},
        )


class UserModelTests(TestCase):
    def test_user_creation_with_valid_data(self):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="test@example.com",
            phone="1234567890",
            nick_name="Test User",
            username="testuser",
            password=password_encrypt("Password1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "USER")
        self.assertTrue(user.is_active)

    def test_user_str_representation(self):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="strtest@example.com",
            phone="",
            nick_name="Str Test",
            username="strtest",
            password=password_encrypt("Password1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        self.assertEqual(str(user), "strtest")

    def test_user_role_choices(self):
        valid_roles = ["ADMIN", "USER"]
        for role in valid_roles:
            user = User.objects.create(
                id=uuid.uuid7(),
                email=f"{role.lower()}@example.com",
                phone="",
                nick_name=f"{role} User",
                username=f"{role.lower()}user",
                password=password_encrypt("Password1!"),
                role=role,
                source="LOCAL",
                is_active=True,
            )
            self.assertEqual(user.role, role)


class UserSerializerTests(TestCase):
    def test_user_list_serializer_returns_expected_fields(self):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="serializer@example.com",
            phone="1234567890",
            nick_name="Serializer Test",
            username="serializertest",
            password=password_encrypt("Password1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        from users.serializers.user import UserInstanceSerializer

        serializer = UserInstanceSerializer(user)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("username", data)
        self.assertIn("email", data)
        self.assertIn("role", data)
        self.assertEqual(data["username"], "serializertest")
        self.assertEqual(data["email"], "serializer@example.com")


class LoginSerializerTests(TestCase):
    def test_login_serializer_validates_required_fields(self):
        from users.serializers.login import LoginRequest

        invalid_data = {"username": "test"}
        serializer = LoginRequest(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_login_serializer_validates_correct_data(self):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="login@example.com",
            phone="",
            nick_name="Login Test",
            username="logintest",
            password=password_encrypt("Password1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        from users.serializers.login import LoginRequest

        valid_data = {
            "username": "logintest",
            "password": "Password1!",
            "login_type": "LOCAL",
        }
        serializer = LoginRequest(data=valid_data)
        self.assertTrue(serializer.is_valid())
