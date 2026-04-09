import json

from django.db.models import Count, QuerySet
from rest_framework import serializers

from common.result import Page
from knowledge.models import Knowledge
from system_manage.models import Workspace
from system_manage.models.resource_mapping import ResourceMapping


class SystemResourceKnowledgeItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    desc = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    type = serializers.IntegerField(required=True)
    workspace_id = serializers.CharField(required=True)
    workspace_name = serializers.CharField(required=True)
    nick_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    resource_count = serializers.IntegerField(required=True)


class SystemResourceDocumentTagSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    key = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class SystemResourceDocumentItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    knowledge_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    char_length = serializers.IntegerField(required=True)
    status = serializers.CharField(required=True)
    status_meta = serializers.JSONField(required=True)
    is_active = serializers.BooleanField(required=True)
    type = serializers.IntegerField(required=True)
    hit_handling_method = serializers.CharField(required=True)
    directly_return_similarity = serializers.FloatField(required=True)
    meta = serializers.JSONField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    paragraph_count = serializers.IntegerField(required=False, allow_null=True)
    tag_count = serializers.IntegerField(required=False, allow_null=True)
    tags = SystemResourceDocumentTagSerializer(many=True, required=False)


class SystemResourceKnowledgeQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    create_user = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
        query_set = QuerySet(Knowledge).select_related('user').order_by('-create_time', 'id')

        if self.validated_data.get('name'):
            query_set = query_set.filter(name__icontains=self.validated_data.get('name'))
        if self.validated_data.get('create_user'):
            query_set = query_set.filter(user_id=self.validated_data.get('create_user'))
        if self.validated_data.get('type') not in [None, '']:
            query_set = query_set.filter(type=self.validated_data.get('type'))

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
                target_id__in=[str(knowledge.id) for knowledge in query_set]
            ).values('target_id').annotate(count=Count('id'))
        }

        return [
            {
                'id': knowledge.id,
                'name': knowledge.name,
                'desc': knowledge.desc,
                'type': knowledge.type,
                'workspace_id': knowledge.workspace_id,
                'workspace_name': workspace_name_map.get(knowledge.workspace_id, knowledge.workspace_id),
                'nick_name': knowledge.user.nick_name if knowledge.user else '',
                'create_time': knowledge.create_time,
                'update_time': knowledge.update_time,
                'resource_count': mapping_counts.get(str(knowledge.id), 0),
            }
            for knowledge in query_set
        ]
