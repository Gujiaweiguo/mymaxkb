from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from system_manage.models import ChatUser, UserGroup, UserGroupRelation


def _check_chat_user_ids(user_ids: list[str]):
    if not user_ids:
        raise AppApiException(500, _("Chat users are required"))
    existing_ids = set(
        QuerySet(ChatUser).filter(id__in=user_ids).values_list("id", flat=True)
    )
    if len(existing_ids) != len(set(user_ids)):
        raise AppApiException(500, _("Chat user does not exist"))


class UserGroupInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)


class UserGroupMemberInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    nick_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    source = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)
    create_time = serializers.DateTimeField(required=True)
    update_time = serializers.DateTimeField(required=True)
    user_group_relation_id = serializers.CharField(required=True)


def serialize_user_group_members(relations):
    return [
        {
            "id": relation.user.id,
            "email": relation.user.email,
            "phone": relation.user.phone,
            "nick_name": relation.user.nick_name,
            "username": relation.user.username,
            "source": relation.user.source,
            "is_active": relation.user.is_active,
            "create_time": relation.user.create_time,
            "update_time": relation.user.update_time,
            "user_group_relation_id": relation.id,
        }
        for relation in relations
    ]


class UserGroupManageSerializer(serializers.Serializer):
    class CreateOrUpdate(serializers.Serializer):
        id = serializers.CharField(required=False, allow_blank=True)
        name = serializers.CharField(required=True, max_length=128)

        def validate(self, attrs):
            group_id = attrs.get("id")
            name = attrs.get("name")
            query_set = QuerySet(UserGroup).filter(name=name)
            if group_id:
                query_set = query_set.exclude(id=group_id)
            if query_set.exists():
                raise AppApiException(500, _("User group name already exists"))
            return attrs

        def save(self, **kwargs):
            self.is_valid(raise_exception=True)
            group_id = self.validated_data.get("id")
            if group_id:
                user_group = QuerySet(UserGroup).filter(id=group_id).first()
                if user_group is None:
                    raise AppApiException(500, _("User group does not exist"))
                user_group.name = self.validated_data.get("name")
                user_group.save(update_fields=["name"])
            else:
                user_group = UserGroup.objects.create(
                    name=self.validated_data.get("name")
                )
            return {"id": str(user_group.id), "name": user_group.name}

    class AddMember(serializers.Serializer):
        user_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=True
        )

        def save(self, user_group_id: str):
            self.is_valid(raise_exception=True)
            if not QuerySet(UserGroup).filter(id=user_group_id).exists():
                raise AppApiException(500, _("User group does not exist"))
            user_ids = list(
                dict.fromkeys(map(str, self.validated_data.get("user_ids", [])))
            )
            _check_chat_user_ids(user_ids)
            existing_pairs = {
                str(relation.user_id)
                for relation in QuerySet(UserGroupRelation).filter(
                    group_id=user_group_id, user_id__in=user_ids
                )
            }
            with transaction.atomic():
                UserGroupRelation.objects.bulk_create(
                    [
                        UserGroupRelation(group_id=user_group_id, user_id=user_id)
                        for user_id in user_ids
                        if str(user_id) not in existing_pairs
                    ]
                )
            return True

    class RemoveMember(serializers.Serializer):
        group_relation_ids = serializers.ListField(
            child=serializers.CharField(required=True), required=True
        )

        def save(self, user_group_id: str):
            self.is_valid(raise_exception=True)
            if not QuerySet(UserGroup).filter(id=user_group_id).exists():
                raise AppApiException(500, _("User group does not exist"))
            relation_ids = list(
                dict.fromkeys(
                    map(str, self.validated_data.get("group_relation_ids", []))
                )
            )
            existing_relation_ids = set(
                QuerySet(UserGroupRelation)
                .filter(group_id=user_group_id, id__in=relation_ids)
                .values_list("id", flat=True)
            )
            if len(existing_relation_ids) != len(set(relation_ids)):
                raise AppApiException(500, _("User group relation does not exist"))
            QuerySet(UserGroupRelation).filter(
                group_id=user_group_id,
                id__in=relation_ids,
            ).delete()
            return True

    class MemberQuery(serializers.Serializer):
        username = serializers.CharField(required=False, allow_blank=True)
        nick_name = serializers.CharField(required=False, allow_blank=True)
        source = serializers.CharField(required=False, allow_blank=True)

        def get_query_set(self, user_group_id: str):
            query_set = (
                QuerySet(UserGroupRelation)
                .filter(group_id=user_group_id)
                .select_related("user")
                .order_by("-id")
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
            return query_set

        def page(self, user_group_id: str, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)
            query_set = self.get_query_set(user_group_id)
            return page_search(
                current_page,
                page_size,
                query_set,
                post_records_handler=lambda relation: serialize_user_group_members(
                    [relation]
                )[0],
            )

    @staticmethod
    def list():
        return [
            {"id": str(user_group.id), "name": user_group.name}
            for user_group in QuerySet(UserGroup).order_by("name")
        ]

    @staticmethod
    def delete(user_group_id: str):
        QuerySet(UserGroup).filter(id=user_group_id).delete()
        return True
