from typing import Any

from django.db.models import QuerySet
from rest_framework import serializers

from common.field.common import ObjectField
from knowledge.models import FileSourceType
from oss.serializers.file import FileSerializer
from system_manage.models import SettingType, SystemSetting


class BrandingFileField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            return data
        if hasattr(data, "read"):
            return data
        raise serializers.ValidationError("Invalid file value")

    def to_representation(self, value):
        return value


class AppearanceSettingResponseSerializer(serializers.Serializer):
    theme = serializers.CharField(required=True)
    icon = serializers.CharField(required=False, allow_blank=True)
    loginLogo = serializers.CharField(required=False, allow_blank=True)
    loginImage = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=True)
    slogan = serializers.CharField(required=True)
    showUserManual = serializers.BooleanField(required=True)
    userManualUrl = serializers.CharField(required=True)
    showForum = serializers.BooleanField(required=True)
    forumUrl = serializers.CharField(required=True)
    showProject = serializers.BooleanField(required=True)
    projectUrl = serializers.CharField(required=True)


class AppearanceSettingSerializer(serializers.Serializer):
    DEFAULT_META = {
        "theme": "#3370FF",
        "icon": "",
        "loginLogo": "",
        "loginImage": "",
        "title": "MaxKB",
        "slogan": "Ready to create your own intelligent assistant?",
        "showUserManual": True,
        "userManualUrl": "https://maxkb.cn/docs/",
        "showForum": True,
        "forumUrl": "https://bbs.fit2cloud.com/c/maxkb/",
        "showProject": True,
        "projectUrl": "https://github.com/1Panel-dev/MaxKB",
    }

    @classmethod
    def one(cls):
        system_setting = (
            QuerySet(SystemSetting).filter(type=SettingType.APPEARANCE).first()
        )
        if system_setting is None:
            return cls.DEFAULT_META
        return {
            **cls.DEFAULT_META,
            **(system_setting.meta if isinstance(system_setting.meta, dict) else {}),
        }

    class Update(serializers.Serializer):
        theme = serializers.CharField(required=False)
        icon = BrandingFileField(required=False)
        loginLogo = BrandingFileField(required=False)
        loginImage = BrandingFileField(required=False)
        title = serializers.CharField(required=False, allow_blank=False, max_length=128)
        slogan = serializers.CharField(required=False, allow_blank=False, max_length=64)
        showUserManual = serializers.BooleanField(required=False)
        userManualUrl = serializers.CharField(
            required=False, allow_blank=True, max_length=128
        )
        showForum = serializers.BooleanField(required=False)
        forumUrl = serializers.CharField(
            required=False, allow_blank=True, max_length=128
        )
        showProject = serializers.BooleanField(required=False)
        projectUrl = serializers.CharField(
            required=False, allow_blank=True, max_length=128
        )

        @staticmethod
        def _save_file(file_value, field_name: str):
            if isinstance(file_value, str):
                return file_value
            if file_value is None:
                return ""
            return FileSerializer(
                data={
                    "file": file_value,
                    "source_id": f"SYSTEM_APPEARANCE_{field_name}",
                    "source_type": FileSourceType.SYSTEM,
                    "meta": {"field": field_name},
                }
            ).upload()

        def update_or_save(self):
            self.is_valid(raise_exception=True)
            current_meta = AppearanceSettingSerializer.one()
            next_meta = {**current_meta, **self.validated_data}
            for field_name in ["icon", "loginLogo", "loginImage"]:
                if field_name in self.validated_data:
                    next_meta[field_name] = self._save_file(
                        self.validated_data.get(field_name), field_name
                    )
            system_setting = (
                QuerySet(SystemSetting).filter(type=SettingType.APPEARANCE).first()
            )
            if system_setting is None:
                system_setting = SystemSetting(type=SettingType.APPEARANCE)
            system_setting.meta = next_meta
            system_setting.save()
            return AppearanceSettingSerializer.one()
