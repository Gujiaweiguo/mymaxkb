import uuid_utils.compat as uuid
import pytest
from django.core.cache import cache

from common.utils.common import password_encrypt
from users.models import User
from knowledge.models import (
    Knowledge,
    KnowledgeFolder,
    KnowledgeType,
    KnowledgeScope,
    Document,
    Paragraph,
    Problem,
    Tag,
)


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
    ):
        return User.objects.create(
            id=uuid.uuid7(),
            email=email,
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role=role,
            source="LOCAL",
            is_active=True,
        )

    return _create_user


@pytest.fixture
def admin_user(create_user):
    return create_user(role="ADMIN", username="admin")


@pytest.fixture
def create_knowledge():
    def _create_knowledge(
        user,
        workspace_id: str = "default",
        name: str = "Test Knowledge",
        knowledge_type: KnowledgeType = KnowledgeType.BASE,
    ):
        return Knowledge.objects.create(
            id=uuid.uuid7(),
            name=name,
            desc=f"{name} Description",
            user=user,
            workspace_id=workspace_id,
            type=knowledge_type,
            scope=KnowledgeScope.WORKSPACE,
        )

    return _create_knowledge


@pytest.fixture
def create_folder():
    def _create_folder(
        user,
        workspace_id: str = "default",
        name: str = "Test Folder",
        parent=None,
    ):
        return KnowledgeFolder.objects.create(
            id=uuid.uuid7().__str__(),
            name=name,
            user=user,
            workspace_id=workspace_id,
            parent=parent,
        )

    return _create_folder
