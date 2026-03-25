from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ApplicationAccessToken, ChatUserType
from common.auth.common import ChatAuthentication, ChatUserToken
from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppUnauthorizedFailed, NotFound404
from system_manage.models import ChatUser, SettingType
from users.serializers.dingtalk_login import DingtalkIdentitySerializer


class DingtalkAuthenticationSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=512, label=_("code"))
    access_token = serializers.CharField(required=True, label=_("access_token"))

    def auth(self):
        self.is_valid(raise_exception=True)
        access_token = self.validated_data["access_token"]
        application_access_token = (
            QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
        )
        if application_access_token is None or not application_access_token.is_active:
            raise NotFound404(404, _("Invalid access token"))
        identity = DingtalkIdentitySerializer.fetch_identity(
            SettingType.CHAT_USER_PLATFORM_SOURCE,
            self.validated_data["code"],
        )
        username = DingtalkIdentitySerializer.resolve_username(identity)
        chat_user = QuerySet(ChatUser).filter(username=username).first()
        if chat_user is None:
            raise AppUnauthorizedFailed(
                500, _("DingTalk user is not bound to an existing chat account")
            )
        if not chat_user.is_active:
            raise AppUnauthorizedFailed(500, _("The chat user has been disabled"))
        return ChatUserToken(
            application_access_token.application_id,
            str(chat_user.id),
            access_token,
            AuthenticationType.CHAT_USER,
            ChatUserType.CHAT_USER.value,
            str(chat_user.id),
            ChatAuthentication("dingtalk", username=username),
        ).to_token()
