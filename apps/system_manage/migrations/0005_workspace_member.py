import django.db.models.deletion
import uuid_utils.compat
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("system_manage", "0004_workspace"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceMember",
            fields=[
                (
                    "create_time",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="创建时间"
                    ),
                ),
                (
                    "update_time",
                    models.DateTimeField(
                        auto_now=True, db_index=True, verbose_name="修改时间"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid_utils.compat.uuid7,
                        editable=False,
                        max_length=128,
                        primary_key=True,
                        serialize=False,
                        verbose_name="主键id",
                    ),
                ),
                (
                    "workspace_id",
                    models.CharField(
                        db_index=True, max_length=64, verbose_name="工作空间id"
                    ),
                ),
                (
                    "role_id",
                    models.CharField(
                        default="USER", max_length=64, verbose_name="角色id"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.user",
                        verbose_name="工作空间成员",
                    ),
                ),
            ],
            options={
                "db_table": "workspace_member",
                "ordering": ["create_time"],
                "unique_together": {("workspace_id", "user")},
            },
        ),
    ]
