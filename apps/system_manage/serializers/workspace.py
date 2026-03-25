# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： workspace.py
@date：2026/3/23
@desc:
"""

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application, ApplicationFolder
from common.exception.app_exception import AppApiException
from common.result import Page
from common.constants.permission_constants import RoleConstants
from knowledge.models import Knowledge, KnowledgeFolder, KnowledgeWorkflow
from models_provider.models import Model
from system_manage.models import (
    Workspace,
    WorkspaceMember,
    WorkspaceUserResourcePermission,
)
from tools.models import Tool, ToolFolder
from trigger.models import Trigger
from users.models import User


DEFAULT_WORKSPACE_ID = "default"
DEFAULT_WORKSPACE_NAME = "default"


def ensure_default_workspace():
    workspace = QuerySet(Workspace).filter(id=DEFAULT_WORKSPACE_ID).first()
    if workspace is None:
        workspace = Workspace(id=DEFAULT_WORKSPACE_ID, name=DEFAULT_WORKSPACE_NAME)
        workspace.save(force_insert=True)
    return workspace


def get_workspace_user_count(workspace_id: str):
    if workspace_id == DEFAULT_WORKSPACE_ID:
        return QuerySet(User).filter(is_active=True).count()
    return QuerySet(WorkspaceMember).filter(workspace_id=workspace_id).count()


def get_workspace_constraint_counts(workspace_id: str):
    return {
        "application": QuerySet(Application).filter(workspace_id=workspace_id).count(),
        "application_folder": QuerySet(ApplicationFolder)
        .filter(workspace_id=workspace_id)
        .count(),
        "knowledge": QuerySet(Knowledge).filter(workspace_id=workspace_id).count(),
        "knowledge_folder": QuerySet(KnowledgeFolder)
        .filter(workspace_id=workspace_id)
        .count(),
        "knowledge_workflow": QuerySet(KnowledgeWorkflow)
        .filter(workspace_id=workspace_id)
        .count(),
        "tool": QuerySet(Tool).filter(workspace_id=workspace_id).count(),
        "tool_folder": QuerySet(ToolFolder).filter(workspace_id=workspace_id).count(),
        "model": QuerySet(Model).filter(workspace_id=workspace_id).count(),
        "trigger": QuerySet(Trigger).filter(workspace_id=workspace_id).count(),
        "resource_permission": QuerySet(WorkspaceUserResourcePermission)
        .filter(workspace_id=workspace_id)
        .count(),
    }


def get_workspace_delete_check(workspace_id: str):
    ensure_default_workspace()
    workspace = QuerySet(Workspace).filter(id=workspace_id).first()
    if workspace is None:
        raise AppApiException(500, "Workspace does not exist")
    if workspace.id == DEFAULT_WORKSPACE_ID:
        return {
            "can_delete": False,
            "message": "Default workspace cannot be deleted",
        }
    constraint_counts = get_workspace_constraint_counts(workspace_id)
    if any(count > 0 for count in constraint_counts.values()):
        return {
            "can_delete": False,
            "message": "Workspace still contains constrained resources",
        }
    return {
        "can_delete": True,
        "message": "",
    }


class WorkspaceItemSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    user_count = serializers.IntegerField(required=True)


class WorkspaceDeleteCheckSerializer(serializers.Serializer):
    can_delete = serializers.BooleanField(required=True)
    message = serializers.CharField(required=True)


class WorkspaceOperateSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=True, max_length=64)

    def _check_name_unique(self, workspace_id=None):
        name = self.validated_data.get("name")
        query_set = QuerySet(Workspace).filter(name=name)
        if workspace_id is not None:
            query_set = query_set.exclude(id=workspace_id)
        if query_set.exists():
            raise AppApiException(500, "Workspace name already exists")

    @transaction.atomic
    def save(self):
        self.is_valid(raise_exception=True)
        ensure_default_workspace()
        workspace_id = self.validated_data.get("id")
        if workspace_id:
            workspace = QuerySet(Workspace).filter(id=workspace_id).first()
            if workspace is None:
                raise AppApiException(500, "Workspace does not exist")
            self._check_name_unique(workspace.id)
            workspace.name = self.validated_data.get("name")
            workspace.save(update_fields=["name", "update_time"])
            return workspace

        self._check_name_unique()
        workspace = Workspace(name=self.validated_data.get("name"))
        workspace.save()
        return workspace


class WorkspaceQuerySerializer(serializers.Serializer):
    @staticmethod
    def list():
        ensure_default_workspace()
        return [
            {
                "id": workspace.id,
                "name": workspace.name,
                "user_count": get_workspace_user_count(workspace.id),
            }
            for workspace in QuerySet(Workspace).all().order_by("create_time")
        ]

    @staticmethod
    def delete_check(workspace_id: str):
        return get_workspace_delete_check(workspace_id)

    @staticmethod
    @transaction.atomic
    def delete(workspace_id: str):
        delete_check = get_workspace_delete_check(workspace_id)
        if not delete_check.get("can_delete"):
            raise AppApiException(500, delete_check.get("message"))
        QuerySet(WorkspaceMember).filter(workspace_id=workspace_id).delete()
        QuerySet(Workspace).filter(id=workspace_id).delete()
        return True


class WorkspaceMemberItemSerializer(serializers.Serializer):
    user_relation_id = serializers.UUIDField(required=True)
    user_id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    nick_name = serializers.CharField(required=True)
    role_id = serializers.CharField(required=True)
    role_name = serializers.CharField(required=True)


class WorkspaceMemberPageQuerySerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nick_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class WorkspaceMemberCreateItemSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.UUIDField(required=True), required=True
    )
    role_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True
    )


def get_workspace_role_options():
    return [
        {
            "id": RoleConstants.USER.name,
            "name": RoleConstants.USER.name,
            "type": RoleConstants.USER.name,
        }
    ]


class WorkspaceMemberSerializer(serializers.Serializer):
    SUPPORTED_ROLE_IDS = {RoleConstants.USER.name}

    @staticmethod
    def _validate_workspace(workspace_id: str):
        ensure_default_workspace()
        workspace = QuerySet(Workspace).filter(id=workspace_id).first()
        if workspace is None:
            raise AppApiException(500, "Workspace does not exist")
        if workspace_id == DEFAULT_WORKSPACE_ID:
            raise AppApiException(
                500, "Default workspace member management is not supported"
            )
        return workspace

    @staticmethod
    def get_role_list():
        return get_workspace_role_options()

    @staticmethod
    def page(
        workspace_id: str,
        query: dict[str, object],
        current_page: int,
        page_size: int,
    ):
        WorkspaceMemberSerializer._validate_workspace(workspace_id)
        query_data = {
            "username": query.get("username", [""])[0]
            if isinstance(query.get("username"), list)
            else query.get("username"),
            "nick_name": query.get("nick_name", [""])[0]
            if isinstance(query.get("nick_name"), list)
            else query.get("nick_name"),
        }
        WorkspaceMemberPageQuerySerializer(data=query_data).is_valid(
            raise_exception=True
        )
        query_set = (
            QuerySet(WorkspaceMember)
            .filter(workspace_id=workspace_id)
            .select_related("user")
        )
        if query_data.get("username"):
            query_set = query_set.filter(
                user__username__contains=query_data.get("username")
            )
        if query_data.get("nick_name"):
            query_set = query_set.filter(
                user__nick_name__contains=query_data.get("nick_name")
            )
        total = query_set.count()
        start = (current_page - 1) * page_size
        records = [
            {
                "user_relation_id": item.id,
                "user_id": item.user_id,
                "username": item.user.username,
                "nick_name": item.user.nick_name,
                "role_id": item.role_id,
                "role_name": item.role_id,
            }
            for item in query_set.order_by("create_time")[start : start + page_size]
        ]
        return Page(total, records, current_page, page_size)

    @staticmethod
    @transaction.atomic
    def add(workspace_id: str, data: list[dict[str, object]]):
        WorkspaceMemberSerializer._validate_workspace(workspace_id)
        serializer = WorkspaceMemberCreateItemSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        existing_user_ids = set(
            QuerySet(WorkspaceMember)
            .filter(workspace_id=workspace_id)
            .values_list("user_id", flat=True)
        )
        save_list = []
        for item in serializer.validated_data:
            role_ids = [
                role_id
                for role_id in item.get("role_ids", [])
                if role_id in WorkspaceMemberSerializer.SUPPORTED_ROLE_IDS
            ]
            role_id = role_ids[0] if role_ids else RoleConstants.USER.name
            for user_id in item.get("user_ids", []):
                if user_id in existing_user_ids:
                    continue
                user = (
                    QuerySet(User)
                    .filter(id=user_id, is_active=True)
                    .exclude(role=RoleConstants.ADMIN.name)
                    .first()
                )
                if user is None:
                    continue
                save_list.append(
                    WorkspaceMember(
                        workspace_id=workspace_id,
                        user_id=user_id,
                        role_id=role_id,
                    )
                )
                existing_user_ids.add(user_id)
        if save_list:
            QuerySet(WorkspaceMember).bulk_create(save_list)
        return True

    @staticmethod
    @transaction.atomic
    def remove(workspace_id: str, user_relation_id: str):
        WorkspaceMemberSerializer._validate_workspace(workspace_id)
        deleted_count, _ = (
            QuerySet(WorkspaceMember)
            .filter(
                workspace_id=workspace_id,
                id=user_relation_id,
            )
            .delete()
        )
        if deleted_count == 0:
            raise AppApiException(500, "Workspace member does not exist")
        return True
