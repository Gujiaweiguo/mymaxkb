from typing import Any, cast

from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from system_manage.models import SystemApiKey
from system_manage.models.system_api_key import default_system_expire_time


class SystemApiKeySerializerModel(serializers.ModelSerializer):
    class Meta:
        model = SystemApiKey
        fields = "__all__"


class SystemApiKeyListSerializerModel(serializers.ModelSerializer):
    secret_key = serializers.SerializerMethodField()

    class Meta:
        model = SystemApiKey
        fields = "__all__"

    @staticmethod
    def get_secret_key(obj: SystemApiKey):
        secret_key = obj.secret_key or ""
        if len(secret_key) <= 12:
            return secret_key
        return f"{secret_key[:8]}******{secret_key[-4:]}"


class EditSystemApiKeySerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False, label=_("Availability"))
    allow_cross_domain = serializers.BooleanField(
        required=False, label=_("Is cross-domain allowed")
    )
    cross_domain_list = serializers.ListSerializer(
        required=False,
        child=serializers.CharField(required=True, label=_("Cross-domain address")),
        label=_("Cross-domain list"),
    )
    is_permanent = serializers.BooleanField(required=False, label=_("Is permanent"))
    expire_time = serializers.DateTimeField(
        required=False, allow_null=True, label=_("Expiration time")
    )

    def validate(self, attrs):
        is_permanent = attrs.get("is_permanent")
        expire_time = attrs.get("expire_time")
        if is_permanent is False:
            if expire_time is None:
                raise serializers.ValidationError(
                    {"expire_time": _("Expiration time is required")}
                )
            if expire_time <= timezone.now():
                raise serializers.ValidationError(
                    {"expire_time": _("Expiration time must be in the future")}
                )
        return attrs


class SystemApiKeyQuerySerializer(serializers.Serializer):
    order_by = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, label=_("order by")
    )


class SystemApiKeySerializer(serializers.Serializer):
    order_by = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, label=_("order by")
    )

    def generate(self):
        system_api_key = SystemApiKey()
        system_api_key.save()
        return SystemApiKeySerializerModel(system_api_key).data

    def page(self, current_page: int, page_size: int):
        query_serializer = SystemApiKeyQuerySerializer(data=self.initial_data)
        query_serializer.is_valid(raise_exception=True)
        order_by = (
            "-create_time"
            if query_serializer.validated_data.get("order_by") in (None, "")
            else query_serializer.validated_data.get("order_by")
        )
        query_set = QuerySet(SystemApiKey).order_by(order_by)
        return page_search(
            current_page,
            page_size,
            query_set,
            lambda item: SystemApiKeyListSerializerModel(item).data,
        )

    class Operate(serializers.Serializer):
        api_key_id = serializers.UUIDField(required=True, label=_("ApiKeyId"))

        def delete(self):
            self.is_valid(raise_exception=True)
            system_api_key = cast(
                Any,
                QuerySet(SystemApiKey).filter(id=self.data.get("api_key_id")).first(),
            )
            if system_api_key is None:
                raise AppApiException(500, _("APIKey does not exist"))
            system_api_key.delete()

        def edit(self, instance):
            self.is_valid(raise_exception=True)
            EditSystemApiKeySerializer(data=instance).is_valid(raise_exception=True)
            system_api_key = cast(
                Any,
                QuerySet(SystemApiKey).filter(id=self.data.get("api_key_id")).first(),
            )
            if system_api_key is None:
                raise AppApiException(500, _("APIKey does not exist"))
            if "is_active" in instance and instance.get("is_active") is not None:
                system_api_key.is_active = instance.get("is_active")
            if (
                "allow_cross_domain" in instance
                and instance.get("allow_cross_domain") is not None
            ):
                system_api_key.allow_cross_domain = instance.get("allow_cross_domain")
            if (
                "cross_domain_list" in instance
                and instance.get("cross_domain_list") is not None
            ):
                system_api_key.cross_domain_list = instance.get("cross_domain_list")
            if "is_permanent" in instance and instance.get("is_permanent") is not None:
                system_api_key.is_permanent = instance.get("is_permanent")
                if not system_api_key.is_permanent:
                    system_api_key.expire_time = instance.get("expire_time")
                else:
                    system_api_key.expire_time = default_system_expire_time()
            system_api_key.save()
            return True
