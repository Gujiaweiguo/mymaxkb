import uuid_utils.compat as uuid
from django.test import TestCase
from unittest.mock import patch

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.models.application_chat import (
    Chat,
    ChatRecord,
    ChatUserType,
    ChatSourceChoices,
    VoteChoices,
    VoteReasonChoices,
)
from chat.serializers.chat_record import VoteSerializer
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
            index=0,
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
            index=0,
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
            index=0,
        )

        self.assertEqual(record.message_tokens, 0)
        self.assertEqual(record.answer_tokens, 0)
        self.assertEqual(record.const, 0)
        self.assertEqual(record.vote_status, VoteChoices.UN_VOTE)


class VoteSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='vote-serializer@example.com',
            phone='',
            nick_name='vote-serializer-nick',
            username='vote-serializer-user',
            password=password_encrypt('Secret1!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.folder = ApplicationFolder.objects.create(
            id='vote-serializer-folder',
            name='Vote Serializer Folder',
            user=self.user,
            workspace_id='default',
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='Vote Serializer App',
            desc='Vote Serializer Description',
            user=self.user,
            folder=self.folder,
            workspace_id='default',
            type=ApplicationTypeChoices.SIMPLE,
            icon='./favicon.ico',
        )
        self.chat = Chat.objects.create(
            id=uuid.uuid7(),
            application=self.application,
            abstract='Vote Serializer Chat',
            chat_user_type=ChatUserType.ANONYMOUS_USER,
        )

    def create_record(self, vote_status=VoteChoices.UN_VOTE, vote_reason=None, vote_other_content=''):
        return ChatRecord.objects.create(
            id=uuid.uuid7(),
            chat=self.chat,
            problem_text='Question',
            answer_text='Answer',
            index=0,
            vote_status=vote_status,
            vote_reason=vote_reason,
            vote_other_content=vote_other_content,
        )

    def create_serializer(self, record):
        return VoteSerializer(
            data={
                'chat_id': str(self.chat.id),
                'chat_record_id': str(record.id),
            }
        )

    @patch('chat.serializers.chat_record.ChatCountSerializer.update_chat')
    @patch('chat.serializers.chat_record.RedisLock')
    def test_vote_serializer_stars_unvoted_record_and_persists_reason(self, redis_lock_cls, update_chat):
        redis_lock_cls.return_value.try_lock.return_value = True
        record = self.create_record()
        serializer = self.create_serializer(record)

        result = serializer.vote(
            {
                'vote_status': VoteChoices.STAR,
                'vote_reason': VoteReasonChoices.ACCURATE,
                'vote_other_content': 'helpful answer',
            }
        )

        record.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(record.vote_status, VoteChoices.STAR)
        self.assertEqual(record.vote_reason, VoteReasonChoices.ACCURATE)
        self.assertEqual(record.vote_other_content, 'helpful answer')
        update_chat.assert_called_once_with()
        redis_lock_cls.return_value.un_lock.assert_called_once_with(str(record.id))

    @patch('chat.serializers.chat_record.ChatCountSerializer.update_chat')
    @patch('chat.serializers.chat_record.RedisLock')
    def test_vote_serializer_tramples_unvoted_record_and_persists_reason(self, redis_lock_cls, update_chat):
        redis_lock_cls.return_value.try_lock.return_value = True
        record = self.create_record()
        serializer = self.create_serializer(record)

        result = serializer.vote(
            {
                'vote_status': VoteChoices.TRAMPLE,
                'vote_reason': VoteReasonChoices.INACCURATE,
                'vote_other_content': 'not correct',
            }
        )

        record.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(record.vote_status, VoteChoices.TRAMPLE)
        self.assertEqual(record.vote_reason, VoteReasonChoices.INACCURATE)
        self.assertEqual(record.vote_other_content, 'not correct')
        update_chat.assert_called_once_with()
        redis_lock_cls.return_value.un_lock.assert_called_once_with(str(record.id))

    @patch('chat.serializers.chat_record.ChatCountSerializer.update_chat')
    @patch('chat.serializers.chat_record.RedisLock')
    def test_vote_serializer_cancels_existing_vote_and_clears_reason(self, redis_lock_cls, update_chat):
        redis_lock_cls.return_value.try_lock.return_value = True
        record = self.create_record(
            vote_status=VoteChoices.STAR,
            vote_reason=VoteReasonChoices.ACCURATE,
            vote_other_content='helpful answer',
        )
        serializer = self.create_serializer(record)

        result = serializer.vote(
            {
                'vote_status': VoteChoices.UN_VOTE,
            }
        )

        record.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(record.vote_status, VoteChoices.UN_VOTE)
        self.assertIsNone(record.vote_reason)
        self.assertEqual(record.vote_other_content, '')
        update_chat.assert_called_once_with()
        redis_lock_cls.return_value.un_lock.assert_called_once_with(str(record.id))

    @patch('chat.serializers.chat_record.ChatCountSerializer.update_chat')
    @patch('chat.serializers.chat_record.RedisLock')
    def test_vote_serializer_rejects_switching_from_star_to_trample_without_cancel(self, redis_lock_cls, update_chat):
        redis_lock_cls.return_value.try_lock.return_value = True
        record = self.create_record(
            vote_status=VoteChoices.STAR,
            vote_reason=VoteReasonChoices.ACCURATE,
            vote_other_content='helpful answer',
        )
        serializer = self.create_serializer(record)

        with self.assertRaisesMessage(Exception, 'Already voted, please cancel first and then vote again'):
            serializer.vote(
                {
                    'vote_status': VoteChoices.TRAMPLE,
                    'vote_reason': VoteReasonChoices.INACCURATE,
                }
            )

        record.refresh_from_db()
        self.assertEqual(record.vote_status, VoteChoices.STAR)
        self.assertEqual(record.vote_reason, VoteReasonChoices.ACCURATE)
        self.assertEqual(record.vote_other_content, 'helpful answer')
        update_chat.assert_not_called()
        redis_lock_cls.return_value.un_lock.assert_called_once_with(str(record.id))

    @patch('chat.serializers.chat_record.ChatCountSerializer.update_chat')
    @patch('chat.serializers.chat_record.RedisLock')
    def test_vote_serializer_rejects_switching_from_trample_to_star_without_cancel(self, redis_lock_cls, update_chat):
        redis_lock_cls.return_value.try_lock.return_value = True
        record = self.create_record(
            vote_status=VoteChoices.TRAMPLE,
            vote_reason=VoteReasonChoices.INACCURATE,
            vote_other_content='not correct',
        )
        serializer = self.create_serializer(record)

        with self.assertRaisesMessage(Exception, 'Already voted, please cancel first and then vote again'):
            serializer.vote(
                {
                    'vote_status': VoteChoices.STAR,
                    'vote_reason': VoteReasonChoices.ACCURATE,
                }
            )

        record.refresh_from_db()
        self.assertEqual(record.vote_status, VoteChoices.TRAMPLE)
        self.assertEqual(record.vote_reason, VoteReasonChoices.INACCURATE)
        self.assertEqual(record.vote_other_content, 'not correct')
        update_chat.assert_not_called()
        redis_lock_cls.return_value.un_lock.assert_called_once_with(str(record.id))
