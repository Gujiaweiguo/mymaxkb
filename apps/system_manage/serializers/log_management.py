import json
from io import BytesIO
from typing import Any, cast

import openpyxl
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from rest_framework import serializers

from common.result.result import Page
from system_manage.models import Log, SettingType, SystemSetting, Workspace


class OperateLogQuerySerializer(serializers.Serializer):
    start_time = serializers.CharField(required=False, allow_blank=True)
    end_time = serializers.CharField(required=False, allow_blank=True)
    user = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    menu = serializers.CharField(required=False, allow_blank=True)
    workspace_ids = serializers.CharField(required=False, allow_blank=True)


class OperateLogCleanTimeSerializer(serializers.Serializer):
    clean_time = serializers.IntegerField(required=True, min_value=1)


class OperateLogSerializer:
    @staticmethod
    def _parse_json_array(value: str | None):
        if not value:
            return []
        try:
            result = json.loads(value)
        except json.JSONDecodeError:
            return []
        return result if isinstance(result, list) else []

    @classmethod
    def _query_set(cls, query_data: dict[str, Any]):
        query_set = QuerySet(Log).all()
        if query_data.get("start_time"):
            query_set = query_set.filter(
                create_time__date__gte=query_data.get("start_time")
            )
        if query_data.get("end_time"):
            query_set = query_set.filter(
                create_time__date__lte=query_data.get("end_time")
            )
        if query_data.get("user"):
            query_set = query_set.filter(
                user__username__icontains=query_data.get("user")
            )
        if query_data.get("ip_address"):
            query_set = query_set.filter(
                ip_address__icontains=query_data.get("ip_address")
            )
        if query_data.get("status"):
            query_set = query_set.filter(
                status=int(cast(str, query_data.get("status")))
            )
        menu_list = cls._parse_json_array(query_data.get("menu"))
        if len(menu_list) > 0:
            query_set = query_set.filter(menu__in=menu_list)
        workspace_ids = cls._parse_json_array(query_data.get("workspace_ids"))
        if len(workspace_ids) > 0:
            query_set = query_set.filter(workspace_id__in=workspace_ids)
        return query_set.order_by("-create_time")

    @classmethod
    def page(cls, query_data: dict[str, Any], current_page: int, page_size: int):
        OperateLogQuerySerializer(data=query_data).is_valid(raise_exception=True)
        query_set = cls._query_set(query_data)
        total = query_set.count()
        start = (current_page - 1) * page_size
        records = cast(list[Log], list(query_set[start : start + page_size]))
        workspace_ids = list(
            {item.workspace_id for item in records if item.workspace_id}
        )
        workspace_name_map = {
            str(item.id): item.name
            for item in QuerySet(Workspace).filter(id__in=workspace_ids)
        }
        return Page(
            total,
            [
                {
                    "id": str(item.id),
                    "menu": item.menu,
                    "operate": item.operate,
                    "operation_object": item.operation_object,
                    "user": item.user,
                    "status": item.status,
                    "ip_address": item.ip_address,
                    "details": item.details,
                    "workspace_id": item.workspace_id,
                    "workspace_name": workspace_name_map.get(
                        str(item.workspace_id), ""
                    ),
                    "create_time": item.create_time,
                }
                for item in records
            ],
            current_page,
            page_size,
        )

    @classmethod
    def export(cls, query_data: dict[str, Any]):
        OperateLogQuerySerializer(data=query_data).is_valid(raise_exception=True)
        query_set = cls._query_set(query_data)
        workspace_ids = list(
            {item.workspace_id for item in query_set if item.workspace_id}
        )
        workspace_name_map = {
            str(item.id): item.name
            for item in QuerySet(Workspace).filter(id__in=workspace_ids)
        }

        def stream_response():
            workbook = openpyxl.Workbook(write_only=True)
            worksheet = workbook.create_sheet()
            worksheet.append(
                [
                    "Menu",
                    "Operate",
                    "Operation Object",
                    "User",
                    "Status",
                    "IP Address",
                    "Workspace",
                    "Create Time",
                ]
            )
            for item in query_set.iterator():
                worksheet.append(
                    [
                        item.menu,
                        item.operate,
                        item.operation_object.get("name", "")
                        if isinstance(item.operation_object, dict)
                        else "",
                        item.user.get("username", "")
                        if isinstance(item.user, dict)
                        else "",
                        item.status,
                        item.ip_address,
                        workspace_name_map.get(str(item.workspace_id), ""),
                        item.create_time.strftime("%Y-%m-%d %H:%M:%S")
                        if item.create_time
                        else "",
                    ]
                )
            output = BytesIO()
            workbook.save(output)
            output.seek(0)
            yield output.getvalue()
            output.close()
            workbook.close()

        response = StreamingHttpResponse(
            stream_response(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="log.xlsx"'
        return response

    @staticmethod
    def menu_operation_option():
        menus = cast(
            list[str],
            list(
                QuerySet(Log).values_list("menu", flat=True).distinct().order_by("menu")
            ),
        )
        return [{"menu": item, "menu_label": item} for item in menus if item]

    @staticmethod
    def get_clean_time():
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.LOG).first()
        if system_setting is None:
            return 180
        return int(system_setting.meta.get("clean_time", 180))

    @staticmethod
    def save_clean_time(data: dict[str, Any]):
        serializer = OperateLogCleanTimeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        QuerySet(SystemSetting).update_or_create(
            type=SettingType.LOG,
            defaults={"meta": {"clean_time": serializer.validated_data["clean_time"]}},
        )
        return True
