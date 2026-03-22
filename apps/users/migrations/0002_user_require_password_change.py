import hashlib

from django.db import migrations, models


LEGACY_DEFAULT_PASSWORD_HASH = "d880e722c47a34d8e9fce789fc62389d"


def _password_hash(raw_password: str | None) -> str | None:
    if not raw_password:
        return None
    return hashlib.md5(raw_password.encode()).hexdigest()


def mark_bootstrap_password_change(apps, schema_editor):
    from maxkb.const import CONFIG

    UserModel = apps.get_model("users", "User")
    bootstrap_password = CONFIG.get("DEFAULT_PASSWORD")
    bootstrap_password_hash = None
    if isinstance(bootstrap_password, str) and not bootstrap_password.startswith(
        "change_me_"
    ):
        bootstrap_password_hash = _password_hash(bootstrap_password)
    candidate_hashes = {LEGACY_DEFAULT_PASSWORD_HASH}
    if bootstrap_password_hash:
        candidate_hashes.add(bootstrap_password_hash)

    UserModel.objects.filter(password__in=candidate_hashes).update(
        require_password_change=True
    )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="require_password_change",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(mark_bootstrap_password_change, migrations.RunPython.noop),
    ]
