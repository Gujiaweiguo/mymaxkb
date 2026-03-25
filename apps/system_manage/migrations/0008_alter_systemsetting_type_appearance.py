from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_manage", "0007_system_api_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="systemsetting",
            name="type",
            field=models.IntegerField(
                choices=[
                    (0, "邮箱"),
                    (1, "私钥秘钥"),
                    (2, "日志清理时间"),
                    (3, "登录认证"),
                    (4, "平台集成"),
                    (5, "对话用户平台集成"),
                    (6, "外观设置"),
                ],
                default=0,
                primary_key=True,
                serialize=False,
                verbose_name="设置类型",
            ),
        ),
    ]
