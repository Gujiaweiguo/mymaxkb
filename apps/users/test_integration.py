import json
import uuid_utils.compat as uuid
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from common.constants.cache_version import Cache_Version
from common.auth.handle.impl.user_token import get_auth
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting
from users.models import User


ADMIN_API_PREFIX = "/admin/api"


class UserAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_username = "users-int-admin"
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username=self.admin_username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="user@example.com",
            phone="",
            nick_name="Regular User",
            username="testuser",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "Admin123!", "login_type": "LOCAL"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("token", data.get("data", {}))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "WrongPassword", "login_type": "LOCAL"},
            format="json",
        )

        data = json.loads(response.content)
        self.assertNotIn("token", data.get("data") or {})

    def test_login_with_missing_fields(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username},
            format="json",
        )

        data = json.loads(response.content)
        self.assertNotIn("token", data.get("data") or {})

    def test_get_user_list_requires_auth(self):
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage")

        self.assertNotEqual(response.status_code, 200)

    def test_get_user_list_with_auth(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.regular_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user/profile")

        self.assertEqual(response.status_code, 200)

    def test_user_manage_page(self):
        self.client.force_authenticate(user=self.admin_user, token="test-token")
        response = self.client.get(f"{ADMIN_API_PREFIX}/user_manage/1/20")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)


class UserProfileContractIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="profile-user@example.com",
            phone="",
            nick_name="Profile User",
            username="profile-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
            language="zh-CN",
            require_password_change=False,
        )
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="profile-admin@example.com",
            phone="",
            nick_name="Profile Admin",
            username="profile-admin",
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
            language="en-US",
            require_password_change=True,
        )

    def test_profile_returns_current_user_contract(self):
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

        response = self.client.get(f"{ADMIN_API_PREFIX}/user/profile")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        data = payload["data"]
        self.assertEqual(str(data["id"]), str(self.user.id))
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["nick_name"], self.user.nick_name)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["source"], self.user.source)
        self.assertEqual(data["language"], self.user.language)
        self.assertIn("USER", data["role"])
        self.assertEqual(data["role_name"], ["USER"])
        self.assertEqual(data["workspace_list"], [{"id": "default", "name": "default"}])
        self.assertIsInstance(data["permissions"], list)
        self.assertIn("APPLICATION:READ", data["permissions"])
        self.assertFalse(data["is_edit_password"])

    def test_profile_sets_password_change_flag_for_local_admin(self):
        self.client.force_authenticate(user=self.admin, token=get_auth(self.admin))

        response = self.client.get(f"{ADMIN_API_PREFIX}/user/profile")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        data = payload["data"]
        self.assertEqual(str(data["id"]), str(self.admin.id))
        self.assertIn("ADMIN", data["role"])
        self.assertEqual(data["role_name"], ["ADMIN"])
        self.assertEqual(data["workspace_list"], [{"id": "default", "name": "default"}])
        self.assertTrue(data["is_edit_password"])


class LoginContractIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_username = "login-contract-admin"
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="login-contract-admin@example.com",
            phone="",
            nick_name="Login Contract Admin",
            username=self.admin_username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_login_returns_token_for_active_local_admin(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "Admin123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data.get("code"), 200)
        self.assertIn("token", data.get("data", {}))

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "WrongPassword"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data.get("code"), 500)
        self.assertEqual(
            data.get("message"), "The username or password is incorrect"
        )
        self.assertNotIn("token", data.get("data") or {})

    def test_login_rejects_disabled_user(self):
        self.admin_user.is_active = False
        self.admin_user.save(update_fields=["is_active"])

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "Admin123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data.get("code"), 1005)
        self.assertEqual(
            data.get("message"),
            "The user has been disabled, please contact the administrator!",
        )
        self.assertNotIn("token", data.get("data") or {})

    def test_logout_clears_cached_token_and_returns_success(self):
        login_response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.admin_username, "password": "Admin123!"},
            format="json",
        )
        token = json.loads(login_response.content)["data"]["token"]
        version, get_key = Cache_Version.TOKEN.value
        self.assertEqual(cache.get(get_key(token), version=version).id, self.admin_user.id)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        logout_response = self.client.post(f"{ADMIN_API_PREFIX}/user/logout")

        self.assertEqual(logout_response.status_code, 200)
        payload = json.loads(logout_response.content)
        self.assertEqual(payload.get("code"), 200)
        self.assertTrue(payload.get("data"))
        self.assertIsNone(cache.get(get_key(token), version=version))

    def test_logout_without_auth_returns_401(self):
        response = self.client.post(f"{ADMIN_API_PREFIX}/user/logout")

        self.assertEqual(response.status_code, 401)


class CaptchaAndCheckCodeContractIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "captcha-contract-admin"
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="captcha-contract-admin@example.com",
            phone="",
            nick_name="Captcha Contract Admin",
            username=self.username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        version, fail_key = self._system_fail_key()
        cache.delete(fail_key, version=version)
        captcha_version, captcha_key = self._captcha_key()
        cache.delete(captcha_key, version=captcha_version)
        register_version, register_key = self._check_code_key("test@example.com", "register")
        cache.delete(register_key, version=register_version)
        reset_version, reset_key = self._check_code_key("test@example.com", "reset_password")
        cache.delete(reset_key, version=reset_version)

    def _create_login_auth_setting(self, *, max_attempts=1, failed_attempts=5, lock_time=10):
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

    def _system_fail_key(self):
        version, get_key = Cache_Version.SYSTEM.value
        return version, get_key(f"system_{self.username}")

    def _captcha_key(self):
        return (
            Cache_Version.CAPTCHA.get_version(),
            Cache_Version.CAPTCHA.get_key(captcha=f"system_{self.username}"),
        )

    def _check_code_key(self, email: str, code_type: str):
        version, get_key = Cache_Version.SYSTEM.value
        return version, get_key(f"{email}:{code_type}")

    @staticmethod
    def _get_model_side_effect(model_name):
        if model_name == "license_is_valid":
            return lambda: True
        return None

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_captcha_endpoint_returns_base64_image_when_needed(self, _get_model):
        _get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)
        version, fail_key = self._system_fail_key()
        cache.set(fail_key, 1, timeout=600, version=version)

        response = self.client.get(f"{ADMIN_API_PREFIX}/user/captcha?username={self.username}")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertTrue(payload["data"]["captcha"].startswith("data:image/png;base64,"))
        captcha_version, captcha_key = self._captcha_key()
        captcha_value = cache.get(captcha_key, version=captcha_version)
        self.assertIsNotNone(captcha_value)
        self.assertEqual(captcha_value, captcha_value.lower())

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_captcha_endpoint_returns_empty_when_not_needed(self, _get_model):
        _get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)

        response = self.client.get(f"{ADMIN_API_PREFIX}/user/captcha?username={self.username}")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"]["captcha"], "")

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_rejects_missing_captcha_when_required(self, _get_model):
        _get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)
        version, fail_key = self._system_fail_key()
        cache.set(fail_key, 1, timeout=600, version=version)

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.username, "password": "Admin123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 1005)
        self.assertEqual(payload["message"], "Captcha is required")

    @patch("users.serializers.login.DatabaseModelManage.get_model")
    def test_login_accepts_correct_captcha_case_insensitive(self, _get_model):
        _get_model.side_effect = self._get_model_side_effect
        self._create_login_auth_setting(max_attempts=1)
        version, fail_key = self._system_fail_key()
        cache.set(fail_key, 1, timeout=600, version=version)
        captcha_version, captcha_key = self._captcha_key()
        cache.set(captcha_key, "right", timeout=300, version=captcha_version)

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/login",
            {"username": self.username, "password": "Admin123!", "captcha": "RIGHT"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertIn("token", payload["data"])

    def test_check_code_accepts_valid_code(self):
        version, cache_key = self._check_code_key("test@example.com", "register")
        cache.set(cache_key, "654321", timeout=1800, version=version)

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/check_code",
            {"email": "test@example.com", "code": "654321", "type": "register"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertTrue(payload["data"])

    def test_check_code_rejects_wrong_code(self):
        version, cache_key = self._check_code_key("test@example.com", "register")
        cache.set(cache_key, "654321", timeout=1800, version=version)

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/check_code",
            {"email": "test@example.com", "code": "000000", "type": "register"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 1005)
        self.assertEqual(
            payload["message"],
            "The verification code is incorrect or the verification code has expired",
        )

    def test_check_code_rejects_missing_code(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/check_code",
            {"email": "test@example.com", "code": "123456", "type": "reset_password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 1005)
        self.assertEqual(
            payload["message"],
            "The verification code is incorrect or the verification code has expired",
        )


class SwitchLanguageContractIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="switch-language@example.com",
            phone="",
            nick_name="Switch Language User",
            username="switch-language-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
            language="zh-CN",
        )
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

    def test_switch_language_updates_user_language(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/language",
            {"language": "en-US"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertIsNone(payload["data"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "en-US")

    def test_switch_language_rejects_unsupported_language(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/language",
            {"language": "fr-FR"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 500)
        self.assertEqual(payload["message"], "language only support:zh-CN,zh-Hant,en-US")
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "zh-CN")


class ResetCurrentPasswordContractIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email="current-reset@example.com",
            phone="",
            nick_name="Current Reset User",
            username="current-reset-user",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.token = get_auth(self.user)
        self.client.force_authenticate(user=self.user, token=self.token)

    def test_current_user_can_reset_password_and_clear_current_token(self):
        version, get_key = Cache_Version.TOKEN.value
        cache.set(get_key(self.token), self.user, timeout=300, version=version)

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/current/reset_password",
            {"password": "Reset123!", "re_password": "Reset123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertTrue(payload["data"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, password_encrypt("Reset123!"))
        self.assertFalse(self.user.require_password_change)
        self.assertIsNone(cache.get(get_key(self.token), version=version))

    def test_current_user_reset_password_rejects_mismatched_confirmation(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/current/reset_password",
            {"password": "Reset123!", "re_password": "Reset456!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 1007)
        self.assertEqual(
            payload["message"],
            "Password and confirmation password are inconsistent",
        )

    def test_current_user_reset_password_rejects_weak_password(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user/current/reset_password",
            {"password": "abcdef", "re_password": "abcdef"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 500)
        self.assertEqual(
            payload["message"],
            "密码:The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters.",
        )


class UserManageCRUDIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_username = "users-manage-admin"
        self.admin_user = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="Admin User",
            username=self.admin_username,
            password=password_encrypt("Admin123!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin_user, token=get_auth(self.admin_user))

    def test_create_user(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user_manage",
            {
                "username": "newuser",
                "password": "NewUser123!",
                "email": "newuser@example.com",
                "role": "USER",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)

    def test_get_user_detail(self):
        response = self.client.get(
            f"{ADMIN_API_PREFIX}/user_manage/{self.admin_user.id}"
        )

        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        response = self.client.put(
            f"{ADMIN_API_PREFIX}/user_manage/{self.admin_user.id}",
            {"nick_name": "Updated Admin"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        test_user = User.objects.create(
            id=uuid.uuid7(),
            email="delete@example.com",
            phone="",
            nick_name="Delete User",
            username="deleteuser",
            password=password_encrypt("Delete123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        response = self.client.delete(
            f"{ADMIN_API_PREFIX}/user_manage/{test_user.id}"
        )

        self.assertEqual(response.status_code, 200)

    def test_batch_delete_users(self):
        first_user = User.objects.create(
            id=uuid.uuid7(),
            email="batch-delete-1@example.com",
            phone="",
            nick_name="Batch Delete One",
            username="batch-delete-one",
            password=password_encrypt("Delete123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        second_user = User.objects.create(
            id=uuid.uuid7(),
            email="batch-delete-2@example.com",
            phone="",
            nick_name="Batch Delete Two",
            username="batch-delete-two",
            password=password_encrypt("Delete123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )

        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user_manage/batch_delete",
            [str(first_user.id), str(second_user.id)],
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertTrue(payload["data"])
        self.assertFalse(User.objects.filter(id=first_user.id).exists())
        self.assertFalse(User.objects.filter(id=second_user.id).exists())

    def test_batch_delete_rejects_empty_ids(self):
        response = self.client.post(
            f"{ADMIN_API_PREFIX}/user_manage/batch_delete",
            [],
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 1004)
        self.assertEqual(payload["message"], "User IDs cannot be empty")


class UserManageDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.regular_user = User.objects.create(
            id=uuid.uuid7(),
            email="user-manage-denied@example.com",
            phone="",
            nick_name="Denied User",
            username="user-manage-denied",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.target_user = User.objects.create(
            id=uuid.uuid7(),
            email="user-manage-target@example.com",
            phone="",
            nick_name="Target User",
            username="user-manage-target",
            password=password_encrypt("User123!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.client.force_authenticate(
            user=self.regular_user, token=get_auth(self.regular_user)
        )

    def test_non_admin_cannot_mutate_user_manage_endpoints(self):
        denied_requests = [
            (
                "post",
                f"{ADMIN_API_PREFIX}/user_manage",
                {
                    "username": "denied-user-create",
                    "password": "Denied123!",
                    "email": "denied-user-create@example.com",
                    "role": "USER",
                },
            ),
            (
                "delete",
                f"{ADMIN_API_PREFIX}/user_manage/{self.target_user.id}",
                None,
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/user_manage/{self.target_user.id}",
                {"nick_name": "Denied Update"},
            ),
            (
                "post",
                f"{ADMIN_API_PREFIX}/user_manage/batch_delete",
                [str(self.target_user.id)],
            ),
            (
                "put",
                f"{ADMIN_API_PREFIX}/user_manage/{self.target_user.id}/re_password",
                {"password": "Denied123!", "re_password": "Denied123!"},
            ),
        ]

        for method, url, payload in denied_requests:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
