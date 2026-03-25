import uuid_utils.compat as uuid
from django.db import models

from common.constants.permission_constants import Group
from common.mixins.app_model_mixin import AppModelMixin


class SharedResourceType(models.TextChoices):
    KNOWLEDGE = Group.KNOWLEDGE.value, "知识库"
    TOOL = Group.TOOL.value, "工具"


class SharedAuthenticationType(models.TextChoices):
    WHITE_LIST = "WHITE_LIST", "白名单"
    BLACK_LIST = "BLACK_LIST", "黑名单"


class SharedResourceAuthorization(AppModelMixin):
    id = models.UUIDField(
        primary_key=True,
        max_length=128,
        default=uuid.uuid7,
        editable=False,
        verbose_name="主键id",
    )
    resource_type = models.CharField(
        max_length=64,
        verbose_name="资源类型",
        choices=SharedResourceType.choices,
        db_index=True,
    )
    resource_id = models.CharField(max_length=128, verbose_name="资源id", db_index=True)
    authentication_type = models.CharField(
        max_length=32,
        verbose_name="授权类型",
        choices=SharedAuthenticationType.choices,
        default=SharedAuthenticationType.WHITE_LIST,
    )
    workspace_id_list = models.JSONField(verbose_name="工作空间id列表", default=list)

    class Meta:
        db_table = "shared_resource_authorization"
        unique_together = ("resource_type", "resource_id")
