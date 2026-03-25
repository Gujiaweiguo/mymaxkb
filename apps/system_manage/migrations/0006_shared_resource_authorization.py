from django.db import migrations, models
import uuid_utils.compat


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0005_resourcemapping"),
        ("system_manage", "0005_workspace_member"),
    ]

    operations = [
        migrations.CreateModel(
            name="SharedResourceAuthorization",
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
                    "resource_type",
                    models.CharField(
                        choices=[("KNOWLEDGE", "知识库"), ("TOOL", "工具")],
                        db_index=True,
                        max_length=64,
                        verbose_name="资源类型",
                    ),
                ),
                (
                    "resource_id",
                    models.CharField(
                        db_index=True, max_length=128, verbose_name="资源id"
                    ),
                ),
                (
                    "authentication_type",
                    models.CharField(
                        choices=[("WHITE_LIST", "白名单"), ("BLACK_LIST", "黑名单")],
                        default="WHITE_LIST",
                        max_length=32,
                        verbose_name="授权类型",
                    ),
                ),
                (
                    "workspace_id_list",
                    models.JSONField(default=list, verbose_name="工作空间id列表"),
                ),
            ],
            options={
                "db_table": "shared_resource_authorization",
                "ordering": ["create_time"],
                "unique_together": {("resource_type", "resource_id")},
            },
        ),
    ]
