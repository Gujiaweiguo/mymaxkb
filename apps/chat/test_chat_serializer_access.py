import uuid_utils.compat as uuid

from django.test import TestCase

from application.models import (
    Application,
    ApplicationAccessToken,
    ApplicationFolder,
    ApplicationTypeChoices,
    ChatUserType,
)
from chat.serializers.chat import ChatSerializers
from common.exception.app_exception import ChatException
from common.utils.common import password_encrypt
from system_manage.models import (
    ChatUser,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroup,
    UserGroupRelation,
    Workspace,
)
from users.models import User


class ChatSerializerAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=uuid.uuid7(),
            email='chat-access-admin@example.com',
            phone='',
            nick_name='Chat Access Admin',
            username='chat-access-admin',
            password=password_encrypt('Admin123!'),
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.workspace = Workspace.objects.create(
            id='chat-access-workspace',
            name='Chat Access Workspace',
        )
        self.folder = ApplicationFolder.objects.create(
            id='chat-access-folder',
            name='Chat Access Folder',
            workspace_id=self.workspace.id,
            user=self.user,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name='chat-access-application',
            desc='chat access application',
            user=self.user,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon='./favicon.ico',
        )
        ApplicationAccessToken.objects.create(
            application=self.application,
            access_token='chat-access-token',
            authentication=True,
            authentication_value={'type': 'login'},
        )
        self.chat_user = ChatUser.objects.create(
            id=uuid.uuid7(),
            email='chat-user-access@example.com',
            phone='13800000000',
            nick_name='Chat User Access',
            username='chat-user-access',
            password=password_encrypt('User123!'),
            source='LOCAL',
            is_active=True,
        )

    def test_is_valid_chat_user_denies_login_auth_chat_user_without_application_access(self):
        serializer = ChatSerializers(
            data={
                'chat_id': uuid.uuid7(),
                'chat_user_id': str(self.chat_user.id),
                'chat_user_type': ChatUserType.CHAT_USER.value,
                'application_id': self.application.id,
                'debug': False,
                'source': {},
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(ChatException):
            serializer.is_valid_chat_user()

    def test_is_valid_chat_user_allows_login_auth_chat_user_with_group_access(self):
        user_group = UserGroup.objects.create(id=str(uuid.uuid7()), name='chat-access-group')
        UserGroupRelation.objects.create(user=self.chat_user, group=user_group)
        ResourceChatUserGroupAuthorize.objects.create(
            workspace_id=self.workspace.id,
            resource_type=ResourceType.APPLICATION,
            resource_id=self.application.id,
            user_group=user_group,
            is_auth=True,
        )
        serializer = ChatSerializers(
            data={
                'chat_id': uuid.uuid7(),
                'chat_user_id': str(self.chat_user.id),
                'chat_user_type': ChatUserType.CHAT_USER.value,
                'application_id': self.application.id,
                'debug': False,
                'source': {},
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.is_valid_chat_user()
