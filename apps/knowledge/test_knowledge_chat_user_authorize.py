import json
import uuid_utils.compat as uuid
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.utils.common import password_encrypt
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeType
from knowledge.serializers.knowledge_chat_user_authorize import (
    get_knowledge_list_of_authorized,
    is_auth_knowledge_chat_user,
)
from knowledge.views.knowledge_chat_user_authorize import (
    SystemKnowledgeChatUserGroupUserView,
    SystemKnowledgeChatUserGroupView,
)
from system_manage.models import (
    ChatUser,
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroup,
    UserGroupRelation,
    Workspace,
)
from users.models import User


class KnowledgeChatUserAuthorizeTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-knowledge-nick",
            username="admin-knowledge-user",
            password=password_encrypt("Secret1!"),
            role=RoleConstants.ADMIN.name,
            source="LOCAL",
            is_active=True,
        )
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )
        self.workspace = Workspace.objects.create(
            id="workspace-knowledge-auth", name="workspace-knowledge-auth"
        )
        self.folder = KnowledgeFolder.objects.create(
            id="knowledge-folder-auth",
            name="knowledge-folder-auth",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="knowledge-auth",
            desc="knowledge-auth-desc",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=KnowledgeType.BASE,
            meta={},
        )

    def create_group(self, name: str):
        return UserGroup.objects.create(id=str(uuid.uuid7()), name=name)

    def create_chat_user(self, username: str):
        return ChatUser.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="13800000000",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            source="LOCAL",
            is_active=True,
        )

    def test_group_authorization_round_trip(self):
        group = self.create_group("group-knowledge-auth")

        get_request = self.factory.get(
            f"/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group"
        )
        force_authenticate(get_request, user=self.admin, token=self.auth_token)
        get_response = SystemKnowledgeChatUserGroupView.as_view()(
            get_request,
            resource_id=str(self.knowledge.id),
        )
        get_payload = json.loads(get_response.content)

        self.assertEqual(get_response.status_code, 200)
        self.assertFalse(
            next(item for item in get_payload["data"] if item["id"] == group.id)[
                "is_auth"
            ]
        )

        put_request = self.factory.put(
            f"/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group",
            data=[{"user_group_id": group.id, "is_auth": True}],
            format="json",
        )
        force_authenticate(put_request, user=self.admin, token=self.auth_token)
        put_response = SystemKnowledgeChatUserGroupView.as_view()(
            put_request,
            resource_id=str(self.knowledge.id),
        )

        self.assertEqual(put_response.status_code, 200)
        self.assertTrue(
            ResourceChatUserGroupAuthorize.objects.filter(
                workspace_id=self.workspace.id,
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=self.knowledge.id,
                user_group=group,
                is_auth=True,
            ).exists()
        )

    def test_user_authorization_page_and_update(self):
        group = self.create_group("group-knowledge-user-auth")
        chat_user = self.create_chat_user("chat-user-knowledge-auth")
        UserGroupRelation.objects.create(user=chat_user, group=group)

        page_request = self.factory.get(
            f"/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group_id/{group.id}/1/20",
            data={"username": "chat-user-knowledge-auth"},
        )
        force_authenticate(page_request, user=self.admin, token=self.auth_token)
        page_response = SystemKnowledgeChatUserGroupUserView.as_view()(
            page_request,
            resource_id=str(self.knowledge.id),
            user_group_id=group.id,
            current_page=1,
            page_size=20,
        )
        page_payload = json.loads(page_response.content)

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_payload["data"]["total"], 1)
        self.assertFalse(page_payload["data"]["records"][0]["is_auth"])

        put_request = self.factory.put(
            f"/system/resource/KNOWLEDGE/{self.knowledge.id}/user_group_id/{group.id}",
            data=[{"chat_user_id": str(chat_user.id), "is_auth": True}],
            format="json",
        )
        force_authenticate(put_request, user=self.admin, token=self.auth_token)
        put_response = SystemKnowledgeChatUserGroupUserView.as_view()(
            put_request,
            resource_id=str(self.knowledge.id),
            user_group_id=group.id,
        )

        self.assertEqual(put_response.status_code, 200)
        self.assertTrue(
            ResourceChatUserAuthorize.objects.filter(
                workspace_id=self.workspace.id,
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=self.knowledge.id,
                user_group=group,
                user=chat_user,
                is_auth=True,
            ).exists()
        )

    def test_helper_supports_default_allow_group_and_user_grants(self):
        other_knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="knowledge-auth-2",
            desc="knowledge-auth-desc-2",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=KnowledgeType.BASE,
            meta={},
        )
        group = self.create_group("group-knowledge-helper-auth")
        chat_user = self.create_chat_user("chat-user-knowledge-helper-auth")
        UserGroupRelation.objects.create(user=chat_user, group=group)

        self.assertEqual(
            get_knowledge_list_of_authorized(
                str(chat_user.id), [str(self.knowledge.id), str(other_knowledge.id)]
            ),
            [str(self.knowledge.id), str(other_knowledge.id)],
        )

        ResourceChatUserGroupAuthorize.objects.create(
            workspace_id=self.workspace.id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=self.knowledge.id,
            user_group=group,
            is_auth=True,
        )
        self.assertTrue(
            is_auth_knowledge_chat_user(str(chat_user.id), str(self.knowledge.id))
        )
        self.assertEqual(
            get_knowledge_list_of_authorized(
                str(chat_user.id), [str(self.knowledge.id), str(other_knowledge.id)]
            ),
            [str(other_knowledge.id), str(self.knowledge.id)],
        )

        ResourceChatUserGroupAuthorize.objects.filter(
            user_group=group, resource_id=self.knowledge.id
        ).update(is_auth=False)
        self.assertFalse(
            is_auth_knowledge_chat_user(str(chat_user.id), str(self.knowledge.id))
        )

        ResourceChatUserAuthorize.objects.create(
            workspace_id=self.workspace.id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=self.knowledge.id,
            user_group=group,
            user=chat_user,
            is_auth=True,
        )
        self.assertTrue(
            is_auth_knowledge_chat_user(str(chat_user.id), str(self.knowledge.id))
        )

    def test_default_base_model_handle_registers_knowledge_authorize_helper(self):
        DatabaseModelManage.model_dict = {}
        DatabaseModelManage.init()

        registered = DatabaseModelManage.get_model("get_knowledge_list_of_authorized")
        self.assertIsNotNone(registered)
        self.assertEqual(registered, get_knowledge_list_of_authorized)
