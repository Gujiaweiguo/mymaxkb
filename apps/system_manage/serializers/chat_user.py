from collections import defaultdict

from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.common import password_encrypt
from system_manage.models import ChatUser, UserGroup, UserGroupRelation
from users.serializers.user import PASSWORD_REGEX


def _check_user_group_ids(user_group_ids: list[str]):
    if not user_group_ids:
        raise AppApiException(500, _("User groups are required"))
    existing_ids = set(
        QuerySet(UserGroup).filter(id__in=user_group_ids).values_list("id", flat=True)
    )
    if len(existing_ids) != len(set(user_group_ids)):
        raise AppApiException(500, _("User group does not exist"))


def _check_chat_user_ids(chat_user_ids: list[str]):
    if not chat_user_ids:
        raise AppApiException(500, _("Chat users are required"))
    existing_ids = set(
        QuerySet(ChatUser).filter(id__in=chat_user_ids).values_list("id", flat=True)
    )
    if len(existing_ids) != len(set(chat_user_ids)):
        raise AppApiException(500, _("Chat user does not exist"))


def _sync_user_groups(user_id: str, user_group_ids: list[str]):
    _check_user_group_ids(user_group_ids)
    QuerySet(UserGroupRelation).filter(user_id=user_id).delete()
    UserGroupRelation.objects.bulk_create(
        [
            UserGroupRelation(user_id=user_id, group_id=user_group_id)
            for user_group_id in user_group_ids
        ]
    )


def _get_user_group_map(user_ids: list[str]):
    group_ids_map: dict[str, list[str]] = defaultdict(list)
    group_names_map: dict[str, list[str]] = defaultdict(list)
    for relation in (
        QuerySet(UserGroupRelation).filter(user_id__in=user_ids).select_related("group")
    ):
        key = str(relation.user_id)
        group_ids_map[key].append(str(relation.group_id))
        group_names_map[key].append(relation.group.name)
    return group_ids_map, group_names_map


def serialize_chat_users(chat_user_list):
    user_ids = [str(chat_user.id) for chat_user in chat_user_list]
    group_ids_map, group_names_map = _get_user_group_map(user_ids)
    return [
        {
            "id": chat_user.id,
            "email": chat_user.email,
            "phone": chat_user.phone,
            "nick_name": chat_user.nick_name,
            "username": chat_user.username,
            "source": chat_user.source,
            "is_active": chat_user.is_active,
            "create_time": chat_user.create_time,
            "update_time": chat_user.update_time,
            "user_group_ids": group_ids_map.get(str(chat_user.id), []),
            "user_group_names": group_names_map.get(str(chat_user.id), []),
        }
        for chat_user in chat_user_list
    ]


class ChatUserInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    nick_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    source = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )
    user_group_names = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )


class ChatUserGroupAssignmentSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )
    is_append = serializers.BooleanField(required=True)

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        ids = list(dict.fromkeys(map(str, self.validated_data.get("ids", []))))
        user_group_ids = list(
            dict.fromkeys(map(str, self.validated_data.get("user_group_ids", [])))
        )
        _check_chat_user_ids(ids)
        _check_user_group_ids(user_group_ids)
        with transaction.atomic():
            if not self.validated_data.get("is_append"):
                QuerySet(UserGroupRelation).filter(user_id__in=ids).delete()
            exists_pairs = {
                (str(relation.user_id), str(relation.group_id))
                for relation in QuerySet(UserGroupRelation).filter(
                    user_id__in=ids, group_id__in=user_group_ids
                )
            }
            UserGroupRelation.objects.bulk_create(
                [
                    UserGroupRelation(user_id=user_id, group_id=user_group_id)
                    for user_id in ids
                    for user_group_id in user_group_ids
                    if (str(user_id), str(user_group_id)) not in exists_pairs
                ]
            )
        return True


class ChatUserBatchDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )

    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        chat_user_ids = list(
            dict.fromkeys(map(str, self.validated_data.get("ids", [])))
        )
        _check_chat_user_ids(chat_user_ids)
        QuerySet(ChatUser).filter(id__in=chat_user_ids).delete()
        return True


class ChatUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, min_length=6, max_length=20)
    re_password = serializers.CharField(required=True, min_length=6, max_length=20)

    def validate(self, attrs):
        password = attrs.get("password", "")
        re_password = attrs.get("re_password", "")
        if password != re_password:
            raise AppApiException(500, _("The two passwords do not match"))
        if PASSWORD_REGEX.match(password) is None:
            raise AppApiException(
                500,
                _(
                    "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                ),
            )
        return attrs

    def save(self, user_id: str):
        self.is_valid(raise_exception=True)
        chat_user = QuerySet(ChatUser).filter(id=user_id).first()
        if chat_user is None:
            raise AppApiException(500, _("Chat user does not exist"))
        chat_user.password = password_encrypt(self.validated_data.get("password"))
        chat_user.save(update_fields=["password"])
        return True


class ChatUserSyncSerializer(serializers.Serializer):
    @staticmethod
    def get_sync_types():
        return []

    @staticmethod
    def sync(sync_type: str):
        raise AppApiException(
            500, _("Chat user sync is not supported in community edition")
        )


class ChatUserManageSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        username = serializers.CharField(required=True, min_length=4, max_length=64)
        email = serializers.EmailField(
            required=False, allow_blank=True, allow_null=True
        )
        password = serializers.CharField(required=True, min_length=6, max_length=20)
        nick_name = serializers.CharField(required=True, min_length=1, max_length=64)
        phone = serializers.CharField(
            required=False, allow_blank=True, allow_null=True, max_length=20
        )
        source = serializers.CharField(required=False, default="LOCAL", max_length=20)
        is_active = serializers.BooleanField(required=False, default=True)
        user_group_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=True
        )

        def validate(self, attrs):
            username = attrs.get("username")
            nick_name = attrs.get("nick_name")
            if QuerySet(ChatUser).filter(username=username).exists():
                raise AppApiException(500, _("Username already exists"))
            if QuerySet(ChatUser).filter(nick_name=nick_name).exists():
                raise AppApiException(500, _("Nick name already exists"))
            if PASSWORD_REGEX.match(attrs.get("password", "")) is None:
                raise AppApiException(
                    500,
                    _(
                        "The password must be 6-20 characters long and must be a combination of letters, numbers, and special characters."
                    ),
                )
            _check_user_group_ids(
                list(dict.fromkeys(map(str, attrs.get("user_group_ids", []))))
            )
            return attrs

        def save(self, **kwargs):
            self.is_valid(raise_exception=True)
            with transaction.atomic():
                chat_user = ChatUser.objects.create(
                    username=self.validated_data.get("username"),
                    email=self.validated_data.get("email") or None,
                    password=password_encrypt(self.validated_data.get("password")),
                    nick_name=self.validated_data.get("nick_name"),
                    phone=self.validated_data.get("phone") or "",
                    source=self.validated_data.get("source", "LOCAL"),
                    is_active=self.validated_data.get("is_active", True),
                )
                _sync_user_groups(
                    str(chat_user.id),
                    list(
                        dict.fromkeys(
                            map(str, self.validated_data.get("user_group_ids", []))
                        )
                    ),
                )
            return serialize_chat_users([chat_user])[0]

    class Update(serializers.Serializer):
        username = serializers.CharField(required=False, min_length=4, max_length=64)
        email = serializers.EmailField(
            required=False, allow_blank=True, allow_null=True
        )
        nick_name = serializers.CharField(required=False, min_length=1, max_length=64)
        phone = serializers.CharField(
            required=False, allow_blank=True, allow_null=True, max_length=20
        )
        source = serializers.CharField(required=False, max_length=20)
        is_active = serializers.BooleanField(required=False)
        user_group_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=False
        )

        def validate(self, attrs):
            user_id = str(self.context.get("user_id"))
            username = attrs.get("username")
            nick_name = attrs.get("nick_name")
            if (
                username
                and QuerySet(ChatUser)
                .filter(username=username)
                .exclude(id=user_id)
                .exists()
            ):
                raise AppApiException(500, _("Username already exists"))
            if (
                nick_name
                and QuerySet(ChatUser)
                .filter(nick_name=nick_name)
                .exclude(id=user_id)
                .exists()
            ):
                raise AppApiException(500, _("Nick name already exists"))
            if "user_group_ids" in attrs:
                _check_user_group_ids(
                    list(dict.fromkeys(map(str, attrs.get("user_group_ids", []))))
                )
            return attrs

        def save(self, **kwargs):
            self.is_valid(raise_exception=True)
            user_id = str(self.context.get("user_id"))
            chat_user = QuerySet(ChatUser).filter(id=user_id).first()
            if chat_user is None:
                raise AppApiException(500, _("Chat user does not exist"))
            with transaction.atomic():
                for field in [
                    "username",
                    "email",
                    "nick_name",
                    "phone",
                    "source",
                    "is_active",
                ]:
                    if field in self.validated_data:
                        value = self.validated_data.get(field)
                        setattr(
                            chat_user,
                            field,
                            None
                            if field == "email" and value == ""
                            else (
                                value or ""
                                if field == "phone" and value is None
                                else value
                            ),
                        )
                chat_user.save()
                if "user_group_ids" in self.validated_data:
                    _sync_user_groups(
                        user_id,
                        list(
                            dict.fromkeys(
                                map(str, self.validated_data.get("user_group_ids", []))
                            )
                        ),
                    )
            return serialize_chat_users([chat_user])[0]

    class Query(serializers.Serializer):
        username = serializers.CharField(required=False, allow_blank=True)
        nick_name = serializers.CharField(required=False, allow_blank=True)
        is_active = serializers.BooleanField(required=False)
        source = serializers.CharField(required=False, allow_blank=True)

        def get_query_set(self):
            query_set = QuerySet(ChatUser)
            username = self.validated_data.get("username")
            nick_name = self.validated_data.get("nick_name")
            source = self.validated_data.get("source")
            if username:
                query_set = query_set.filter(username__contains=username)
            if nick_name:
                query_set = query_set.filter(nick_name__contains=nick_name)
            if "is_active" in self.validated_data:
                query_set = query_set.filter(
                    is_active=self.validated_data.get("is_active")
                )
            if source:
                query_set = query_set.filter(source=source)
            return query_set.order_by("-create_time")

        def list(self):
            self.is_valid(raise_exception=True)
            return serialize_chat_users(list(self.get_query_set()))

        def page(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)
            query_set = self.get_query_set()
            return page_search(
                current_page,
                page_size,
                query_set,
                post_records_handler=lambda record: serialize_chat_users([record])[0],
            )

    @staticmethod
    def delete(user_id: str):
        QuerySet(ChatUser).filter(id=user_id).delete()
        return True
