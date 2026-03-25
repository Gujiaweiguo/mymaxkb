from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from system_manage.models import (
    ChatUser,
    ResourceChatUserAuthorize,
    ResourceChatUserGroupAuthorize,
    ResourceType,
    UserGroup,
    UserGroupRelation,
)
from system_manage.serializers.login_auth_setting import LoginAuthSettingSerializer


class ApplicationChatUserGroupItemSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    is_auth = serializers.BooleanField(required=True)


class ApplicationChatUserGroupUserItemSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    is_auth = serializers.BooleanField(required=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    nick_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    source = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)


class ApplicationChatUserGroupEditSerializer(serializers.Serializer):
    user_group_id = serializers.CharField(required=True)
    is_auth = serializers.BooleanField(required=True)


class ApplicationChatUserEditSerializer(serializers.Serializer):
    chat_user_id = serializers.CharField(required=True)
    is_auth = serializers.BooleanField(required=True)


def _validate_resource_type(resource_type: str):
    if resource_type != ResourceType.APPLICATION.value:
        raise AppApiException(500, _("Unsupported resource type"))


def _validate_application(application_id: str, workspace_id: str | None = None):
    query_set = QuerySet(Application).filter(id=application_id)
    if workspace_id is not None:
        query_set = query_set.filter(workspace_id=workspace_id)
    application = query_set.first()
    if application is None:
        raise AppApiException(500, _("Application does not exist"))
    return application


def _validate_user_group(user_group_id: str):
    user_group = QuerySet(UserGroup).filter(id=user_group_id).first()
    if user_group is None:
        raise AppApiException(500, _("User group does not exist"))
    return user_group


def _validate_chat_users(chat_user_ids: list[str]):
    if not chat_user_ids:
        raise AppApiException(500, _("Chat users are required"))
    existing_ids = set(
        QuerySet(ChatUser).filter(id__in=chat_user_ids).values_list("id", flat=True)
    )
    if len(existing_ids) != len(set(chat_user_ids)):
        raise AppApiException(500, _("Chat user does not exist"))


def _serialize_relation(relation: UserGroupRelation, authorized_user_ids: set[str]):
    return {
        "id": relation.user.id,
        "is_auth": str(relation.user_id) in authorized_user_ids,
        "email": relation.user.email,
        "phone": relation.user.phone,
        "nick_name": relation.user.nick_name,
        "username": relation.user.username,
        "source": relation.user.source,
        "is_active": relation.user.is_active,
        "create_time": relation.user.create_time,
        "update_time": relation.user.update_time,
    }


class ApplicationChatUserAuthorizeSerializer(serializers.Serializer):
    class GroupQuery(serializers.Serializer):
        @staticmethod
        def list(
            resource_type: str, application_id: str, workspace_id: str | None = None
        ):
            _validate_resource_type(resource_type)
            application = _validate_application(application_id, workspace_id)
            auth_map = {
                str(item.user_group_id): item.is_auth
                for item in QuerySet(ResourceChatUserGroupAuthorize).filter(
                    workspace_id=application.workspace_id,
                    resource_type=resource_type,
                    resource_id=application.id,
                )
            }
            return [
                {
                    "id": user_group.id,
                    "name": user_group.name,
                    "is_auth": auth_map.get(str(user_group.id), False),
                }
                for user_group in QuerySet(UserGroup).order_by("name")
            ]

    class GroupOperate(serializers.Serializer):
        data = serializers.ListSerializer(
            child=ApplicationChatUserGroupEditSerializer(), required=True
        )

        def save(
            self,
            resource_type: str,
            application_id: str,
            workspace_id: str | None = None,
        ):
            self.is_valid(raise_exception=True)
            _validate_resource_type(resource_type)
            application = _validate_application(application_id, workspace_id)
            items = self.validated_data.get("data", [])
            user_group_ids = [str(item.get("user_group_id")) for item in items]
            for user_group_id in user_group_ids:
                _validate_user_group(user_group_id)
            exist_map = {
                str(item.user_group_id): item
                for item in QuerySet(ResourceChatUserGroupAuthorize).filter(
                    workspace_id=application.workspace_id,
                    resource_type=resource_type,
                    resource_id=application.id,
                    user_group_id__in=user_group_ids,
                )
            }
            create_list = []
            update_list = []
            for item in items:
                user_group_id = str(item.get("user_group_id"))
                is_auth = item.get("is_auth")
                exist = exist_map.get(user_group_id)
                if exist is None:
                    create_list.append(
                        ResourceChatUserGroupAuthorize(
                            workspace_id=application.workspace_id,
                            resource_type=resource_type,
                            resource_id=application.id,
                            user_group_id=user_group_id,
                            is_auth=is_auth,
                        )
                    )
                else:
                    exist.is_auth = is_auth
                    update_list.append(exist)
            if create_list:
                ResourceChatUserGroupAuthorize.objects.bulk_create(create_list)
            if update_list:
                QuerySet(ResourceChatUserGroupAuthorize).bulk_update(
                    update_list, ["is_auth"]
                )
            return True

    class UserQuery(serializers.Serializer):
        username = serializers.CharField(required=False, allow_blank=True)
        nick_name = serializers.CharField(required=False, allow_blank=True)
        source = serializers.CharField(required=False, allow_blank=True)

        def page(
            self,
            resource_type: str,
            application_id: str,
            user_group_id: str,
            current_page: int,
            page_size: int,
            workspace_id: str | None = None,
        ):
            self.is_valid(raise_exception=True)
            _validate_resource_type(resource_type)
            application = _validate_application(application_id, workspace_id)
            _validate_user_group(user_group_id)
            query_set = (
                QuerySet(UserGroupRelation)
                .filter(group_id=user_group_id)
                .select_related("user")
            )
            username = self.validated_data.get("username")
            nick_name = self.validated_data.get("nick_name")
            source = self.validated_data.get("source")
            if username:
                query_set = query_set.filter(user__username__contains=username)
            if nick_name:
                query_set = query_set.filter(user__nick_name__contains=nick_name)
            if source:
                query_set = query_set.filter(user__source=source)
            authorized_user_ids = set(
                map(
                    str,
                    QuerySet(ResourceChatUserAuthorize)
                    .filter(
                        workspace_id=application.workspace_id,
                        resource_type=resource_type,
                        resource_id=application.id,
                        user_group_id=user_group_id,
                        is_auth=True,
                    )
                    .values_list("user_id", flat=True),
                )
            )
            return page_search(
                current_page,
                page_size,
                query_set.order_by("-id"),
                post_records_handler=lambda relation: _serialize_relation(
                    relation, authorized_user_ids
                ),
            )

    class UserOperate(serializers.Serializer):
        data = serializers.ListSerializer(
            child=ApplicationChatUserEditSerializer(), required=True
        )

        def save(
            self,
            resource_type: str,
            application_id: str,
            user_group_id: str,
            workspace_id: str | None = None,
        ):
            self.is_valid(raise_exception=True)
            _validate_resource_type(resource_type)
            application = _validate_application(application_id, workspace_id)
            _validate_user_group(user_group_id)
            items = self.validated_data.get("data", [])
            chat_user_ids = [str(item.get("chat_user_id")) for item in items]
            _validate_chat_users(chat_user_ids)
            member_user_ids = set(
                map(
                    str,
                    QuerySet(UserGroupRelation)
                    .filter(group_id=user_group_id, user_id__in=chat_user_ids)
                    .values_list("user_id", flat=True),
                )
            )
            if len(member_user_ids) != len(set(chat_user_ids)):
                raise AppApiException(
                    500, _("Chat user does not belong to the user group")
                )
            exist_map = {
                str(item.user_id): item
                for item in QuerySet(ResourceChatUserAuthorize).filter(
                    workspace_id=application.workspace_id,
                    resource_type=resource_type,
                    resource_id=application.id,
                    user_group_id=user_group_id,
                    user_id__in=chat_user_ids,
                )
            }
            create_list = []
            update_list = []
            for item in items:
                chat_user_id = str(item.get("chat_user_id"))
                is_auth = item.get("is_auth")
                exist = exist_map.get(chat_user_id)
                if exist is None:
                    create_list.append(
                        ResourceChatUserAuthorize(
                            workspace_id=application.workspace_id,
                            resource_type=resource_type,
                            resource_id=application.id,
                            user_group_id=user_group_id,
                            user_id=chat_user_id,
                            is_auth=is_auth,
                        )
                    )
                else:
                    exist.is_auth = is_auth
                    update_list.append(exist)
            with transaction.atomic():
                if create_list:
                    ResourceChatUserAuthorize.objects.bulk_create(create_list)
                if update_list:
                    QuerySet(ResourceChatUserAuthorize).bulk_update(
                        update_list, ["is_auth"]
                    )
            return True

    @staticmethod
    def get_auth_types():
        return LoginAuthSettingSerializer.one().get("auth_types", [])


def is_auth_application_chat_user(chat_user_id: str, application_id: str) -> bool:
    application = QuerySet(Application).filter(id=application_id).first()
    if application is None:
        return False
    user_group_ids = list(
        map(
            str,
            QuerySet(UserGroupRelation)
            .filter(user_id=chat_user_id)
            .values_list("group_id", flat=True),
        )
    )
    if (
        QuerySet(ResourceChatUserGroupAuthorize)
        .filter(
            workspace_id=application.workspace_id,
            resource_type=ResourceType.APPLICATION,
            resource_id=application.id,
            user_group_id__in=user_group_ids,
            is_auth=True,
        )
        .exists()
    ):
        return True
    return (
        QuerySet(ResourceChatUserAuthorize)
        .filter(
            workspace_id=application.workspace_id,
            resource_type=ResourceType.APPLICATION,
            resource_id=application.id,
            user_id=chat_user_id,
            user_group_id__in=user_group_ids,
            is_auth=True,
        )
        .exists()
    )
