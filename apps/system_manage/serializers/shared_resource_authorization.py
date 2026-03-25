from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from knowledge.models import Knowledge
from system_manage.models import (
    SharedAuthenticationType,
    SharedResourceAuthorization,
    SharedResourceType,
)
from tools.models import Tool


RESOURCE_MODEL_MAP = {
    SharedResourceType.KNOWLEDGE: Knowledge,
    SharedResourceType.TOOL: Tool,
}


class SharedResourceAuthorizationItemSerializer(serializers.Serializer):
    authentication_type = serializers.CharField(required=True)
    workspace_id_list = serializers.ListField(
        child=serializers.CharField(), required=True
    )


class SharedResourceAuthorizationSerializer(serializers.Serializer):
    DEFAULT_DATA = {
        "authentication_type": SharedAuthenticationType.WHITE_LIST,
        "workspace_id_list": [],
    }

    @staticmethod
    def validate_resource(resource_type: str, resource_id: str):
        if resource_type not in SharedResourceType.values:
            raise AppApiException(500, "Unsupported shared resource type")
        model = RESOURCE_MODEL_MAP.get(resource_type)
        if model is None or not QuerySet(model).filter(id=resource_id).exists():
            raise AppApiException(500, "Shared resource does not exist")
        return resource_type

    @classmethod
    def one(cls, resource_type: str, resource_id: str):
        cls.validate_resource(resource_type, resource_id)
        instance = (
            QuerySet(SharedResourceAuthorization)
            .filter(
                resource_type=resource_type,
                resource_id=resource_id,
            )
            .first()
        )
        if instance is None:
            return cls.DEFAULT_DATA.copy()
        return {
            "authentication_type": instance.authentication_type,
            "workspace_id_list": instance.workspace_id_list or [],
        }

    class Operate(serializers.Serializer):
        authentication_type = serializers.ChoiceField(
            choices=SharedAuthenticationType.choices, required=True
        )
        workspace_id_list = serializers.ListField(
            child=serializers.CharField(required=True), required=True
        )

        @staticmethod
        def normalize_workspace_ids(workspace_id_list):
            result = []
            for workspace_id in workspace_id_list:
                workspace_id = str(workspace_id)
                if workspace_id and workspace_id not in result:
                    result.append(workspace_id)
            return result

        def create(self, validated_data):
            resource_type = validated_data.get("resource_type")
            resource_id = validated_data.get("resource_id")
            SharedResourceAuthorizationSerializer.validate_resource(
                resource_type, resource_id
            )
            instance = (
                QuerySet(SharedResourceAuthorization)
                .filter(
                    resource_type=resource_type,
                    resource_id=resource_id,
                )
                .first()
            )
            if instance is None:
                instance = SharedResourceAuthorization(
                    resource_type=resource_type, resource_id=resource_id
                )
            instance.authentication_type = validated_data.get("authentication_type")
            instance.workspace_id_list = self.normalize_workspace_ids(
                validated_data.get("workspace_id_list", [])
            )
            instance.save()
            return {
                "authentication_type": instance.authentication_type,
                "workspace_id_list": instance.workspace_id_list,
            }
