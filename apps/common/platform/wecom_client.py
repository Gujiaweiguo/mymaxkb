# coding=utf-8
import requests
from django.utils.translation import gettext_lazy as _

from common.exception.app_exception import AppApiException


class WecomClient:
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"

    def __init__(self, corp_id: str, app_secret: str):
        self.corp_id = corp_id
        self.app_secret = app_secret

    @classmethod
    def _raise_for_wecom_error(cls, data: dict, fallback_message: str):
        errcode = data.get("errcode", 0)
        if errcode not in (0, "0", None):
            errmsg = data.get("errmsg") or fallback_message
            raise AppApiException(500, str(errmsg))

    def get_access_token(self) -> str:
        response = requests.get(
            f"{self.BASE_URL}/gettoken",
            params={
                "corpid": self.corp_id,
                "corpsecret": self.app_secret,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self._raise_for_wecom_error(data, _("Failed to get WeCom access token"))
        access_token = data.get("access_token")
        if not access_token:
            raise AppApiException(500, _("Missing WeCom access token"))
        return str(access_token)

    def get_user_identity(self, code: str) -> dict:
        access_token = self.get_access_token()
        response = requests.get(
            f"{self.BASE_URL}/auth/getuserinfo",
            params={
                "access_token": access_token,
                "code": code,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self._raise_for_wecom_error(data, _("Failed to get WeCom user identity"))
        return data
