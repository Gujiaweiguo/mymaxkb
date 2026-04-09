from django.db.models import QuerySet
from rest_framework import serializers

from common.constants.permission_constants import (
    Group,
    PermissionConstants,
    Permission_Label,
    RoleConstants,
    SystemGroup,
)
from common.exception.app_exception import AppApiException
from common.result import Page
from users.models import User


SUPPORTED_SYSTEM_ROLES = [RoleConstants.ADMIN, RoleConstants.USER]


class SystemRoleItemSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    role_name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    create_user = serializers.CharField(required=True)
    internal = serializers.BooleanField(required=True)
    user_count = serializers.IntegerField(required=True)


class SystemRolePermissionActionSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    enable = serializers.BooleanField(required=True)


class SystemRolePermissionFeatureSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    permission = SystemRolePermissionActionSerializer(many=True, required=True)
    enable = serializers.BooleanField(required=True)


class SystemRolePermissionModuleSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    children = SystemRolePermissionFeatureSerializer(many=True, required=True)


class SystemRoleListResponseSerializer(serializers.Serializer):
    internal_role = SystemRoleItemSerializer(many=True, required=True)
    custom_role = SystemRoleItemSerializer(many=True, required=True)


class SystemRoleMemberItemSerializer(serializers.Serializer):
    user_relation_id = serializers.CharField(required=True)
    user_id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    nick_name = serializers.CharField(required=True)
    workspace_id = serializers.CharField(required=True, allow_blank=True)
    workspace_name = serializers.CharField(required=True, allow_blank=True)


class SystemRoleMemberPageQuerySerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nick_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SystemRoleSerializer(serializers.Serializer):
    @staticmethod
    def _get_role_enum(role_id: str):
        role_enum = next(
            (
                role_constant
                for role_constant in SUPPORTED_SYSTEM_ROLES
                if role_constant.value.name == role_id
            ),
            None,
        )
        if role_enum is None:
            raise AppApiException(500, "Role does not exist")
        return role_enum

    @staticmethod
    def _to_role_item(role_enum):
        role_value = role_enum.value
        return {
            "id": role_value.name,
            "role_name": role_value.name,
            "type": role_value.name,
            "create_user": "system",
            "internal": True,
            "user_count": QuerySet(User)
            .filter(role=role_value.name, is_active=True)
            .count(),
        }

    @classmethod
    def list(cls):
        return {
            "internal_role": [cls._to_role_item(role_enum) for role_enum in SUPPORTED_SYSTEM_ROLES],
            "custom_role": [],
        }

    @classmethod
    def permission_list(cls, role_id: str):
        role_enum = cls._get_role_enum(role_id)
        permission_items = []
        for permission_constant in PermissionConstants:
            permission = permission_constant.value
            if SystemGroup.ROLE not in (permission.parent_group or []):
                continue
            if role_enum not in permission.role_list:
                continue
            permission_items.append(
                {
                    "id": str(permission),
                    "name": str(Permission_Label.get(permission.operate.value, permission.operate.value)),
                    "enable": True,
                }
            )

        return [
            {
                "id": SystemGroup.ROLE.value,
                "name": str(Permission_Label.get(SystemGroup.ROLE.value, SystemGroup.ROLE.value)),
                "children": [
                    {
                        "id": Group.ROLE.value,
                        "name": str(Permission_Label.get(Group.ROLE.value, Group.ROLE.value)),
                        "permission": permission_items,
                        "enable": len(permission_items) > 0,
                    }
                ],
            }
        ]

    @classmethod
    def page(
        cls,
        role_id: str,
        query: dict[str, object],
        current_page: int,
        page_size: int,
    ):
        role_enum = cls._get_role_enum(role_id)
        query_data = {
            "username": query.get("username", [""])[0]
            if isinstance(query.get("username"), list)
            else query.get("username"),
            "nick_name": query.get("nick_name", [""])[0]
            if isinstance(query.get("nick_name"), list)
            else query.get("nick_name"),
        }
        SystemRoleMemberPageQuerySerializer(data=query_data).is_valid(
            raise_exception=True
        )

        query_set = QuerySet(User).filter(role=role_enum.value.name, is_active=True)
        if query_data.get("username"):
            query_set = query_set.filter(username__contains=query_data.get("username"))
        if query_data.get("nick_name"):
            query_set = query_set.filter(nick_name__contains=query_data.get("nick_name"))

        total = query_set.count()
        start = (current_page - 1) * page_size
        records = [
            {
                "user_relation_id": str(item.id),
                "user_id": item.id,
                "username": item.username,
                "nick_name": item.nick_name,
                "workspace_id": "",
                "workspace_name": "",
            }
            for item in query_set.order_by("create_time")[start : start + page_size]
        ]
        return Page(total, records, current_page, page_size)
