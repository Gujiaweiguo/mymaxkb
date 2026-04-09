import json

from django.db.models import Count, QuerySet
from rest_framework import serializers

from common.result import Page
from system_manage.models import Workspace
from system_manage.models.resource_mapping import ResourceMapping
from tools.models import Tool


class SystemResourceToolItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    icon = serializers.CharField(required=True, allow_blank=True)
    tool_type = serializers.CharField(required=True)
    template_id = serializers.CharField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=True)
    init_field_list = serializers.ListField(required=True)
    nick_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    update_time = serializers.DateTimeField(required=True)
    create_time = serializers.DateTimeField(required=True)
    workspace_id = serializers.CharField(required=True)
    workspace_name = serializers.CharField(required=True)
    resource_count = serializers.IntegerField(required=True)


class SystemResourceToolRecordItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    workspace_id = serializers.CharField(required=True)
    tool_id = serializers.UUIDField(required=True)
    source_type = serializers.CharField(required=True)
    source_id = serializers.UUIDField(required=True)
    meta = serializers.JSONField(required=True)
    state = serializers.CharField(required=True)
    run_time = serializers.FloatField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    source_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tool_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tool_icon = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    trigger_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SystemResourceToolQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    create_user = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tool_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workspace_ids = serializers.CharField(required=False, allow_blank=True, allow_null=True)

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
        records = self.serialize_records(query_set[start:start + page_size])
        return Page(total, records, current_page, page_size)

    def get_query_set(self):
        query_set = QuerySet(Tool).select_related('user').order_by('-create_time')

        if self.validated_data.get('name'):
            query_set = query_set.filter(name__contains=self.validated_data.get('name'))
        if self.validated_data.get('create_user'):
            query_set = query_set.filter(user_id=self.validated_data.get('create_user'))
        if self.validated_data.get('tool_type'):
            query_set = query_set.filter(tool_type=self.validated_data.get('tool_type'))

        source = self.validated_data.get('source')
        if source == 'TOOL_STORE':
            query_set = query_set.filter(template_id__isnull=False)
        elif source == 'CUSTOM':
            query_set = query_set.filter(template_id__isnull=True)

        workspace_ids = self._parse_json_list(self.validated_data.get('workspace_ids'))
        if workspace_ids:
            query_set = query_set.filter(workspace_id__in=workspace_ids)

        return query_set

    @staticmethod
    def serialize_records(query_set):
        workspace_name_map = {
            workspace.id: workspace.name for workspace in QuerySet(Workspace).all()
        }
        mapping_counts = {
            str(item['target_id']): item['count']
            for item in ResourceMapping.objects.filter(
                target_id__in=[str(tool.id) for tool in query_set]
            ).values('target_id').annotate(count=Count('id'))
        }

        return [
            {
                'id': tool.id,
                'name': tool.name,
                'icon': tool.icon,
                'tool_type': tool.tool_type,
                'template_id': tool.template_id,
                'is_active': tool.is_active,
                'init_field_list': tool.init_field_list,
                'nick_name': tool.user.nick_name if tool.user else '',
                'update_time': tool.update_time,
                'create_time': tool.create_time,
                'workspace_id': tool.workspace_id,
                'workspace_name': workspace_name_map.get(tool.workspace_id, tool.workspace_id),
                'resource_count': mapping_counts.get(str(tool.id), 0),
            }
            for tool in query_set
        ]
