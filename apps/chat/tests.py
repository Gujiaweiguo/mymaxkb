import uuid_utils.compat as uuid
from django.test import TestCase

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_chat import (
    Chat,
    ChatRecord,
    ChatUserType,
    ChatSourceChoices,
    VoteChoices,
)
from common.utils.common import password_encrypt
from users.models import User


class ChatModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_application(self, user):
        folder = ApplicationFolder.objects.create(
            id="chat-folder",
            name="Chat Folder",
            user=user,
            workspace_id="default",
        )
        return Application.objects.create(
            id=uuid.uuid7(),
            name="Chat App",
            desc="Chat Description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_chat_creation(self):
        user = self.create_user("chat-user")
        app = self.create_application(user)
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=app,
            abstract="Test Chat",
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

        self.assertEqual(chat.abstract, "Test Chat")
        self.assertEqual(chat.chat_user_type, ChatUserType.ANONYMOUS_USER)
        self.assertEqual(chat.application, app)

    def test_chat_default_values(self):
        user = self.create_user("chat-default-user")
        app = self.create_application(user)
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=app,
            abstract="Default Chat",
        )

        self.assertEqual(chat.star_num, 0)
        self.assertEqual(chat.trample_num, 0)
        self.assertEqual(chat.chat_record_count, 0)
        self.assertEqual(chat.is_deleted, False)


class ChatRecordModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def create_application(self, user):
        folder = ApplicationFolder.objects.create(
            id="record-folder",
            name="Record Folder",
            user=user,
            workspace_id="default",
        )
        return Application.objects.create(
            id=uuid.uuid7(),
            name="Record App",
            desc="Record Description",
            user=user,
            folder=folder,
            workspace_id="default",
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
        )

    def test_chat_record_creation(self):
        user = self.create_user("record-user")
        app = self.create_application(user)
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=app,
            abstract="Record Chat",
        )
        record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=chat,
            problem_text="Hello, how are you?",
            answer_text="I'm doing well, thank you!",
        )

        self.assertEqual(record.problem_text, "Hello, how are you?")
        self.assertEqual(record.answer_text, "I'm doing well, thank you!")
        self.assertEqual(record.vote_status, VoteChoices.UN_VOTE)

    def test_chat_record_vote_update(self):
        user = self.create_user("vote-user")
        app = self.create_application(user)
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=app,
            abstract="Vote Chat",
        )
        record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=chat,
            problem_text="Question",
            answer_text="Answer",
        )

        record.vote_status = VoteChoices.STAR
        record.vote_reason = "accurate"
        record.save()

        record.refresh_from_db()
        self.assertEqual(record.vote_status, VoteChoices.STAR)
        self.assertEqual(record.vote_reason, "accurate")

    def test_chat_record_default_values(self):
        user = self.create_user("default-record-user")
        app = self.create_application(user)
        chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=app,
            abstract="Default Record Chat",
        )
        record = ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=chat,
            problem_text="Question",
            answer_text="Answer",
        )

        self.assertEqual(record.message_tokens, 0)
        self.assertEqual(record.answer_tokens, 0)
        self.assertEqual(record.star_num, 0)
        self.assertEqual(record.trample_num, 0)
