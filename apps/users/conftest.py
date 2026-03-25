import uuid_utils.compat as uuid
import pytest
from django.core.cache import cache

from common.utils.common import password_encrypt
from users.models import User
from system_manage.models import Workspace


@pytest.fixture
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def create_user():
    def _create_user(
        role: str = "USER",
        username: str = "testuser",
        email: str = "test@example.com",
        source: str = "LOCAL",
        is_active: bool = True,
    ):
        return User.objects.create(
            id=uuid.uuid7(),
            email=email,
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role=role,
            source=source,
            is_active=is_active,
        )

    return _create_user


@pytest.fixture
def admin_user(create_user):
    return create_user(role="ADMIN", username="admin")


@pytest.fixture
def regular_user(create_user):
    return create_user(role="USER", username="user")


@pytest.fixture
def default_workspace():
    return Workspace.objects.get_or_create(
        id="default", defaults={"name": "Default Workspace"}
    )[0]
