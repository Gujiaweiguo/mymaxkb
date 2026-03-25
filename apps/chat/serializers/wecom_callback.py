import base64
import binascii
import hashlib
from importlib import import_module
import xml.etree.ElementTree as ET
from typing import cast

from Crypto.Cipher import AES
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from application.models import Chat, ChatRecord, ChatSourceChoices, ChatUserType
from application.serializers.application_platform import (
    ApplicationPlatformManageSerializer,
)
from system_manage.models import SettingType
from system_manage.serializers.platform_source import PlatformSourceManageSerializer


class WecomCallbackSerializer:
    block_size = 32
    supported_event_types = {"enter_agent"}

    @classmethod
    def get_callback_config(cls, application_id: str) -> dict:
        status = ApplicationPlatformManageSerializer.get_config(application_id, "wecom")
        if not status.get("is_valid"):
            raise ValueError(str(_("WeCom application callback is not ready")))
        if not status.get("is_active"):
            raise ValueError(str(_("WeCom application callback is not enabled")))
        config = (
            status.get("config", {})
            if isinstance(status.get("config", {}), dict)
            else {}
        )
        token = config.get("token")
        encoding_aes_key = config.get("encoding_aes_key")
        if not token or not encoding_aes_key:
            raise ValueError(
                str(_("WeCom application callback is missing required credentials"))
            )
        provider = PlatformSourceManageSerializer.get(
            SettingType.PLATFORM_SOURCE, "wecom"
        )
        provider_config = (
            provider.get("config", {})
            if isinstance(provider.get("config", {}), dict)
            else {}
        )
        return {
            "token": str(token),
            "encoding_aes_key": str(encoding_aes_key),
            "receive_id": str(provider_config.get("corp_id") or ""),
        }

    @classmethod
    def build_signature(cls, token: str, timestamp: str, nonce: str, value: str) -> str:
        return hashlib.sha1(
            "".join(sorted([token, timestamp, nonce, value])).encode("utf-8")
        ).hexdigest()

    @classmethod
    def verify_signature(
        cls, token: str, msg_signature: str, timestamp: str, nonce: str, value: str
    ) -> bool:
        return cls.build_signature(token, timestamp, nonce, value) == msg_signature

    @classmethod
    def pkcs7_unpad(cls, value: bytes) -> bytes:
        pad = value[-1]
        if pad < 1 or pad > cls.block_size:
            raise ValueError(str(_("Invalid WeCom callback padding")))
        return value[:-pad]

    @classmethod
    def decrypt_message(cls, encoding_aes_key: str, encrypted: str) -> tuple[str, str]:
        try:
            aes_key = base64.b64decode(f"{encoding_aes_key}=")
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[:16])
            decrypted = cipher.decrypt(base64.b64decode(encrypted))
            plain = cls.pkcs7_unpad(decrypted)
            msg_len = int.from_bytes(plain[16:20], byteorder="big")
            message = plain[20 : 20 + msg_len].decode("utf-8")
            receive_id = plain[20 + msg_len :].decode("utf-8")
            return message, receive_id
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise ValueError(str(_("Invalid WeCom callback payload"))) from exc

    @classmethod
    def validate_receive_id(cls, expected_receive_id: str, actual_receive_id: str):
        if (
            expected_receive_id
            and actual_receive_id
            and expected_receive_id != actual_receive_id
        ):
            raise ValueError(str(_("Invalid WeCom callback receiver")))

    @classmethod
    def verify_request(
        cls,
        application_id: str,
        msg_signature: str,
        timestamp: str,
        nonce: str,
        value: str,
    ):
        config = cls.get_callback_config(application_id)
        if not cls.verify_signature(
            config["token"], msg_signature, timestamp, nonce, value
        ):
            raise ValueError(str(_("Invalid WeCom callback signature")))
        message, receive_id = cls.decrypt_message(config["encoding_aes_key"], value)
        cls.validate_receive_id(config["receive_id"], receive_id)
        return message

    @classmethod
    def verify_url(cls, application_id: str, query_params) -> HttpResponse:
        message = cls.verify_request(
            application_id,
            str(query_params.get("msg_signature") or ""),
            str(query_params.get("timestamp") or ""),
            str(query_params.get("nonce") or ""),
            str(query_params.get("echostr") or ""),
        )
        return HttpResponse(message.encode("utf-8"), content_type="text/plain")

    @classmethod
    def parse_encrypt(cls, body: bytes) -> str:
        try:
            xml_root = ET.fromstring(body.decode("utf-8"))
        except (ET.ParseError, UnicodeDecodeError) as exc:
            raise ValueError(str(_("Invalid WeCom callback XML"))) from exc
        encrypt = xml_root.findtext("Encrypt")
        if not encrypt:
            raise ValueError(str(_("Missing WeCom callback payload")))
        return encrypt

    @classmethod
    def parse_message_xml(cls, message: str) -> dict[str, str]:
        try:
            xml_root = ET.fromstring(message)
        except ET.ParseError as exc:
            raise ValueError(str(_("Invalid WeCom decrypted callback XML"))) from exc

        payload = {
            "msg_type": str(xml_root.findtext("MsgType") or "").strip(),
            "event": str(xml_root.findtext("Event") or "").strip(),
            "content": str(xml_root.findtext("Content") or "").strip(),
            "from_user_name": str(xml_root.findtext("FromUserName") or "").strip(),
            "msg_id": str(xml_root.findtext("MsgId") or "").strip(),
        }
        if not payload["msg_type"]:
            raise ValueError(str(_("Missing WeCom callback message type")))
        return payload

    @classmethod
    def route_message(cls, payload: dict[str, str]):
        msg_type = payload.get("msg_type", "")
        if msg_type == "text":
            cls.handle_text_message(payload)
            return
        if (
            msg_type == "event"
            and payload.get("event", "") in cls.supported_event_types
        ):
            cls.handle_enter_agent(payload)
            return
        return

    @classmethod
    def handle_enter_agent(cls, payload: dict[str, str]):
        from_user_name = payload.get("from_user_name", "")
        if not from_user_name:
            raise ValueError(str(_("Missing WeCom callback sender")))
        QuerySet(Chat).create(
            application_id=payload["application_id"],
            abstract=str(_("Enterprise WeChat enter agent")),
            chat_user_id=from_user_name,
            chat_user_type=ChatUserType.PLATFORM_USER.value,
            asker={"username": from_user_name},
            source={"type": ChatSourceChoices.ENTERPRISE_WECHAT.value},
        )

    @classmethod
    def get_or_create_wecom_chat(cls, payload: dict[str, str]) -> Chat:
        from_user_name = payload.get("from_user_name", "")
        if not from_user_name:
            raise ValueError(str(_("Missing WeCom callback sender")))
        chat = (
            QuerySet(Chat)
            .filter(
                application_id=payload["application_id"],
                chat_user_id=from_user_name,
                chat_user_type=ChatUserType.PLATFORM_USER.value,
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
                application_id=payload["application_id"],
                abstract=(
                    payload.get("content", "") or str(_("Enterprise WeChat text"))
                )[:1024],
                chat_user_id=from_user_name,
                chat_user_type=ChatUserType.PLATFORM_USER.value,
                asker={"username": from_user_name},
                source={"type": ChatSourceChoices.ENTERPRISE_WECHAT.value},
            ),
        )

    @classmethod
    def handle_text_message(cls, payload: dict[str, str]):
        content = payload.get("content", "")
        if not content:
            raise ValueError(str(_("Missing WeCom callback content")))
        chat = cls.get_or_create_wecom_chat(payload)
        existing_chat_record = cast(
            ChatRecord | None,
            cls.get_existing_text_record(str(chat.id), payload.get("msg_id", "")),
        )
        if existing_chat_record is not None:
            if existing_chat_record.answer_text:
                return
            cls.generate_text_answer(chat, existing_chat_record, payload)
            return
        next_index = QuerySet(ChatRecord).filter(chat_id=chat.id).count() + 1
        chat_record = QuerySet(ChatRecord).create(
            chat_id=chat.id,
            problem_text=content,
            answer_text="",
            index=next_index,
            source={
                "type": ChatSourceChoices.ENTERPRISE_WECHAT.value,
                "msg_id": payload.get("msg_id", ""),
            },
        )
        QuerySet(Chat).filter(id=chat.id).update(
            abstract=content[:1024],
            chat_record_count=next_index,
            update_time=timezone.now(),
        )
        cls.generate_text_answer(chat, chat_record, payload)

    @classmethod
    def get_existing_text_record(cls, chat_id: str, msg_id: str):
        if not msg_id:
            return None
        return (
            QuerySet(ChatRecord).filter(chat_id=chat_id, source__msg_id=msg_id).first()
        )

    @classmethod
    def generate_text_answer(
        cls, chat: Chat, chat_record: ChatRecord, payload: dict[str, str]
    ):
        chat_serializers_module = import_module("chat.serializers.chat")
        chat_serializer_cls = getattr(chat_serializers_module, "ChatSerializers")
        chat_serializer_cls(
            data={
                "chat_id": str(chat.id),
                "chat_user_id": payload["from_user_name"],
                "chat_user_type": ChatUserType.PLATFORM_USER.value,
                "application_id": payload["application_id"],
                "ip_address": "",
                "source": {
                    "type": ChatSourceChoices.ENTERPRISE_WECHAT.value,
                    "msg_id": payload.get("msg_id", ""),
                },
            }
        ).chat(
            instance={
                "message": payload["content"],
                "re_chat": False,
                "stream": False,
                "chat_record_id": str(chat_record.id),
                "form_data": {},
            }
        )

    @classmethod
    def receive_callback(
        cls, application_id: str, query_params, body: bytes
    ) -> HttpResponse:
        encrypt = cls.parse_encrypt(body)
        message = cls.verify_request(
            application_id,
            str(query_params.get("msg_signature") or ""),
            str(query_params.get("timestamp") or ""),
            str(query_params.get("nonce") or ""),
            encrypt,
        )
        payload = cls.parse_message_xml(message)
        payload["application_id"] = application_id
        cls.route_message(payload)
        return HttpResponse(b"success", content_type="text/plain")
