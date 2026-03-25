import requests
from django.utils.translation import gettext_lazy as _

from common.exception.app_exception import AppApiException


class DingtalkClient:
    BASE_URL = "https://oapi.dingtalk.com"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def _raise_for_dingtalk_error(cls, data: dict, fallback_message: str):
        errcode = data.get("errcode", 0)
        if errcode not in (0, "0", None):
            errmsg = data.get("errmsg") or fallback_message
            raise AppApiException(500, str(errmsg))

    def get_access_token(self) -> str:
        response = requests.get(
            f"{self.BASE_URL}/gettoken",
            params={
                "appkey": self.app_key,
                "appsecret": self.app_secret,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self._raise_for_dingtalk_error(data, _("Failed to get DingTalk access token"))
        access_token = data.get("access_token")
        if not access_token:
            raise AppApiException(500, _("Missing DingTalk access token"))
        return str(access_token)

    def get_user_identity(self, code: str) -> dict:
        access_token = self.get_access_token()
        response = requests.post(
            f"{self.BASE_URL}/topapi/v2/user/getuserinfo",
            params={"access_token": access_token},
            json={"code": code},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self._raise_for_dingtalk_error(data, _("Failed to get DingTalk user identity"))
        result = data.get("result")
        if not isinstance(result, dict):
            raise AppApiException(500, _("Missing DingTalk user identity result"))
        return result
