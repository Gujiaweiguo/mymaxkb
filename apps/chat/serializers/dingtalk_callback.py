import base64
import binascii
import hashlib
import json
import os
import struct
import time

from Crypto.Cipher import AES
from django.db.models import QuerySet
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from application.models import Chat, ChatSourceChoices, ChatUserType
from application.serializers.application_platform import (
    ApplicationPlatformManageSerializer,
)
from system_manage.models import SettingType
from system_manage.serializers.platform_source import PlatformSourceManageSerializer


class DingtalkCallbackSerializer:
    block_size = 32
    supported_event_types = {"user_add_org"}

    @classmethod
    def get_callback_config(cls, application_id: str) -> dict:
        status = ApplicationPlatformManageSerializer.get_config(
            application_id, "dingtalk"
        )
        if not status.get("is_valid"):
            raise ValueError(str(_("DingTalk application callback is not ready")))
        if not status.get("is_active"):
            raise ValueError(str(_("DingTalk application callback is not enabled")))
        config = (
            status.get("config", {})
            if isinstance(status.get("config", {}), dict)
            else {}
        )
        token = config.get("token")
        encoding_aes_key = config.get("encoding_aes_key")
        if not token or not encoding_aes_key:
            raise ValueError(
                str(_("DingTalk application callback is missing required credentials"))
            )
        provider = PlatformSourceManageSerializer.get(
            SettingType.PLATFORM_SOURCE, "dingtalk"
        )
        provider_config = (
            provider.get("config", {})
            if isinstance(provider.get("config", {}), dict)
            else {}
        )
        owner_key = provider_config.get("app_key") or provider_config.get("corp_id")
        if not owner_key:
            raise ValueError(
                str(_("DingTalk provider configuration is missing owner key"))
            )
        return {
            "token": str(token),
            "encoding_aes_key": str(encoding_aes_key),
            "owner_key": str(owner_key),
        }

    @classmethod
    def build_signature(cls, token: str, timestamp: str, nonce: str, value: str) -> str:
        return hashlib.sha1(
            "".join(sorted([nonce, timestamp, token, value])).encode("utf-8")
        ).hexdigest()

    @classmethod
    def verify_signature(
        cls, token: str, msg_signature: str, timestamp: str, nonce: str, value: str
    ) -> bool:
        return cls.build_signature(token, timestamp, nonce, value) == msg_signature

    @classmethod
    def pkcs7_pad(cls, value: bytes) -> bytes:
        pad = cls.block_size - (len(value) % cls.block_size)
        return value + bytes([pad]) * pad

    @classmethod
    def pkcs7_unpad(cls, value: bytes) -> bytes:
        pad = value[-1]
        if pad < 1 or pad > cls.block_size:
            raise ValueError(str(_("Invalid DingTalk callback padding")))
        return value[:-pad]

    @classmethod
    def decrypt_message(cls, encoding_aes_key: str, encrypted: str) -> tuple[str, str]:
        try:
            aes_key = base64.b64decode(f"{encoding_aes_key}=")
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
            decrypted = cipher.decrypt(base64.b64decode(encrypted))
            plain = cls.pkcs7_unpad(decrypted)
            msg_len = struct.unpack("!I", plain[16:20])[0]
            message = plain[20 : 20 + msg_len].decode("utf-8")
            owner_key = plain[20 + msg_len :].decode("utf-8")
            return message, owner_key
        except (ValueError, UnicodeDecodeError, binascii.Error, struct.error) as exc:
            raise ValueError(str(_("Invalid DingTalk callback payload"))) from exc

    @classmethod
    def encrypt_message(
        cls, encoding_aes_key: str, owner_key: str, message: str
    ) -> str:
        aes_key = base64.b64decode(f"{encoding_aes_key}=")
        random_bytes = os.urandom(16)
        message_bytes = message.encode("utf-8")
        payload = (
            random_bytes
            + struct.pack("!I", len(message_bytes))
            + message_bytes
            + owner_key.encode("utf-8")
        )
        padded = cls.pkcs7_pad(payload)
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
        return base64.b64encode(cipher.encrypt(padded)).decode("utf-8")

    @classmethod
    def parse_encrypt(cls, body: bytes) -> str:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(str(_("Invalid DingTalk callback body"))) from exc
        encrypt = payload.get("encrypt") if isinstance(payload, dict) else None
        if not encrypt:
            raise ValueError(str(_("Missing DingTalk callback payload")))
        return str(encrypt)

    @classmethod
    def verify_request(cls, application_id: str, query_params, body: bytes) -> dict:
        config = cls.get_callback_config(application_id)
        encrypt = cls.parse_encrypt(body)
        msg_signature = str(
            query_params.get("msg_signature") or query_params.get("signature") or ""
        )
        timestamp = str(
            query_params.get("timeStamp") or query_params.get("timestamp") or ""
        )
        nonce = str(query_params.get("nonce") or "")
        if not cls.verify_signature(
            config["token"], msg_signature, timestamp, nonce, encrypt
        ):
            raise ValueError(str(_("Invalid DingTalk callback signature")))
        message, owner_key = cls.decrypt_message(config["encoding_aes_key"], encrypt)
        if owner_key and owner_key != config["owner_key"]:
            raise ValueError(str(_("Invalid DingTalk callback owner key")))
        try:
            payload = json.loads(message)
        except json.JSONDecodeError as exc:
            raise ValueError(
                str(_("Invalid DingTalk decrypted callback payload"))
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError(str(_("Invalid DingTalk decrypted callback payload")))
        return payload

    @classmethod
    def build_success_response(cls, application_id: str) -> JsonResponse:
        config = cls.get_callback_config(application_id)
        timestamp = str(int(time.time()))
        nonce = base64.b16encode(os.urandom(8)).decode("utf-8").lower()
        encrypted = cls.encrypt_message(
            config["encoding_aes_key"], config["owner_key"], "success"
        )
        return JsonResponse(
            {
                "msg_signature": cls.build_signature(
                    config["token"], timestamp, nonce, encrypted
                ),
                "encrypt": encrypted,
                "timeStamp": timestamp,
                "nonce": nonce,
            }
        )

    @classmethod
    def route_message(cls, application_id: str, payload: dict) -> None:
        event_type = str(payload.get("EventType") or "")
        if event_type in ("", "check_url"):
            return
        if event_type in cls.supported_event_types:
            cls.handle_user_add_org(application_id, payload)
            return
        return

    @classmethod
    def handle_user_add_org(cls, application_id: str, payload: dict) -> None:
        user_ids = payload.get("userId")
        if not isinstance(user_ids, list) or len(user_ids) == 0:
            raise ValueError(str(_("Missing DingTalk callback userId")))
        event_id = str(payload.get("eventId") or "").strip()
        if (
            event_id
            and QuerySet(Chat)
            .filter(
                application_id=application_id,
                source__event_type="user_add_org",
                source__event_id=event_id,
            )
            .exists()
        ):
            return
        normalized_user_ids = [
            str(user_id).strip() for user_id in user_ids if str(user_id).strip()
        ]
        if len(normalized_user_ids) == 0:
            raise ValueError(str(_("Missing DingTalk callback userId")))
        for chat_user_id in normalized_user_ids:
            QuerySet(Chat).create(
                application_id=application_id,
                abstract=str(_("DingTalk user added to org")),
                chat_user_id=chat_user_id,
                chat_user_type=ChatUserType.PLATFORM_USER.value,
                asker={"username": chat_user_id},
                source={
                    "type": ChatSourceChoices.DINGTALK.value,
                    "event_type": "user_add_org",
                    "event_id": event_id,
                },
            )

    @classmethod
    def receive_callback(
        cls, application_id: str, query_params, body: bytes
    ) -> JsonResponse:
        payload = cls.verify_request(application_id, query_params, body)
        cls.route_message(application_id, payload)
        return cls.build_success_response(application_id)
