import base64
import hashlib
import json
import os
import struct
from typing import cast
from unittest.mock import patch

from Crypto.Cipher import AES
import uuid_utils.compat as uuid
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
from chat.serializers.dingtalk_callback import DingtalkCallbackSerializer
from chat.views.dingtalk_callback import DingtalkApplicationCallbackView
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from system_manage.models import SettingType, SystemSetting, Workspace
from users.models import User
from django.db.models import QuerySet


class DingtalkApplicationCallbackTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = QuerySet(User).create(
            id=uuid.uuid7(),
            email="dingtalk-callback@example.com",
            phone="",
            nick_name="dingtalk-callback-nick",
            username="dingtalk-callback-owner",
            password=password_encrypt("Secret1!"),
            role="USER",
            source="LOCAL",
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id="workspace-dingtalk-callback", name="workspace-dingtalk-callback"
        )
        self.folder = ApplicationFolder.objects.create(
            id="folder-dingtalk-callback",
            name="folder-dingtalk-callback",
            workspace_id=self.workspace.id,
            user=self.owner,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="DingTalk Callback App",
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
                    "dingtalk": {
                        "config": {
                            "client_id": "client-id",
                            "client_secret": "client-secret",
                            "token": self.token,
                            "encoding_aes_key": self.encoding_aes_key,
                            "callback_url": f"/api/chat/dingtalk/{self.application.id}",
                        },
                        "is_active": True,
                    }
                }
            },
        )
        SystemSetting.objects.create(
            type=SettingType.PLATFORM_SOURCE,
            meta={
                "dingtalk": {
                    "config": {
                        "corp_id": "corp-id",
                        "app_key": "app-key",
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
        payload = (
            os.urandom(16)
            + struct.pack("!I", len(message.encode("utf-8")))
            + message.encode("utf-8")
            + b"app-key"
        )
        pad = 32 - (len(payload) % 32)
        payload += bytes([pad]) * pad
        encrypted = AES.new(
            self.raw_aes_key, AES.MODE_CBC, self.raw_aes_key[:16]
        ).encrypt(payload)
        return base64.b64encode(encrypted).decode("utf-8")

    def build_signature(
        self, value: str, timestamp: str = "1711276800", nonce: str = "nonce"
    ):
        signature = hashlib.sha1(
            "".join(sorted([nonce, timestamp, self.token, value])).encode("utf-8")
        ).hexdigest()
        return signature, timestamp, nonce

    @staticmethod
    def fake_answer_chat(self_obj, instance, base_to_response=None):
        chat_record = QuerySet(ChatRecord).get(id=instance["chat_record_id"])
        chat_record.answer_text = f"mock answer: {instance['message']}"
        chat_record.save(update_fields=["answer_text", "update_time"])
        return {"answer_text": chat_record.answer_text}

    def test_dingtalk_callback_post_returns_encrypted_success(self):
        encrypt = self.encrypt_message(json.dumps({"EventType": "check_url"}))
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(
            set(payload.keys()), {"msg_signature", "encrypt", "timeStamp", "nonce"}
        )
        message, owner_key = DingtalkCallbackSerializer.decrypt_message(
            self.encoding_aes_key, payload["encrypt"]
        )
        self.assertEqual(message, "success")
        self.assertEqual(owner_key, "app-key")

    def test_dingtalk_callback_rejects_invalid_signature(self):
        encrypt = self.encrypt_message(json.dumps({"EventType": "check_url"}))
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature=bad-signature&timeStamp=1711276800&nonce=nonce",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)

    def test_dingtalk_callback_rejects_inactive_config(self):
        access = ApplicationAccessToken.objects.get(application=self.application)
        access.authentication_value["platform_config"]["dingtalk"]["is_active"] = False
        access.save(update_fields=["authentication_value", "update_time"])
        encrypt = self.encrypt_message(json.dumps({"EventType": "check_url"}))
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)

    def test_dingtalk_callback_routes_user_add_org_to_chat_shell(self):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "EventType": "user_add_org",
                    "eventId": "event-1",
                    "userId": ["ding-user-1"],
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        asker = cast(dict, chat.asker)
        source = cast(dict, chat.source)
        self.assertEqual(chat.chat_user_id, "ding-user-1")
        self.assertEqual(chat.chat_user_type, ChatUserType.PLATFORM_USER.value)
        self.assertEqual(asker["username"], "ding-user-1")
        self.assertEqual(source["type"], ChatSourceChoices.DINGTALK.value)
        self.assertEqual(source["event_type"], "user_add_org")
        self.assertEqual(source["event_id"], "event-1")

    def test_dingtalk_callback_routes_all_users_in_user_add_org(self):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "EventType": "user_add_org",
                    "eventId": "event-multi",
                    "userId": ["ding-user-1", "ding-user-2"],
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 2)
        self.assertTrue(
            QuerySet(Chat)
            .filter(application=self.application, chat_user_id="ding-user-1")
            .exists()
        )
        self.assertTrue(
            QuerySet(Chat)
            .filter(application=self.application, chat_user_id="ding-user-2")
            .exists()
        )

    def test_dingtalk_callback_dedupes_repeated_user_add_org_event(self):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "EventType": "user_add_org",
                    "eventId": "event-dup",
                    "userId": ["ding-user-dup"],
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        first_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )
        second_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        first_response = DingtalkApplicationCallbackView.as_view()(
            first_request, application_id=str(self.application.id)
        )
        second_response = DingtalkApplicationCallbackView.as_view()(
            second_request, application_id=str(self.application.id)
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 1)

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_persists_chat_record_and_answer(
        self, mock_chat
    ):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-1",
                    "conversationId": "conv-1",
                    "senderStaffId": "ding-user-1",
                    "sessionWebhook": "https://oapi.dingtalk.com/robot/sendBySession?session=abc",
                    "text": {"content": "你好"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        self.assertEqual(chat.chat_user_id, "ding-user-1")
        self.assertEqual(chat.chat_user_type, ChatUserType.PLATFORM_USER.value)
        source = cast(dict, chat.source)
        self.assertEqual(source["type"], ChatSourceChoices.DINGTALK.value)
        self.assertEqual(source["conversation_id"], "conv-1")
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.problem_text, "你好")
        self.assertEqual(chat_record.answer_text, "mock answer: 你好")
        self.assertEqual(chat_record.source["msg_id"], "ding-msg-1")
        self.assertEqual(
            chat_record.source["session_webhook"],
            "https://oapi.dingtalk.com/robot/sendBySession?session=abc",
        )
        mock_chat.assert_called_once()

    @patch("common.platform.dingtalk_client.DingtalkClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_sends_outbound_reply(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-send",
                    "conversationId": "conv-send",
                    "senderStaffId": "ding-user-send",
                    "sessionWebhook": "https://oapi.dingtalk.com/robot/sendBySession?session=send",
                    "text": {"content": "发送消息"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once_with(
            session_webhook="https://oapi.dingtalk.com/robot/sendBySession?session=send",
            content="mock answer: 发送消息",
        )

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_dedupes_msg_id(self, mock_chat):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-dup",
                    "conversationId": "conv-dup",
                    "senderStaffId": "ding-user-dup",
                    "text": {"content": "重复消息"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        first_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )
        second_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        first_response = DingtalkApplicationCallbackView.as_view()(
            first_request, application_id=str(self.application.id)
        )
        second_response = DingtalkApplicationCallbackView.as_view()(
            second_request, application_id=str(self.application.id)
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        self.assertEqual(QuerySet(ChatRecord).filter(chat_id=chat.id).count(), 1)
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.source["msg_id"], "ding-msg-dup")
        self.assertEqual(chat_record.answer_text, "mock answer: 重复消息")
        mock_chat.assert_called_once()

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_duplicate_pending_record_does_not_rerun_answer(
        self, mock_chat
    ):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-pending",
                    "conversationId": "conv-pending",
                    "senderStaffId": "ding-user-pending",
                    "text": {"content": "处理中消息"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        first_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )
        second_request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        first_response = DingtalkApplicationCallbackView.as_view()(
            first_request, application_id=str(self.application.id)
        )
        second_response = DingtalkApplicationCallbackView.as_view()(
            second_request, application_id=str(self.application.id)
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        self.assertEqual(QuerySet(ChatRecord).filter(chat_id=chat.id).count(), 1)
        mock_chat.assert_called_once()

    @patch("common.platform.dingtalk_client.DingtalkClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_returns_success_when_outbound_send_fails(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        mock_send.side_effect = AppApiException(500, "send failed")
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-send-fail",
                    "conversationId": "conv-send-fail",
                    "senderStaffId": "ding-user-send-fail",
                    "sessionWebhook": "https://oapi.dingtalk.com/robot/sendBySession?session=fail",
                    "text": {"content": "发送失败"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.answer_text, "mock answer: 发送失败")
        mock_chat.assert_called_once()
        mock_send.assert_called_once()

    @patch("common.platform.dingtalk_client.DingtalkClient.send_text_message")
    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_returns_success_when_session_webhook_missing_after_local_success(
        self, mock_chat, mock_send
    ):
        mock_chat.side_effect = self.fake_answer_chat
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-no-webhook",
                    "conversationId": "conv-no-webhook",
                    "senderStaffId": "ding-user-no-webhook",
                    "text": {"content": "没有 webhook"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        chat = cast(Chat, QuerySet(Chat).get(application=self.application))
        chat_record = QuerySet(ChatRecord).get(chat_id=chat.id)
        self.assertEqual(chat_record.answer_text, "mock answer: 没有 webhook")
        mock_chat.assert_called_once()
        mock_send.assert_not_called()

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_rejects_missing_sender(self, mock_chat):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-no-sender",
                    "conversationId": "conv-no-sender",
                    "text": {"content": "你好"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_rejects_missing_content(self, mock_chat):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-no-content",
                    "conversationId": "conv-no-content",
                    "senderStaffId": "ding-user-no-content",
                    "text": {},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_rejects_missing_msg_id(self, mock_chat):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "conversationId": "conv-no-msg-id",
                    "senderStaffId": "ding-user-no-msg-id",
                    "text": {"content": "你好"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()

    @patch("chat.serializers.chat.ChatSerializers.chat", autospec=True)
    def test_dingtalk_callback_text_message_rejects_missing_conversation_id(
        self, mock_chat
    ):
        encrypt = self.encrypt_message(
            json.dumps(
                {
                    "msgtype": "text",
                    "msgId": "ding-msg-no-conv",
                    "senderStaffId": "ding-user-no-conv",
                    "text": {"content": "你好"},
                }
            )
        )
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
        mock_chat.assert_not_called()

    def test_dingtalk_callback_noops_unsupported_event(self):
        encrypt = self.encrypt_message(json.dumps({"EventType": "org_admin_add"}))
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuerySet(Chat).filter(application=self.application).count(), 0)

    def test_dingtalk_callback_rejects_user_add_org_without_user_id(self):
        encrypt = self.encrypt_message(json.dumps({"EventType": "user_add_org"}))
        signature, timestamp, nonce = self.build_signature(encrypt)
        request = self.factory.post(
            f"/chat/dingtalk/{self.application.id}?msg_signature={signature}&timeStamp={timestamp}&nonce={nonce}",
            data=json.dumps({"encrypt": encrypt}),
            content_type="application/json",
        )

        response = DingtalkApplicationCallbackView.as_view()(
            request, application_id=str(self.application.id)
        )

        self.assertEqual(response.status_code, 400)
