import json
from types import SimpleNamespace
from typing import Any, cast

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

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


class OperateLogTests(TestCase):
    factory: APIRequestFactory
    admin: User
    auth_token: SimpleNamespace
    workspace: Workspace

    def setUp(self):
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
