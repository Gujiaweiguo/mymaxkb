import json
import uuid_utils.compat as uuid
from types import SimpleNamespace

from django.db.models import QuerySet
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants.permission_constants import RoleConstants
from common.utils.common import password_encrypt
from system_manage.models import ChatUser, UserGroup, UserGroupRelation
from system_manage.views.chat_user import (
    ChatUserBatchAddGroupView,
    ChatUserBatchDeleteView,
    ChatUserListView,
    ChatUserManageView,
    ChatUserOperateView,
    ChatUserPageView,
    ChatUserPasswordView,
    ChatUserSyncView,
    ChatUserSyncTypeView,
)
from system_manage.views.user_group import (
    UserGroupDeleteView,
    UserGroupMemberAddView,
    UserGroupMemberPageView,
    UserGroupMemberRemoveView,
    UserGroupView,
)
from users.models import User


class ChatUserManagementTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User(
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
        self.admin.save()
        self.auth_token = SimpleNamespace(
            role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[],
        )

    def create_chat_user(self, username: str, source: str = "LOCAL"):
        chat_user = ChatUser(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="13800000000",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            source=source,
            is_active=True,
        )
        chat_user.save()
        return chat_user

    def create_group(self, name: str):
        user_group = UserGroup(id=str(uuid.uuid7()), name=name)
        user_group.save()
        return user_group

    def test_chat_user_create_update_and_password_reset(self):
        group = self.create_group("group-a")

        create_request = self.factory.post(
            "/system/chat_user",
            data={
                "username": "chat-user-a",
                "email": "chat-user-a@example.com",
                "password": "Secret1!",
                "nick_name": "chat-user-a-nick",
                "phone": "13800138000",
                "user_group_ids": [group.id],
            },
            format="json",
        )
        force_authenticate(create_request, user=self.admin, token=self.auth_token)
        create_response = ChatUserManageView.as_view()(create_request)

        self.assertEqual(create_response.status_code, 200)
        created = QuerySet(ChatUser).get(username="chat-user-a")
        self.assertTrue(
            QuerySet(UserGroupRelation).filter(user=created, group=group).exists()
        )

        update_request = self.factory.put(
            f"/system/chat_user/{created.id}",
            data={
                "nick_name": "chat-user-a-renamed",
                "user_group_ids": [group.id],
                "is_active": False,
            },
            format="json",
        )
        force_authenticate(update_request, user=self.admin, token=self.auth_token)
        update_response = ChatUserOperateView.as_view()(
            update_request, user_id=str(created.id)
        )

        self.assertEqual(update_response.status_code, 200)
        created.refresh_from_db()
        self.assertEqual(created.nick_name, "chat-user-a-renamed")
        self.assertFalse(created.is_active)

        password_request = self.factory.put(
            f"/system/chat_user/{created.id}/re_password",
            data={"password": "Reset1!", "re_password": "Reset1!"},
            format="json",
        )
        force_authenticate(password_request, user=self.admin, token=self.auth_token)
        password_response = ChatUserPasswordView.as_view()(
            password_request, user_id=str(created.id)
        )

        self.assertEqual(password_response.status_code, 200)
        created.refresh_from_db()
        self.assertEqual(created.password, password_encrypt("Reset1!"))

    def test_chat_user_page_and_list_include_group_and_source(self):
        group = self.create_group("group-b")
        chat_user = self.create_chat_user("chat-user-b", source="LDAP")
        UserGroupRelation(user=chat_user, group=group).save()

        list_request = self.factory.get("/system/chat_user/list")
        force_authenticate(list_request, user=self.admin, token=self.auth_token)
        list_response = ChatUserListView.as_view()(list_request)
        list_payload = json.loads(list_response.content)

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_payload["data"][0]["source"], "LDAP")
        self.assertEqual(list_payload["data"][0]["user_group_names"], ["group-b"])

        page_request = self.factory.get(
            "/system/chat_user/user_manage/1/20", data={"username": "chat-user-b"}
        )
        force_authenticate(page_request, user=self.admin, token=self.auth_token)
        page_response = ChatUserPageView.as_view()(
            page_request, current_page=1, page_size=20
        )
        page_payload = json.loads(page_response.content)

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_payload["data"]["total"], 1)
        self.assertEqual(page_payload["data"]["records"][0]["username"], "chat-user-b")

    def test_batch_add_group_and_batch_delete(self):
        group_a = self.create_group("group-c")
        group_b = self.create_group("group-d")
        chat_user = self.create_chat_user("chat-user-c")
        UserGroupRelation(user=chat_user, group=group_a).save()

        add_group_request = self.factory.post(
            "/system/chat_user/batch_add_group",
            data={
                "ids": [str(chat_user.id)],
                "user_group_ids": [group_b.id],
                "is_append": True,
            },
            format="json",
        )
        force_authenticate(add_group_request, user=self.admin, token=self.auth_token)
        add_group_response = ChatUserBatchAddGroupView.as_view()(add_group_request)

        self.assertEqual(add_group_response.status_code, 200)
        self.assertEqual(QuerySet(UserGroupRelation).filter(user=chat_user).count(), 2)

        batch_delete_request = self.factory.post(
            "/system/chat_user/batch_delete",
            data=[str(chat_user.id)],
            format="json",
        )
        force_authenticate(batch_delete_request, user=self.admin, token=self.auth_token)
        batch_delete_response = ChatUserBatchDeleteView.as_view()(batch_delete_request)

        self.assertEqual(batch_delete_response.status_code, 200)
        self.assertFalse(QuerySet(ChatUser).filter(id=chat_user.id).exists())

    def test_batch_add_group_rejects_invalid_chat_user_id(self):
        group = self.create_group("group-invalid")
        request = self.factory.post(
            "/system/chat_user/batch_add_group",
            data={
                "ids": [str(uuid.uuid7())],
                "user_group_ids": [group.id],
                "is_append": True,
            },
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserBatchAddGroupView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)

    def test_batch_delete_rejects_invalid_request_shape(self):
        request = self.factory.post(
            "/system/chat_user/batch_delete",
            data={"ids": [str(uuid.uuid7())]},
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserBatchDeleteView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)

    def test_user_group_create_member_page_and_remove(self):
        chat_user = self.create_chat_user("chat-user-d", source="OIDC")

        create_group_request = self.factory.post(
            "/system/group", data={"name": "group-e"}, format="json"
        )
        force_authenticate(create_group_request, user=self.admin, token=self.auth_token)
        create_group_response = UserGroupView.as_view()(create_group_request)
        group_payload = json.loads(create_group_response.content)

        self.assertEqual(create_group_response.status_code, 200)
        group_id = group_payload["data"]["id"]

        add_member_request = self.factory.post(
            f"/system/group/{group_id}/add_member",
            data={"user_ids": [str(chat_user.id)]},
            format="json",
        )
        force_authenticate(add_member_request, user=self.admin, token=self.auth_token)
        add_member_response = UserGroupMemberAddView.as_view()(
            add_member_request, user_group_id=group_id
        )

        self.assertEqual(add_member_response.status_code, 200)

        page_request = self.factory.get(
            f"/system/group/{group_id}/user_list/1/20",
            data={"username": "chat-user-d"},
        )
        force_authenticate(page_request, user=self.admin, token=self.auth_token)
        page_response = UserGroupMemberPageView.as_view()(
            page_request, user_group_id=group_id, current_page=1, page_size=20
        )
        page_payload = json.loads(page_response.content)

        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_payload["data"]["total"], 1)
        relation_id = page_payload["data"]["records"][0]["user_group_relation_id"]

        remove_member_request = self.factory.post(
            f"/system/group/{group_id}/remove_member",
            data={"group_relation_ids": [relation_id]},
            format="json",
        )
        force_authenticate(
            remove_member_request, user=self.admin, token=self.auth_token
        )
        remove_member_response = UserGroupMemberRemoveView.as_view()(
            remove_member_request, user_group_id=group_id
        )

        self.assertEqual(remove_member_response.status_code, 200)
        self.assertFalse(QuerySet(UserGroupRelation).filter(id=relation_id).exists())

        delete_group_request = self.factory.delete(f"/system/group/{group_id}")
        force_authenticate(delete_group_request, user=self.admin, token=self.auth_token)
        delete_group_response = UserGroupDeleteView.as_view()(
            delete_group_request, user_group_id=group_id
        )

        self.assertEqual(delete_group_response.status_code, 200)
        self.assertFalse(QuerySet(UserGroup).filter(id=group_id).exists())

    def test_user_group_member_add_rejects_invalid_user_id(self):
        group = self.create_group("group-member-invalid")
        request = self.factory.post(
            f"/system/group/{group.id}/add_member",
            data={"user_ids": [str(uuid.uuid7())]},
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = UserGroupMemberAddView.as_view()(
            request, user_group_id=str(group.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)

    def test_user_group_member_remove_rejects_unknown_relation(self):
        group = self.create_group("group-remove-invalid")
        request = self.factory.post(
            f"/system/group/{group.id}/remove_member",
            data={"group_relation_ids": [str(uuid.uuid7())]},
            format="json",
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = UserGroupMemberRemoveView.as_view()(
            request, user_group_id=str(group.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)

    def test_sync_endpoint_is_not_supported_in_ce(self):
        request = self.factory.post(
            "/system/chat_user/sync/LDAP", data={}, format="json"
        )
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserSyncView.as_view()(request, sync_type="LDAP")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], 500)

    def test_sync_types_returns_empty_list_in_ce(self):
        request = self.factory.get("/system/chat_user/sync_types")
        force_authenticate(request, user=self.admin, token=self.auth_token)
        response = ChatUserSyncTypeView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], 200)
        self.assertEqual(payload["data"], [])
