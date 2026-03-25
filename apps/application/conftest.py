import uuid_utils.compat as uuid
import pytest
from django.core.cache import cache

from common.utils.common import password_encrypt
from users.models import User
from application.models import Application, ApplicationFolder, ApplicationTypeChoices
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
def create_application_folder():
    def _create_folder(user, workspace_id: str = "default", name: str = "Test Folder"):
        return ApplicationFolder.objects.create(
            id=uuid.uuid7().__str__(),
            name=name,
            user=user,
            workspace_id=workspace_id,
        )

    return _create_folder


@pytest.fixture
def create_application():
    def _create_app(
        user,
        folder,
        workspace_id: str = "default",
        name: str = "Test App",
        app_type: ApplicationTypeChoices = ApplicationTypeChoices.SIMPLE,
    ):
        return Application.objects.create(
            id=uuid.uuid7(),
            name=name,
            desc=f"{name} Description",
            user=user,
            folder=folder,
            workspace_id=workspace_id,
            type=app_type,
            icon="./favicon.ico",
        )

    return _create_app
