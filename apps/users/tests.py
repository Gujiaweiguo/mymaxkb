from importlib import import_module
from types import SimpleNamespace
from unittest.mock import patch

import uuid_utils.compat as uuid
from django.core import signing
from django.core.cache import cache
from django.test import RequestFactory, TestCase

from common.auth import authenticate as authenticate_module
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.auth.handle.impl.user_token import get_auth
from common.exception.app_exception import AppApiException, AppAuthenticationFailed
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SystemSetting, SettingType
from users.models import User
from users.serializers.login import LoginSerializer, system_get_key, system_version
from users.serializers.user import UserProfileSerializer, get_community_user_manage_response


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


class LoginSerializerContractTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="login-contract-admin@example.com",
            phone="",
            nick_name="Login Contract Admin",
            username="login-contract-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    @staticmethod
    def _get_model_side_effect(model_name):
        if model_name == "license_is_valid":
            return lambda: True
        return None

    def _create_login_auth_setting(
        self,
        *,
        max_attempts=1,
        failed_attempts=5,
        lock_time=10,
    ):
        SystemSetting.objects.create(
            type=SettingType.LOGIN_AUTH,
            meta={
                "default_value": "LOCAL",
                "login_methods": ["LOCAL"],
                "max_attempts": max_attempts,
                "failed_attempts": failed_attempts,
                "lock_time": lock_time,
            },
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model", return_value=None)
    def test_login_returns_token_for_active_local_admin(self, _get_model):
        result = LoginSerializer.login(
            {
                "username": self.admin_user.username,
                "password": "Admin123!",
            }
        )

        self.assertIn("token", result)
        token_payload = signing.loads(result["token"])
        self.assertEqual(token_payload["username"], self.admin_user.username)
        self.assertEqual(token_payload["id"], str(self.admin_user.id))
        self.assertEqual(
            token_payload["type"], AuthenticationType.SYSTEM_USER.value
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model", return_value=None)
    def test_login_rejects_wrong_password(self, _get_model):
        with self.assertRaises(AppApiException) as context:
            LoginSerializer.login(
                {
                    "username": self.admin_user.username,
                    "password": "WrongPassword",
                }
            )

        self.assertEqual(context.exception.code, 500)
        self.assertEqual(
            str(context.exception.message), "The username or password is incorrect"
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model", return_value=None)
    def test_login_rejects_disabled_user_with_correct_password(self, _get_model):
        self.admin_user.is_active = False
        self.admin_user.save(update_fields=["is_active"])

        with self.assertRaises(AppApiException) as context:
            LoginSerializer.login(
                {
                    "username": self.admin_user.username,
                    "password": "Admin123!",
                }
            )

        self.assertEqual(context.exception.code, 1005)
        self.assertEqual(
            str(context.exception.message),
            "The user has been disabled, please contact the administrator!",
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_rejects_locked_account_when_lock_cache_is_set(self, get_model):
        get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(lock_time=7)
        cache.set(
            system_get_key(f"system_{self.admin_user.username}_lock"),
            1,
            timeout=420,
            version=system_version,
        )

        with self.assertRaises(AppApiException) as context:
            LoginSerializer.login(
                {
                    "username": self.admin_user.username,
                    "password": "Admin123!",
                }
            )

        self.assertEqual(context.exception.code, 1005)
        self.assertEqual(
            str(context.exception.message),
            "This account has been locked for 7 minutes, please try again later",
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_requires_captcha_after_max_attempts_threshold(self, get_model):
        get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=2)
        cache.set(
            system_get_key(f"system_{self.admin_user.username}"),
            2,
            timeout=600,
            version=system_version,
        )

        with self.assertRaises(AppApiException) as context:
            LoginSerializer.login(
                {
                    "username": self.admin_user.username,
                    "password": "Admin123!",
                }
            )

        self.assertEqual(context.exception.code, 1005)
        self.assertEqual(str(context.exception.message), "Captcha is required")

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_rejects_invalid_captcha_when_required(self, get_model):
        get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)
        cache.set(
            system_get_key(f"system_{self.admin_user.username}"),
            1,
            timeout=600,
            version=system_version,
        )
        cache.set(
            Cache_Version.CAPTCHA.get_key(captcha=f"system_{self.admin_user.username}"),
            "right",
            timeout=300,
            version=Cache_Version.CAPTCHA.get_version(),
        )

        with self.assertRaises(AppApiException) as context:
            LoginSerializer.login(
                {
                    "username": self.admin_user.username,
                    "password": "Admin123!",
                    "captcha": "wrong",
                }
            )

        self.assertEqual(context.exception.code, 1005)
        self.assertEqual(
            str(context.exception.message), "Captcha code error or expiration"
        )

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_allows_correct_captcha_after_threshold(self, get_model):
        get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)
        cache.set(
            system_get_key(f"system_{self.admin_user.username}"),
            1,
            timeout=600,
            version=system_version,
        )
        cache.set(
            Cache_Version.CAPTCHA.get_key(captcha=f"system_{self.admin_user.username}"),
            "right",
            timeout=300,
            version=Cache_Version.CAPTCHA.get_version(),
        )

        result = LoginSerializer.login(
            {
                "username": self.admin_user.username,
                "password": "Admin123!",
                "captcha": "RIGHT",
            }
        )

        self.assertIn("token", result)


class RequirePasswordChangeAuthContractTests(TestCase):
    class StubHandle:
        def __init__(self, auth_result):
            self.auth_result = auth_result

        def support(self, request, token, get_token_details):
            return True

        def handle(self, request, token, get_token_details):
            return self.auth_result

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="password-change-user@example.com",
            phone="",
            nick_name="Password Change User",
            username="password-change-user",
            password=password_encrypt("Password1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
            require_password_change=True,
        )
        self.auth = SimpleNamespace(role_list=["ADMIN"], permission_list=[])

    def _authenticate(self, auth_class, path: str):
        handle = self.StubHandle((self.user, self.auth))
        request = self.request_factory.get(path, HTTP_AUTHORIZATION="Bearer test-token")
        if auth_class is authenticate_module.TokenAuth:
            patch_target = "handles"
        elif auth_class is authenticate_module.ChatTokenAuth:
            patch_target = "chat_handles"
        else:
            patch_target = "all_handles"

        with patch.object(authenticate_module, patch_target, [handle]):
            return auth_class().authenticate(request)

    def test_token_auth_blocks_flagged_user_on_non_whitelisted_path(self):
        with self.assertRaises(AppAuthenticationFailed) as context:
            self._authenticate(authenticate_module.TokenAuth, "/admin/api/application/list")

        self.assertEqual(context.exception.code, 1002)
        self.assertEqual(
            str(context.exception.message), "Password change required before continuing"
        )

    def test_all_token_auth_blocks_flagged_user_on_non_whitelisted_path(self):
        with self.assertRaises(AppAuthenticationFailed) as context:
            self._authenticate(
                authenticate_module.AllTokenAuth,
                "/admin/api/workspace/default/application/list",
            )

        self.assertEqual(context.exception.code, 1002)
        self.assertEqual(
            str(context.exception.message), "Password change required before continuing"
        )

    def test_chat_token_auth_blocks_flagged_user_on_non_whitelisted_path(self):
        with self.assertRaises(AppAuthenticationFailed) as context:
            self._authenticate(authenticate_module.ChatTokenAuth, "/api/chat/open")

        self.assertEqual(context.exception.code, 1002)
        self.assertEqual(
            str(context.exception.message), "Password change required before continuing"
        )

    def test_password_change_gate_allows_whitelisted_paths(self):
        for auth_class in (
            authenticate_module.TokenAuth,
            authenticate_module.ChatTokenAuth,
            authenticate_module.AllTokenAuth,
        ):
            for allowed_path in authenticate_module.PASSWORD_CHANGE_ALLOWED_PATHS:
                with self.subTest(auth_class=auth_class.__name__, allowed_path=allowed_path):
                    auth_result = self._authenticate(auth_class, f"/admin/api{allowed_path}")

                    self.assertEqual(auth_result, (self.user, self.auth))


class UserProfilePasswordChangeSignalTests(TestCase):
    @patch("users.serializers.user.get_workspace_list_by_user", return_value=["default"])
    @patch("users.serializers.user.DatabaseModelManage.get_model", return_value=None)
    def test_profile_sets_is_edit_password_true_for_local_flagged_user(
        self, _get_model, _get_workspace_list
    ):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="local-flagged@example.com",
            phone="",
            nick_name="Local Flagged",
            username="local-flagged",
            password=password_encrypt("Password1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
            require_password_change=True,
        )

        profile = UserProfileSerializer.profile(
            user, SimpleNamespace(role_list=["ADMIN"], permission_list=[])
        )

        self.assertTrue(profile["is_edit_password"])

    @patch("users.serializers.user.get_workspace_list_by_user", return_value=["default"])
    @patch("users.serializers.user.DatabaseModelManage.get_model", return_value=None)
    def test_profile_sets_is_edit_password_false_for_non_local_flagged_user(
        self, _get_model, _get_workspace_list
    ):
        user = User.objects.create(
            id=uuid.uuid7(),
            email="ldap-flagged@example.com",
            phone="",
            nick_name="LDAP Flagged",
            username="ldap-flagged",
            password=password_encrypt("Password1!"),
            role="ADMIN",
            source="LDAP",
            is_active=True,
            require_password_change=True,
        )

        profile = UserProfileSerializer.profile(
            user, SimpleNamespace(role_list=["ADMIN"], permission_list=[])
        )

        self.assertFalse(profile["is_edit_password"])


class BootstrapPasswordFlagMigrationContractTests(TestCase):
    def setUp(self):
        self.migration_module = import_module(
            "users.migrations.0002_user_require_password_change"
        )
        self.apps_stub = SimpleNamespace(get_model=lambda app_label, model_name: User)

    def _create_user(self, username: str, password: str) -> User:
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=username,
            username=username,
            password=password,
            role="ADMIN",
            source="LOCAL",
            is_active=True,
            require_password_change=False,
        )

    def test_mark_bootstrap_password_change_flags_legacy_default_hash(self):
        user = self._create_user(
            "legacy-bootstrap-user",
            self.migration_module.LEGACY_DEFAULT_PASSWORD_HASH,
        )

        with patch("maxkb.const.CONFIG", {"DEFAULT_PASSWORD": "AnotherPassword123!"}):
            self.migration_module.mark_bootstrap_password_change(self.apps_stub, None)

        user.refresh_from_db()
        self.assertTrue(user.require_password_change)

    def test_mark_bootstrap_password_change_flags_configured_bootstrap_hash(self):
        user = self._create_user(
            "configured-bootstrap-user",
            self.migration_module._password_hash("BootstrapPassword123!"),
        )

        with patch("maxkb.const.CONFIG", {"DEFAULT_PASSWORD": "BootstrapPassword123!"}):
            self.migration_module.mark_bootstrap_password_change(self.apps_stub, None)

        user.refresh_from_db()
        self.assertTrue(user.require_password_change)

    def test_mark_bootstrap_password_change_ignores_placeholder_bootstrap_password(self):
        user = self._create_user(
            "placeholder-bootstrap-user",
            self.migration_module._password_hash("change_me_bootstrap_admin_password"),
        )

        with patch(
            "maxkb.const.CONFIG", {"DEFAULT_PASSWORD": "change_me_bootstrap_admin_password"}
        ):
            self.migration_module.mark_bootstrap_password_change(self.apps_stub, None)

        user.refresh_from_db()
        self.assertFalse(user.require_password_change)
