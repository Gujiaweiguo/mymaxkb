from datetime import timedelta
import json
from types import SimpleNamespace
from typing import Any, cast

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from common.auth.handle.impl.user_token import get_auth
from common.exception.app_exception import AppApiException
from common.log.log import log
from common.job.clean_operation_log_job import clean_operation_log_job_lock
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import Log, SettingType, SystemSetting, Workspace
from system_manage.views.log_management import (
    OperateLogCleanTimeView,
    OperateLogExportView,
    OperateLogMenuOptionView,
    OperateLogPageView,
)
from users.models import User


ADMIN_API_PREFIX = '/admin/api'


class OperateLogTests(TestCase):
    factory: APIRequestFactory
    admin: User
    auth_token: SimpleNamespace
    workspace: Workspace

    def setUp(self):
        Log.objects.all().delete()
        self.factory = APIRequestFactory()
        self.admin = QuerySet(User).create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-operate-log",
            username="admin-operate-log",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )
        self.workspace = cast(
            Workspace,
            QuerySet(Workspace).create(id="workspace-log", name="workspace-log"),
        )
        Log.objects.create(
            menu="Chat user management",
            operate="Create chat user",
            operation_object={"name": "alice"},
            user={"username": "admin-operate-log"},
            status=200,
            ip_address="10.0.0.1",
            details={"path": "/system/chat_user", "body": {}, "query": {}},
            workspace_id=self.workspace.id,
        )
        Log.objects.create(
            menu="Platform Source Settings",
            operate="Validate platform source configuration",
            operation_object={"name": "wecom"},
            user={"username": "other-admin"},
            status=500,
            ip_address="10.0.0.2",
            details={"path": "/platform/source", "body": {}, "query": {}},
            workspace_id="other-workspace",
        )

    def test_operate_log_page_returns_paginated_records(self):
        request = self.factory.get("/operate_log/1/20")
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = cast(
            Any, OperateLogPageView.as_view()(request, current_page=1, page_size=20)
        )
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["total"], 2)
        self.assertEqual(len(payload["data"]["records"]), 2)
        first = payload["data"]["records"][0]
        self.assertIn("workspace_name", first)

    def test_operate_log_page_filters_by_status_and_menu(self):
        request = self.factory.get(
            "/operate_log/1/20",
            data={"status": "500", "menu": json.dumps(["Platform Source Settings"])},
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = cast(
            Any, OperateLogPageView.as_view()(request, current_page=1, page_size=20)
        )
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["total"], 1)
        self.assertEqual(
            payload["data"]["records"][0]["operate"],
            "Validate platform source configuration",
        )

    def test_operate_log_menu_option_returns_unique_menus(self):
        request = self.factory.get("/operate_log/menu_operation_option/")
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = cast(Any, OperateLogMenuOptionView.as_view()(request))
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            payload["data"],
            [
                {"menu": "Chat user management", "menu_label": "Chat user management"},
                {
                    "menu": "Platform Source Settings",
                    "menu_label": "Platform Source Settings",
                },
            ],
        )

    def test_operate_log_export_returns_xlsx_attachment(self):
        request = self.factory.post(
            "/operate_log/export/", data={"status": "200"}, format="json"
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)

        response = cast(Any, OperateLogExportView.as_view()(request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="log.xlsx"'
        )

    def test_operate_log_clean_time_defaults_and_saves(self):
        get_request = self.factory.get("/operate_log/get_clean_time")
        force_authenticate(get_request, user=self.admin, token=self.auth_token)

        get_response = cast(Any, OperateLogCleanTimeView.as_view()(get_request))
        get_payload = json.loads(get_response.content)

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_payload["data"], 180)

        save_request = self.factory.post(
            "/operate_log/save", data={"clean_time": 365}, format="json"
        )
        force_authenticate(save_request, user=self.admin, token=self.auth_token)

        save_response = cast(Any, OperateLogCleanTimeView.as_view()(save_request))
        self.assertEqual(save_response.status_code, 200)

        setting = SystemSetting.objects.get(type=SettingType.LOG)
        self.assertEqual(setting.meta["clean_time"], 365)

    def test_operation_log_cleanup_removes_only_expired_logs_for_configured_retention(self):
        SystemSetting.objects.update_or_create(
            type=SettingType.LOG,
            defaults={"meta": {"clean_time": 30}},
        )
        expired_log = Log.objects.create(
            menu="Operate Log Settings",
            operate="Cleanup expired logs",
            operation_object={"name": "expired"},
            user={"username": "admin-operate-log"},
            status=200,
            ip_address="10.0.0.3",
            details={"path": "/operate_log/save", "body": {}, "query": {}},
            workspace_id=self.workspace.id,
        )
        retained_log = Log.objects.create(
            menu="Operate Log Settings",
            operate="Retain fresh logs",
            operation_object={"name": "retained"},
            user={"username": "admin-operate-log"},
            status=200,
            ip_address="10.0.0.4",
            details={"path": "/operate_log/get_clean_time", "body": {}, "query": {}},
            workspace_id=self.workspace.id,
        )
        Log.objects.filter(id=expired_log.id).update(
            create_time=timezone.now() - timedelta(days=31)
        )
        Log.objects.filter(id=retained_log.id).update(
            create_time=timezone.now() - timedelta(days=29)
        )

        clean_operation_log_job_lock.__wrapped__()

        self.assertFalse(Log.objects.filter(id=expired_log.id).exists())
        self.assertTrue(Log.objects.filter(id=retained_log.id).exists())
        self.assertEqual(Log.objects.count(), 3)

    def test_operation_log_cleanup_uses_default_retention_when_setting_missing(self):
        expired_log = Log.objects.create(
            menu="Operate Log Settings",
            operate="Cleanup with default retention",
            operation_object={"name": "expired-default"},
            user={"username": "admin-operate-log"},
            status=200,
            ip_address="10.0.0.5",
            details={"path": "/operate_log/export", "body": {}, "query": {}},
            workspace_id=self.workspace.id,
        )
        retained_log = Log.objects.create(
            menu="Operate Log Settings",
            operate="Keep within default retention",
            operation_object={"name": "retained-default"},
            user={"username": "admin-operate-log"},
            status=200,
            ip_address="10.0.0.6",
            details={"path": "/operate_log/1/20", "body": {}, "query": {}},
            workspace_id=self.workspace.id,
        )
        Log.objects.filter(id=expired_log.id).update(
            create_time=timezone.now() - timedelta(days=181)
        )
        Log.objects.filter(id=retained_log.id).update(
            create_time=timezone.now() - timedelta(days=179)
        )

        clean_operation_log_job_lock.__wrapped__()

        self.assertFalse(Log.objects.filter(id=expired_log.id).exists())
        self.assertTrue(Log.objects.filter(id=retained_log.id).exists())
        self.assertEqual(Log.objects.count(), 3)


class OperateLogDecoratorTests(TestCase):
    class DecoratedView:
        @log(menu="Decorator Menu", operate="Successful operation")
        def success(self, request, **kwargs):
            return {"ok": True}

        @log(menu="Decorator Menu", operate="Failing operation")
        def failure(self, request, **kwargs):
            raise AppApiException(500, "boom")

    def setUp(self):
        Log.objects.all().delete()
        self.user = QuerySet(User).create(
            id=uuid.uuid7(),
            email="decorator-user@example.com",
            phone="",
            nick_name="decorator-user",
            username="decorator-user",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )

    def _build_request(self, path: str):
        return SimpleNamespace(
            user=self.user,
            path=path,
            data={"field": "value"},
            query_params={"page": "1"},
            META={"REMOTE_ADDR": "127.0.0.1"},
        )

    def test_log_decorator_writes_log_on_successful_request(self):
        request = self._build_request("/admin/api/test/success")

        result = self.DecoratedView().success(request, workspace_id="workspace-success")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(Log.objects.count(), 1)
        record = Log.objects.get()
        self.assertEqual(record.menu, "Decorator Menu")
        self.assertEqual(record.operate, "Successful operation")
        self.assertEqual(record.status, 200)
        self.assertEqual(record.user["username"], self.user.username)
        self.assertEqual(record.ip_address, "127.0.0.1")
        self.assertEqual(record.details["path"], "/admin/api/test/success")
        self.assertEqual(record.workspace_id, "workspace-success")

    def test_log_decorator_writes_log_when_wrapped_view_raises(self):
        request = self._build_request("/admin/api/test/failure")

        with self.assertRaises(AppApiException):
            self.DecoratedView().failure(request, workspace_id="workspace-failure")

        self.assertEqual(Log.objects.count(), 1)
        record = Log.objects.get()
        self.assertEqual(record.menu, "Decorator Menu")
        self.assertEqual(record.operate, "Failing operation")
        self.assertEqual(record.status, 500)
        self.assertEqual(record.user["username"], self.user.username)
        self.assertEqual(record.ip_address, "127.0.0.1")
        self.assertEqual(record.details["path"], "/admin/api/test/failure")
        self.assertEqual(record.workspace_id, "workspace-failure")


class OperateLogAuthorizationDeniedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='log-user@example.com',
            phone='',
            nick_name='log-user',
            username='log-user',
            password=password_encrypt('User123!'),
            role=RoleConstants.USER.name,
            source='LOCAL',
            is_active=True,
        )

    def test_non_admin_cannot_manage_operate_log_endpoints(self):
        self.client.force_authenticate(user=self.user, token=get_auth(self.user))

        responses = [
            self.client.get(f'{ADMIN_API_PREFIX}/operate_log/1/10'),
            self.client.get(f'{ADMIN_API_PREFIX}/operate_log/menu_operation_option/'),
            self.client.post(f'{ADMIN_API_PREFIX}/operate_log/export/', {}, format='json'),
            self.client.get(f'{ADMIN_API_PREFIX}/operate_log/get_clean_time'),
            self.client.post(f'{ADMIN_API_PREFIX}/operate_log/save', {}, format='json'),
        ]

        for response in responses:
            self.assertEqual(response.status_code, 403)
