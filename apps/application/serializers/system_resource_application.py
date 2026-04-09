# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： system_resource_application.py
@date：2026/3/23
@desc:
"""

import json

from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application
from common.result import Page
from system_manage.models import Workspace


class SystemResourceApplicationItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    icon = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    is_publish = serializers.BooleanField(required=True)
    nick_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workspace_id = serializers.CharField(required=True)
    workspace_name = serializers.CharField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    resource_count = serializers.IntegerField(required=True)


class SystemResourceApplicationQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    create_user = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workspace_ids = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    @staticmethod
    def _parse_json_list(raw_value):
        if not raw_value:
            return []
        try:
            value = json.loads(raw_value)
            return value if isinstance(value, list) else []
        except Exception:
            return []

    def page(self, current_page: int, page_size: int):
        self.is_valid(raise_exception=True)
        query_set = self.get_query_set()

        total = query_set.count()
        start = (current_page - 1) * page_size
        records = self.serialize_records(query_set[start : start + page_size])
        return Page(total, records, current_page, page_size)

    def list(self):
        self.is_valid(raise_exception=True)
        return self.serialize_records(self.get_query_set())

    def get_query_set(self):
        query_set = QuerySet(Application).select_related("user").order_by("-create_time")

        if self.validated_data.get("name"):
            query_set = query_set.filter(name__contains=self.validated_data.get("name"))
        if self.validated_data.get("create_user"):
            query_set = query_set.filter(user_id=self.validated_data.get("create_user"))
        if self.validated_data.get("type"):
            query_set = query_set.filter(type=self.validated_data.get("type"))

        workspace_ids = self._parse_json_list(self.validated_data.get("workspace_ids"))
        if workspace_ids:
            query_set = query_set.filter(workspace_id__in=workspace_ids)

        status_list = self._parse_json_list(self.validated_data.get("status"))
        if status_list:
            query_set = query_set.filter(is_publish__in=status_list)

        return query_set

    @staticmethod
    def serialize_records(query_set):
        workspace_name_map = {
            workspace.id: workspace.name for workspace in QuerySet(Workspace).all()
        }

        return [
            {
                "id": application.id,
                "name": application.name,
                "icon": application.icon,
                "type": application.type,
                "is_publish": application.is_publish,
                "nick_name": application.user.nick_name if application.user else "",
                "workspace_id": application.workspace_id,
                "workspace_name": workspace_name_map.get(
                    application.workspace_id, application.workspace_id
                ),
                "create_time": application.create_time,
                "update_time": application.update_time,
                "resource_count": 0,
            }
            for application in query_set
        ]
