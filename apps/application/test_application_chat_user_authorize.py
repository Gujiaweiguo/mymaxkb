import json
import uuid_utils.compat as uuid
from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from application.models import Application, ApplicationFolder, ApplicationTypeChoices
from application.serializers.application_access_token import AccessTokenSerializer
from application.serializers.application_chat_user_authorize import (
    is_auth_application_chat_user,
)
from application.views.application_chat_user_authorize import (
    ChatUserAuthTypeView,
    SystemApplicationChatUserGroupUserView,
    SystemApplicationChatUserGroupView,
)
from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
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


class ApplicationChatUserAuthorizeTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email="admin@example.com",
            phone="",
            nick_name="admin-nick",
            username="admin-user",
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
            id="workspace-app-auth", name="workspace-app-auth"
        )
        self.folder = ApplicationFolder.objects.create(
            id="app-folder-auth",
            name="app-folder-auth",
            workspace_id=self.workspace.id,
            user=self.admin,
        )
        self.application = Application.objects.create(
            id=uuid.uuid7(),
            name="app-auth",
            desc="app-auth-desc",
            user=self.admin,
            folder=self.folder,
            workspace_id=self.workspace.id,
            type=ApplicationTypeChoices.SIMPLE,
            icon="./favicon.ico",
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
        group = self.create_group("group-app-auth")

        get_request = self.factory.get(
            f"/system/resource/APPLICATION/{self.application.id}/user_group"
        )
        force_authenticate(get_request, user=self.admin, token=self.auth_token)
        get_response = SystemApplicationChatUserGroupView.as_view()(
            get_request,
            resource_type="APPLICATION",
            resource_id=str(self.application.id),
        )
        get_payload = json.loads(get_response.content)

        self.assertEqual(get_response.status_code, 200)
        self.assertFalse(
            next(item for item in get_payload["data"] if item["id"] == group.id)[
                "is_auth"
            ]
        )

        put_request = self.factory.put(
            f"/system/resource/APPLICATION/{self.application.id}/user_group",
            data=[{"user_group_id": group.id, "is_auth": True}],
            format="json",
        )
        force_authenticate(put_request, user=self.admin, token=self.auth_token)
        put_response = SystemApplicationChatUserGroupView.as_view()(
            put_request,
            resource_type="APPLICATION",
            resource_id=str(self.application.id),
        )

        self.assertEqual(put_response.status_code, 200)
        self.assertTrue(
            ResourceChatUserGroupAuthorize.objects.filter(
                workspace_id=self.workspace.id,
                resource_type=ResourceType.APPLICATION,
                resource_id=self.application.id,
                user_group=group,
                is_auth=True,
            ).exists()
        )

    def test_user_authorization_page_and_update(self):
        group = self.create_group("group-user-auth")
        chat_user = self.create_chat_user("chat-user-app-auth")
        UserGroupRelation.objects.create(user=chat_user, group=group)

        page_request = self.factory.get(
            f"/system/resource/APPLICATION/{self.application.id}/user_group_id/{group.id}/1/20",
            data={"username": "chat-user-app-auth"},
        )
        force_authenticate(page_request, user=self.admin, token=self.auth_token)
        page_response = SystemApplicationChatUserGroupUserView.as_view()(
            page_request,
            resource_type="APPLICATION",
            resource_id=str(self.application.id),
            user_group_id=group.id,
            current_page=1,
            page_size=20,
        )
        page_payload = json.loads(page_response.content)

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_payload["data"]["total"], 1)
        self.assertFalse(page_payload["data"]["records"][0]["is_auth"])

        put_request = self.factory.put(
            f"/system/resource/APPLICATION/{self.application.id}/user_group_id/{group.id}",
            data=[{"chat_user_id": str(chat_user.id), "is_auth": True}],
            format="json",
        )
        force_authenticate(put_request, user=self.admin, token=self.auth_token)
        put_response = SystemApplicationChatUserGroupUserView.as_view()(
            put_request,
            resource_type="APPLICATION",
            resource_id=str(self.application.id),
            user_group_id=group.id,
        )

        self.assertEqual(put_response.status_code, 200)
        self.assertTrue(
            ResourceChatUserAuthorize.objects.filter(
                workspace_id=self.workspace.id,
                resource_type=ResourceType.APPLICATION,
                resource_id=self.application.id,
                user_group=group,
                user=chat_user,
                is_auth=True,
            ).exists()
        )

    def test_is_auth_application_chat_user_supports_group_and_user_grants(self):
        group = self.create_group("group-helper-auth")
        chat_user = self.create_chat_user("chat-user-helper-auth")
        UserGroupRelation.objects.create(user=chat_user, group=group)

        self.assertFalse(
            is_auth_application_chat_user(str(chat_user.id), str(self.application.id))
        )

        ResourceChatUserGroupAuthorize.objects.create(
            workspace_id=self.workspace.id,
            resource_type=ResourceType.APPLICATION,
            resource_id=self.application.id,
            user_group=group,
            is_auth=True,
        )
        self.assertTrue(
            is_auth_application_chat_user(str(chat_user.id), str(self.application.id))
        )

        ResourceChatUserGroupAuthorize.objects.filter(
            user_group=group, resource_id=self.application.id
        ).update(is_auth=False)
        ResourceChatUserAuthorize.objects.create(
            workspace_id=self.workspace.id,
            resource_type=ResourceType.APPLICATION,
            resource_id=self.application.id,
            user_group=group,
            user=chat_user,
            is_auth=True,
        )
        self.assertTrue(
            is_auth_application_chat_user(str(chat_user.id), str(self.application.id))
        )

    def test_access_token_serializer_returns_auth_fields_in_ce(self):
        result_data = AccessTokenSerializer(
            data={
                "workspace_id": self.workspace.id,
                "application_id": self.application.id,
            }
        ).edit(
            {
                "access_num": 10,
                "authentication": True,
                "authentication_value": {
                    "type": "password",
                    "password_value": "secret",
                    "max_attempts": 1,
                },
            }
        )

        self.assertTrue(result_data["authentication"])
        self.assertEqual(result_data["authentication_value"]["type"], "password")

    def test_chat_user_auth_type_endpoint_returns_options(self):
        request = self.factory.get("/chat_user/auth/types")
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserAuthTypeView.as_view()(request)
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(payload["data"]), 1)
