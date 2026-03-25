import base64
import hashlib
import os
import struct
from unittest.mock import patch

from Crypto.Cipher import AES
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationVersion,
    ApplicationTypeChoices,
    Chat,
    ChatRecord,
    ChatSourceChoices,
    ChatUserType,
)
from chat.views.wecom_callback import WecomApplicationCallbackView
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting, Workspace
from users.models import User


class WecomApplicationCallbackTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = QuerySet(User).create(
            id=uuid.uuid7(),
            email="wecom-callback@example.com",
            phone="",
            nick_name="wecom-callback-nick",
            username="wecom-callback-owner",
            password=password_encrypt("Secret1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-wecom-callback", name="workspace-wecom-callback"
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-wecom-callback",
            name="folder-wecom-callback",
            workspace_id=self.workspace.id,
            user=self.owner,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="WeCom Callback App",
            desc="desc",
            user=self.owner,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )
        self.application_version = ApplicationVersion.objects.create(
            application=self.application,
            workspace_id=self.workspace.id,
            application_name=self.application.name,
            user=self.owner,
            type=self.application.type,
            model_id=None,
        )
        self.token = "callback-token"
        self.raw_aes_key = b"0123456789abcdef0123456789abcdef"
        self.encoding_aes_key = (
            base64.b64encode(self.raw_aes_key).decode("utf-8").rstrip("=")
        )
        ApplicationAccessToken.objects.create(
            application=self.application,
            access_token="callback-access-token",
            is_active=True,
            authentication_value={
                "platform_config": {
                    "wecom": {
                        "config": {
                            "app_id": "app-id",
                            "agent_id": "agent-id",
                            "secret": "app-secret",
                            "token": self.token,
                            "encoding_aes_key": self.encoding_aes_key,
                            "callback_url": f"/api/chat/wecom/{self.application.id}",
                        },
                        "is_active": True,
                    }
                }
            },
        )
        SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                "wecom": {
                    "config": {
                        "corp_id": "corp-id",
                        "agent_id": "provider-agent-id",
                        "app_secret": "provider-secret",
                    },
                    "is_valid": True,
                    "is_active": True,
                    "state": "enabled",
                    "failure_reason": "",
                }
            },
        )

    def encrypt_message(self, message: str) -> str:
        message_bytes = message.encode("utf-8")
        plain = (
            os.urandom(16)
            + struct.pack("!I", len(message_bytes))
            + message_bytes
            + b"corp-id"
        )
        pad = 32 - (len(plain) % 32)
        plain += bytes([pad]) * pad
        encrypted = AES.new(
            self.raw_aes_key, AES.MODE_CBC, self.raw_aes_key[:16]
        ).encrypt(plain)
        return base64.b64encode(encrypted).decode("utf-8")

    def build_signature(
        self, value: str, timestamp: str = "1711276800", nonce: str = "nonce"
    ):
        signature = hashlib.sha1(
            "".join(sorted([self.token, timestamp, nonce, value])).encode("utf-8")
        ).hexdigest()
        return signature, timestamp, nonce

    def build_callback_path(self, signature: str, timestamp: str, nonce: str) -> str:
        return (
            f"/chat/wecom/{self.application.id}?msg_signature={signature}"
            f"&timestamp={timestamp}&nonce={nonce}"
        )

    @staticmethod
    def fake_answer_chat(self_obj, instance, base_to_response=None):
        chat_record = QuerySet(ChatRecord).get(id=instance["chat_record_id"])
        chat_record.answer_text = f"mock answer: {instance['message']}"
        chat_record.save(update_fields=["answer_text", "update_time"])
        return {"answer_text": chat_record.answer_text}

    def test_wecom_callback_get_returns_decrypted_echostr(self):
        echostr = self.encrypt_message("verify-ok")
        signature, timestamp, nonce = self.build_signature(echostr)
        request = self.factory.get(
            f"/chat/wecom/{self.application.id}",
            data={
                "msg_signature": signature,
                "timestamp": timestamp,
                "nonce": nonce,
                "echostr": echostr,
            },
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "verify-ok")

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_returns_success_after_decrypt(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello]]></Content><FromUserName><![CDATA[text-user-1]]></FromUserName><MsgId>msg-1</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        chat = QuerySet(Chat).get(application=self.application)
        self.assertEqual(chat.chat_user_id, "text-user-1")
        self.assertEqual(chat.chat_user_type, ChatUserType.PLATFORM_USER.value)
        self.assertEqual(chat.abstract, "hello")
        self.assertEqual(chat.chat_record_count, 1)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.problem_text, "hello")
        self.assertEqual(chat_record.answer_text, "mock answer: hello")
        self.assertEqual(chat_record.index, 1)
        self.assertEqual(
            chat_record.source["type"], ChatSourceChoices.ENTERPRISE_WECHAT.value
        )
        self.assertEqual(chat_record.source["msg_id"], "msg-1")
        mock_chat.assert_called_once()
        serializer_self = mock_chat.call_args[0][0]
        self.assertEqual(serializer_self.initial_data["source"]["msg_id"], "msg-1")
        mock_send.assert_called_once_with(
            to_user="text-user-1", agent_id="agent-id", content="mock answer: hello"
        )

    def test_wecom_callback_post_supports_enter_agent_event(self):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[enter_agent]]></Event><FromUserName><![CDATA[wecom-user-1]]></FromUserName></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 0)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        chat = QuerySet(Chat).get(application=self.application)
        self.assertEqual(chat.chat_user_id, "wecom-user-1")
        self.assertEqual(chat.chat_user_type, ChatUserType.PLATFORM_USER.value)
        self.assertEqual(chat.asker["username"], "wecom-user-1")
        self.assertEqual(chat.source["type"], ChatSourceChoices.ENTERPRISE_WECHAT.value)

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_reuses_enter_agent_chat_for_text(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        enter_encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[enter_agent]]></Event><FromUserName><![CDATA[wecom-user-2]]></FromUserName></xml>"
        )
        enter_signature, enter_timestamp, enter_nonce = self.build_signature(
            enter_encrypt
        )
        enter_request = self.factory.post(
            self.build_callback_path(enter_signature, enter_timestamp, enter_nonce),
            data=f"<xml><Encrypt><![CDATA[{enter_encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )
        enter_response = WecomApplicationCallbackView.as_view()(
            enter_request, application_id=str(self.application.id)
        )
        self.assertEqual(enter_response.status_code, 200)

        text_encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[follow up]]></Content><FromUserName><![CDATA[wecom-user-2]]></FromUserName><MsgId>msg-2</MsgId></xml>"
        )
        text_signature, text_timestamp, text_nonce = self.build_signature(text_encrypt)
        text_request = self.factory.post(
            self.build_callback_path(text_signature, text_timestamp, text_nonce),
            data=f"<xml><Encrypt><![CDATA[{text_encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        text_response = WecomApplicationCallbackView.as_view()(
            text_request, application_id=str(self.application.id)
        )

        self.assertEqual(text_response.status_code, 200)
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 1)
        chat = QuerySet(Chat).get(application=self.application)
        self.assertEqual(chat.chat_user_id, "wecom-user-2")
        self.assertEqual(chat.abstract, "follow up")
        self.assertEqual(chat.chat_record_count, 1)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.problem_text, "follow up")
        self.assertEqual(chat_record.answer_text, "mock answer: follow up")
        mock_chat.assert_called_once()
        mock_send.assert_called_once_with(
            to_user="wecom-user-2",
            agent_id="agent-id",
            content="mock answer: follow up",
        )

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_noops_duplicate_msg_id(self, mock_chat, mock_send):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello again]]></Content><FromUserName><![CDATA[text-user-3]]></FromUserName><MsgId>msg-dup</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        first_response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )
        second_request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )
        second_response = WecomApplicationCallbackView.as_view()(
            second_request, application_id=str(self.application.id)
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        chat = QuerySet(Chat).get(application=self.application)
        self.assertEqual(QuerySet(ChatRecord).filter(chat_id=chat.id).count(), 1)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.source["msg_id"], "msg-dup")
        self.assertEqual(chat_record.answer_text, "mock answer: hello again")
        mock_chat.assert_called_once()
        mock_send.assert_called_once_with(
            to_user="text-user-3",
            agent_id="agent-id",
            content="mock answer: hello again",
        )

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    def test_wecom_callback_post_real_text_flow_updates_same_record_and_preserves_msg_id(
        self, mock_send
    ):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[real hello]]></Content><FromUserName><![CDATA[text-user-real]]></FromUserName><MsgId>msg-real</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        chat = QuerySet(Chat).get(
            application=self.application, chat_user_id="text-user-real"
        )
        self.assertEqual(QuerySet(ChatRecord).filter(chat_id=chat.id).count(), 1)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.problem_text, "real hello")
        self.assertIn("AI model is not configured", chat_record.answer_text)
        self.assertEqual(chat_record.index, 1)
        self.assertEqual(
            chat_record.source["type"], ChatSourceChoices.ENTERPRISE_WECHAT.value
        )
        self.assertEqual(chat_record.source["msg_id"], "msg-real")
        mock_send.assert_called_once()

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_returns_success_when_outbound_send_raises_app_error(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        mock_send.side_effect = AppApiException(500, "send failed")
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello fail]]></Content><FromUserName><![CDATA[text-user-fail]]></FromUserName><MsgId>msg-fail</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        chat = QuerySet(Chat).get(application=self.application)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.answer_text, "mock answer: hello fail")
        mock_chat.assert_called_once()
        mock_send.assert_called_once()

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_returns_success_when_outbound_credentials_missing_after_local_success(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        setting = SystemSetting.objects.get(type=SettingType.PLATFORM_SOURCE)
        setting.meta["wecom"]["config"].pop("corp_id")
        setting.save()
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello no corp]]></Content><FromUserName><![CDATA[text-user-nocorp]]></FromUserName><MsgId>msg-nocorp</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        chat = QuerySet(Chat).get(application=self.application)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.answer_text, "mock answer: hello no corp")
        mock_chat.assert_called_once()
        mock_send.assert_not_called()

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_rejects_text_without_sender(
        self, mock_chat, mock_send
    ):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[hello]]></Content><MsgId>msg-3</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()
        mock_send.assert_not_called()

    @patch("common.platform.wecom_client.WecomClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_wecom_callback_post_rejects_text_without_content(
        self, mock_chat, mock_send
    ):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[text]]></MsgType><FromUserName><![CDATA[text-user-2]]></FromUserName><MsgId>msg-4</MsgId></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()
        mock_send.assert_not_called()

    def test_wecom_callback_post_noops_unsupported_event(self):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[unsubscribe]]></Event></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "success")
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 0)

    def test_wecom_callback_post_rejects_malformed_decrypted_xml(self):
        encrypt = self.encrypt_message("<xml><MsgType><![CDATA[text]]></MsgType>")
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)

    def test_wecom_callback_post_rejects_enter_agent_without_sender(self):
        encrypt = self.encrypt_message(
            "<xml><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[enter_agent]]></Event></xml>"
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            self.build_callback_path(signature, timestamp, nonce),
            data=f"<xml><Encrypt><![CDATA[{encrypt}]]></Encrypt></xml>",
            content_type="text/xml",
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)

    def test_wecom_callback_rejects_invalid_signature(self):
        echostr = self.encrypt_message("verify-ok")
        request = self.factory.get(
            f"/chat/wecom/{self.application.id}",
            data={
                "msg_signature": "bad-signature",
                "timestamp": "1711276800",
                "nonce": "nonce",
                "echostr": echostr,
            },
        )

        response = WecomApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
