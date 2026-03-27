# coding=utf-8
"""
@project: MaxKB
@Author：OpenCode
@file： workspace.py
@date：2026/3/23
@desc:
"""

import uuid_utils.compat as uuid
from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Workspace(AppModelMixin):
    id = models.CharField(
        primary_key=True,
        max_length=64,
        editable=False,
        default=uuid.uuid7,
        verbose_name="主键id",
    )
    name = models.CharField(
        max_length=64, unique=True, db_index=True, verbose_name="工作空间名称"
    )

    class Meta:
        db_table = "workspace"

    def __str__(self) -> str:
        return str(self.name)


class WorkspaceMember(AppModelMixin):
    id = models.UUIDField(
        primary_key=True,
        max_length=128,
        default=uuid.uuid7,
        editable=False,
        verbose_name="主键id",
    )
    workspace_id = models.CharField(
        max_length=64, db_index=True, verbose_name="工作空间id"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="工作空间成员"
    )
    role_id = models.CharField(max_length=64, default="USER", verbose_name="角色id")

    class Meta:
        db_table = "workspace_member"
        unique_together = ("workspace_id", "user")
