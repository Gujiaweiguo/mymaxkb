from rest_framework import serializers


class PlatformSourceItemSerializer(serializers.Serializer):
    auth_type = serializers.CharField(required=True)
    config = serializers.DictField(required=False, default=dict)
    is_active = serializers.BooleanField(required=False, default=False)
    is_valid = serializers.BooleanField(required=False, default=False)
    is_configured = serializers.BooleanField(required=False, default=False)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    failure_reason = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


class PlatformSourceRequestSerializer(serializers.Serializer):
    key = serializers.CharField(required=True)
    config = serializers.DictField(required=False, default=dict)
    is_active = serializers.BooleanField(required=False)
    isActive = serializers.BooleanField(required=False, source="is_active")
