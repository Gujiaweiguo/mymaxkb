import json
from types import SimpleNamespace
from datetime import timedelta
from typing import Any, cast

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, force_authenticate

from common.middleware.cross_domain_middleware import CrossDomainMiddleware
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import SystemApiKey
from system_manage.serializers.system_api_key import EditSystemApiKeySerializer
from system_manage.views.system_api_key import SystemApiKeyView
from system_manage.views.system_profile import SystemProfileApiKey
from users.models import User


class SystemApiKeyTests(TestCase):
    factory: APIRequestFactory
    admin: Any
    auth_token: SimpleNamespace

    @staticmethod
    def call_view(view_cls: Any, request, **kwargs):
        return cast(Any, cast(Any, view_cls.as_view())(request, **kwargs))

    def setUp(self):
        self.factory = APIRequestFactory()
        self.middleware = CrossDomainMiddleware(lambda request: None)
        self.admin = QuerySet(User).create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-system-api-key",
            username="admin-system-api-key",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )
        self.user = QuerySet(User).create(
            id=uuid.uuid7(),
            email="user@example.com",
            phone="",
            nick_name="user-system-api-key",
            username="user-system-api-key",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.USER.name,
            source="LOCAL",
            is_active=True,
        )
        self.user_token = SimpleNamespace(
            role_list=[RoleConstants.USER.value.__str__()],
            permission_list=[],
        )

    def test_create_and_page_system_api_keys(self):
        create_request = self.factory.post("/system/api_key")
        force_authenticate(create_request, user=self.admin, token=self.auth_token)
        create_response = self.call_view(SystemApiKeyView, create_request)
        create_payload = json.loads(create_response.content)

        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_payload["data"]["secret_key"].startswith("system-"))

        page_request = self.factory.get("/system/api_key/1/20")
        force_authenticate(page_request, user=self.admin, token=self.auth_token)
        page_response = self.call_view(
            SystemApiKeyView.Page, page_request, current_page=1, page_size=20
        )
        page_payload = json.loads(page_response.content)

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_payload["data"]["total"], 1)
        self.assertNotEqual(
            page_payload["data"]["records"][0]["secret_key"],
            create_payload["data"]["secret_key"],
        )
        self.assertIn("******", page_payload["data"]["records"][0]["secret_key"])

        system_api_key = QuerySet(SystemApiKey).get(id=create_payload["data"]["id"])
        self.assertTrue(system_api_key.is_permanent)
        self.assertGreater(system_api_key.expire_time, timezone.now())

    def test_update_system_api_key(self):
        system_api_key = QuerySet(SystemApiKey).create()
        request = self.factory.put(
            f"/system/api_key/{system_api_key.id}",
            data={
                "is_active": False,
                "allow_cross_domain": True,
                "cross_domain_list": ["https://example.com"],
                "is_permanent": False,
                "expire_time": "2030-01-01T00:00:00Z",
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = self.call_view(
            SystemApiKeyView.Operate, request, api_key_id=str(system_api_key.id)
        )

        self.assertEqual(response.status_code, 200)
        system_api_key.refresh_from_db()
        self.assertFalse(system_api_key.is_active)
        self.assertTrue(system_api_key.allow_cross_domain)
        self.assertEqual(system_api_key.cross_domain_list, ["https://example.com"])
        self.assertFalse(system_api_key.is_permanent)

    def test_update_system_api_key_requires_future_expire_time_for_non_permanent(self):
        serializer = EditSystemApiKeySerializer(data={"is_permanent": False})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

        serializer = EditSystemApiKeySerializer(
            data={"is_permanent": False, "expire_time": "2000-01-01T00:00:00Z"}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_delete_system_api_key(self):
        system_api_key = QuerySet(SystemApiKey).create()
        request = self.factory.delete(f"/system/api_key/{system_api_key.id}")
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = self.call_view(
            SystemApiKeyView.Operate, request, api_key_id=str(system_api_key.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuerySet(SystemApiKey).filter(id=system_api_key.id).exists())

    def test_system_api_key_can_access_system_profile_endpoint(self):
        system_api_key = QuerySet(SystemApiKey).create()
        request = self.factory.get("/system/profile")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {system_api_key.secret_key}"

        response = self.call_view(SystemProfileApiKey, request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["code"], 200)

    def test_inactive_system_api_key_is_denied(self):
        system_api_key = QuerySet(SystemApiKey).create(is_active=False)
        request = self.factory.get("/system/profile")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {system_api_key.secret_key}"

        response = self.call_view(SystemProfileApiKey, request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["code"], 500)

    def test_expired_system_api_key_is_denied(self):
        system_api_key = QuerySet(SystemApiKey).create(
            is_permanent=False,
            expire_time=timezone.now() - timedelta(days=1),
        )
        request = self.factory.get("/system/profile")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {system_api_key.secret_key}"

        response = self.call_view(SystemProfileApiKey, request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["code"], 500)

    def test_invalid_system_api_key_is_denied(self):
        request = self.factory.get("/system/profile")
        request.META["HTTP_AUTHORIZATION"] = "Bearer system-invalid"

        response = self.call_view(SystemProfileApiKey, request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["code"], 500)

    def test_system_api_key_cross_domain_allows_listed_origin(self):
        system_api_key = QuerySet(SystemApiKey).create(
            allow_cross_domain=True,
            cross_domain_list=["https://allowed.example.com"],
        )
        request = self.factory.get(
            "/system/profile",
            HTTP_AUTHORIZATION=f"Bearer {system_api_key.secret_key}",
            HTTP_ORIGIN="https://allowed.example.com",
        )

        response = self.call_view(SystemProfileApiKey, request)
        response = self.middleware.process_response(request, response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "https://allowed.example.com"
        )
        self.assertEqual(response["Access-Control-Allow-Methods"], "GET,POST,DELETE,PUT")
        self.assertIn("Authorization", response["Access-Control-Allow-Headers"])

    def test_system_api_key_cross_domain_denies_unlisted_origin(self):
        system_api_key = QuerySet(SystemApiKey).create(
            allow_cross_domain=True,
            cross_domain_list=["https://allowed.example.com"],
        )
        request = self.factory.get(
            "/system/profile",
            HTTP_AUTHORIZATION=f"Bearer {system_api_key.secret_key}",
            HTTP_ORIGIN="https://denied.example.com",
        )

        response = self.call_view(SystemProfileApiKey, request)
        response = self.middleware.process_response(request, response)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.has_header("Access-Control-Allow-Origin"))
        self.assertFalse(response.has_header("Access-Control-Allow-Methods"))
        self.assertFalse(response.has_header("Access-Control-Allow-Headers"))

    def test_non_admin_cannot_manage_system_api_key_endpoints(self):
        system_api_key = QuerySet(SystemApiKey).create()

        requests = [
            (SystemApiKeyView, self.factory.post("/system/api_key"), {}),
            (
                SystemApiKeyView.Page,
                self.factory.get("/system/api_key/1/20"),
                {"current_page": 1, "page_size": 20},
            ),
            (
                SystemApiKeyView.Operate,
                self.factory.put(
                    f"/system/api_key/{system_api_key.id}",
                    data={"is_active": False},
                    format="json",
                ),
                {"api_key_id": str(system_api_key.id)},
            ),
            (
                SystemApiKeyView.Operate,
                self.factory.delete(f"/system/api_key/{system_api_key.id}"),
                {"api_key_id": str(system_api_key.id)},
            ),
        ]

        for view_cls, request, kwargs in requests:
            with self.subTest(view=view_cls.__name__, kwargs=kwargs):
                force_authenticate(request, user=self.user, token=self.user_token)
                response = self.call_view(view_cls, request, **kwargs)
                self.assertEqual(response.status_code, 403)
