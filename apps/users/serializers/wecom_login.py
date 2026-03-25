import requests

from django.core import signing
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.exception.app_exception import AppApiException
from common.platform.wecom_client import WecomClient
from maxkb.const import CONFIG
from system_manage.models import SettingType, SystemSetting
from users.models import User


class WecomIdentitySerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=512, label=_("Code"))

    @staticmethod
    def get_provider_credentials(setting_type: int):
        setting = QuerySet(SystemSetting).filter(type=setting_type).first()
        meta = (
            setting.meta
            if setting is not None and isinstance(setting.meta, dict)
            else {}
        )
        provider = meta.get("wecom") if isinstance(meta.get("wecom"), dict) else {}
        config = (
            provider.get("config") if isinstance(provider.get("config"), dict) else {}
        )
        if not provider.get("is_valid"):
            raise AppApiException(500, _("WeCom integration is not ready"))
        if not provider.get("is_active"):
            raise AppApiException(500, _("WeCom integration is not enabled"))
        corp_id = config.get("corp_id")
        app_secret = config.get("app_secret")
        if not corp_id or not app_secret:
            raise AppApiException(
                500, _("WeCom integration is missing required credentials")
            )
        return str(corp_id), str(app_secret)

    @staticmethod
    def resolve_username(identity: dict) -> str:
        userid = identity.get("userid")
        if userid:
            return str(userid)
        openid = identity.get("openid")
        if openid:
            return str(openid)
        raise AppApiException(500, _("Unable to resolve WeCom user identity"))

    @classmethod
    def fetch_identity(cls, setting_type: int, code: str) -> dict:
        corp_id, app_secret = cls.get_provider_credentials(setting_type)
        try:
            return WecomClient(
                corp_id=corp_id, app_secret=app_secret
            ).get_user_identity(code)
        except requests.RequestException as exc:
            raise AppApiException(500, _("Failed to request WeCom identity")) from exc


class WecomLoginSerializer(WecomIdentitySerializer):
    def login(self):
        self.is_valid(raise_exception=True)
        identity = self.fetch_identity(
            SettingType.PLATFORM_SOURCE, self.validated_data["code"]
        )
        username = self.resolve_username(identity)
        user = QuerySet(User).filter(username=username).first()
        if user is None:
            raise AppApiException(
                500, _("WeCom user is not bound to an existing account")
            )
        if not user.is_active:
            raise AppApiException(
                1005, _("The user has been disabled, please contact the administrator!")
            )
        token = signing.dumps(
            {
                "username": user.username,
                "id": str(user.id),
                "email": user.email,
                "type": AuthenticationType.SYSTEM_USER.value,
            }
        )
        version, get_key = Cache_Version.TOKEN.value
        timeout = CONFIG.get_session_timeout()
        cache.set(get_key(token), user, timeout=timeout, version=version)
        return {"token": token}
