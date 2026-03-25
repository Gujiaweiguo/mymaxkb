import hashlib
from datetime import timedelta

import uuid_utils.compat as uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from common.mixins.app_model_mixin import AppModelMixin


def default_system_secret_key():
    return "system-" + hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()


def default_system_expire_time():
    return timezone.now() + timedelta(days=365 * 100)


class SystemApiKey(AppModelMixin):
    id = models.UUIDField(
        primary_key=True,
        max_length=128,
        default=uuid.uuid7,
        editable=False,
        verbose_name="主键id",
    )
    secret_key = models.CharField(
        max_length=1024,
        verbose_name="秘钥",
        unique=True,
        default=default_system_secret_key,
    )
    is_active = models.BooleanField(default=True, verbose_name="是否开启")
    allow_cross_domain = models.BooleanField(default=False, verbose_name="是否允许跨域")
    cross_domain_list = ArrayField(
        verbose_name="跨域列表",
        base_field=models.CharField(max_length=128, blank=True),
        default=list,
    )
    expire_time = models.DateTimeField(
        verbose_name="过期时间", default=default_system_expire_time
    )
    is_permanent = models.BooleanField(default=True, verbose_name="是否永久")

    class Meta:
        db_table = "system_api_key"
