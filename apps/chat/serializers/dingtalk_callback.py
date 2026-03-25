import base64
import binascii
import hashlib
from importlib import import_module
import json
import os
import struct
import time
import traceback
from typing import cast

from Crypto.Cipher import AES
from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from application.models import (
    Application,
    Chat,
    ChatRecord,
    ChatSourceChoices,
    ChatUserType,
)
from application.serializers.application_platform import (
    ApplicationPlatformManageSerializer,
)
from common.platform.dingtalk_client import DingtalkClient
from common.utils.logger import maxkb_logger
from system_manage.models import SettingType
from system_manage.serializers.platform_source import PlatformSourceManageSerializer


class DingtalkCallbackSerializer:
    block_size = 32
    supported_event_types = {"user_add_org"}
    supported_message_types = {"text"}

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
        msg_type = str(payload.get("msgtype") or "").strip().lower()
        if msg_type in cls.supported_message_types:
            cls.handle_text_message(application_id, payload)
            return
        event_type = str(payload.get("EventType") or "")
        if event_type in ("", "check_url"):
            return
        if event_type in cls.supported_event_types:
            cls.handle_user_add_org(application_id, payload)
            return
        return

    @classmethod
    def resolve_chat_user_id(cls, payload: dict) -> str:
        chat_user_id = str(
            payload.get("senderStaffId") or payload.get("senderId") or ""
        ).strip()
        if not chat_user_id:
            raise ValueError(str(_("Missing DingTalk callback sender")))
        return chat_user_id

    @classmethod
    def normalize_text_payload(cls, payload: dict) -> dict[str, str]:
        return {
            "chat_user_id": cls.resolve_chat_user_id(payload),
            "conversation_id": str(payload.get("conversationId") or "").strip(),
            "msg_id": str(payload.get("msgId") or "").strip(),
            "content": cls.get_text_content(payload),
            "session_webhook": str(payload.get("sessionWebhook") or "").strip(),
        }

    @classmethod
    def get_or_create_dingtalk_chat(
        cls, application_id: str, message_payload: dict[str, str]
    ) -> Chat:
        chat_user_id = message_payload["chat_user_id"]
        conversation_id = message_payload["conversation_id"]
        chat = (
            QuerySet(Chat)
            .filter(
                application_id=application_id,
                chat_user_id=chat_user_id,
                chat_user_type=ChatUserType.PLATFORM_USER.value,
                source__type=ChatSourceChoices.DINGTALK.value,
                source__conversation_id=conversation_id,
                is_deleted=False,
            )
            .order_by("-create_time")
            .first()
        )
        if chat is not None:
            return cast(Chat, chat)
        return cast(
            Chat,
            QuerySet(Chat).create(
                application_id=application_id,
                abstract=(message_payload["content"] or str(_("DingTalk text")))[:1024],
                chat_user_id=chat_user_id,
                chat_user_type=ChatUserType.PLATFORM_USER.value,
                asker={"username": chat_user_id},
                source={
                    "type": ChatSourceChoices.DINGTALK.value,
                    "conversation_id": conversation_id,
                    "sender_id": chat_user_id,
                },
            ),
        )

    @classmethod
    def get_text_content(cls, payload: dict) -> str:
        text = payload.get("text")
        if not isinstance(text, dict):
            raise ValueError(str(_("Missing DingTalk callback content")))
        content = str(text.get("content") or "").strip()
        if not content:
            raise ValueError(str(_("Missing DingTalk callback content")))
        return content

    @classmethod
    def get_existing_text_record(cls, chat_id: str, msg_id: str):
        if not msg_id:
            return None
        return (
            QuerySet(ChatRecord).filter(chat_id=chat_id, source__msg_id=msg_id).first()
        )

    @classmethod
    def handle_text_message(cls, application_id: str, payload: dict) -> None:
        message_payload = cls.normalize_text_payload(payload)
        if not message_payload["conversation_id"]:
            raise ValueError(str(_("Missing DingTalk callback conversationId")))
        if not message_payload["msg_id"]:
            raise ValueError(str(_("Missing DingTalk callback msgId")))
        with transaction.atomic():
            QuerySet(Application).select_for_update().filter(id=application_id).first()
            chat = cls.get_or_create_dingtalk_chat(application_id, message_payload)
            existing_chat_record = cast(
                ChatRecord | None,
                cls.get_existing_text_record(str(chat.id), message_payload["msg_id"]),
            )
            if existing_chat_record is not None:
                return
            next_index = QuerySet(ChatRecord).filter(chat_id=chat.id).count() + 1
            chat_record = QuerySet(ChatRecord).create(
                chat_id=chat.id,
                problem_text=message_payload["content"],
                answer_text="",
                index=next_index,
                source={
                    "type": ChatSourceChoices.DINGTALK.value,
                    "msg_id": message_payload["msg_id"],
                    "conversation_id": message_payload["conversation_id"],
                    "session_webhook": message_payload["session_webhook"],
                    "sender_id": message_payload["chat_user_id"],
                },
            )
            QuerySet(Chat).filter(id=chat.id).update(
                abstract=message_payload["content"][:1024],
                chat_record_count=next_index,
                update_time=timezone.now(),
                source={
                    "type": ChatSourceChoices.DINGTALK.value,
                    "conversation_id": message_payload["conversation_id"],
                    "sender_id": message_payload["chat_user_id"],
                },
            )
        cls.generate_text_answer(
            chat, chat_record, application_id, payload, message_payload
        )

    @classmethod
    def generate_text_answer(
        cls,
        chat: Chat,
        chat_record: ChatRecord,
        application_id: str,
        payload: dict,
        message_payload: dict[str, str],
    ) -> None:
        chat_serializers_module = import_module("chat.serializers.chat")
        chat_serializer_cls = getattr(chat_serializers_module, "ChatSerializers")
        chat_serializer_cls(
            data={
                "chat_id": str(chat.id),
                "chat_user_id": message_payload["chat_user_id"],
                "chat_user_type": ChatUserType.PLATFORM_USER.value,
                "application_id": application_id,
                "ip_address": "",
                "source": {
                    "type": ChatSourceChoices.DINGTALK.value,
                    "msg_id": message_payload["msg_id"],
                    "conversation_id": message_payload["conversation_id"],
                    "session_webhook": message_payload["session_webhook"],
                    "sender_id": message_payload["chat_user_id"],
                },
            }
        ).chat(
            instance={
                "message": message_payload["content"],
                "re_chat": False,
                "stream": False,
                "chat_record_id": str(chat_record.id),
                "form_data": {},
            }
        )
        chat_record.refresh_from_db()
        try:
            cls.send_text_reply(chat_record, message_payload)
        except Exception as exc:
            maxkb_logger.error(
                _("DingTalk outbound reply failed {error}{traceback}").format(
                    error=str(exc), traceback=traceback.format_exc()
                )
            )

    @classmethod
    def send_text_reply(
        cls, chat_record: ChatRecord, message_payload: dict[str, str]
    ) -> None:
        answer_text = str(chat_record.answer_text or "").strip()
        if not answer_text:
            return
        session_webhook = message_payload.get("session_webhook", "")
        if not session_webhook:
            raise ValueError(
                str(_("DingTalk outbound response is missing session webhook"))
            )
        DingtalkClient.send_text_message(
            session_webhook=session_webhook, content=answer_text
        )

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
