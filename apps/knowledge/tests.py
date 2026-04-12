import uuid_utils.compat as uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from common.utils.common import password_encrypt
from knowledge.models import (
    State,
    Status,
    Knowledge,
    KnowledgeFolder,
    KnowledgeType,
    KnowledgeScope,
    Document,
    Paragraph,
    Problem,
    TaskType,
    Tag,
)
from users.models import User


class KnowledgeModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_knowledge_creation(self):
        user = self.create_user("kb-creator")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Test Knowledge",
            desc="Test Description",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        self.assertEqual(knowledge.name, "Test Knowledge")
        self.assertEqual(knowledge.type, KnowledgeType.BASE)
        self.assertEqual(knowledge.scope, KnowledgeScope.WORKSPACE)
        self.assertEqual(knowledge.workspace_id, "default")

    def test_knowledge_str_representation(self):
        user = self.create_user("kb-str-user")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Str Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

        self.assertEqual(str(knowledge), "Str Knowledge")


class StatusTests(SimpleTestCase):
    def test_default_status_marks_all_task_types_as_ignored(self):
        status = Status()

        self.assertEqual(status[TaskType.EMBEDDING], State.IGNORED)
        self.assertEqual(status[TaskType.GENERATE_PROBLEM], State.IGNORED)
        self.assertEqual(status[TaskType.SYNC], State.IGNORED)
        self.assertEqual(str(status), 'nnn')

    def test_status_of_round_trips_full_status_string(self):
        status = Status.of('210')

        self.assertEqual(status[TaskType.EMBEDDING], State.PENDING)
        self.assertEqual(status[TaskType.GENERATE_PROBLEM], State.STARTED)
        self.assertEqual(status[TaskType.SYNC], State.SUCCESS)
        self.assertEqual(str(status), '210')

    def test_short_status_string_defaults_missing_task_types_to_ignored(self):
        status = Status.of('2')

        self.assertEqual(status[TaskType.EMBEDDING], State.SUCCESS)
        self.assertEqual(status[TaskType.GENERATE_PROBLEM], State.IGNORED)
        self.assertEqual(status[TaskType.SYNC], State.IGNORED)
        self.assertEqual(str(status), 'nn2')

    def test_setitem_and_update_status_change_only_target_task(self):
        status = Status()

        status[TaskType.EMBEDDING] = State.STARTED
        status.update_status(TaskType.SYNC, State.REVOKED)

        self.assertEqual(status[TaskType.EMBEDDING], State.STARTED)
        self.assertEqual(status[TaskType.GENERATE_PROBLEM], State.IGNORED)
        self.assertEqual(status[TaskType.SYNC], State.REVOKED)
        self.assertEqual(str(status), '5n1')


class KnowledgeFolderModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_folder_creation(self):
        user = self.create_user("folder-user")
        folder = KnowledgeFolder.objects.create(
            id=uuid.uuid7().__str__(),
            name="Test Folder",
            user=user,
            workspace_id="default",
        )

        self.assertEqual(folder.name, "Test Folder")
        self.assertEqual(folder.user, user)

    def test_folder_with_children(self):
        user = self.create_user("folder-parent-user")
        parent = KnowledgeFolder.objects.create(
            id=uuid.uuid7().__str__(),
            name="Parent Folder",
            user=user,
            workspace_id="default",
        )
        child = KnowledgeFolder.objects.create(
            id=uuid.uuid7().__str__(),
            name="Child Folder",
            user=user,
            workspace_id="default",
            parent=parent,
        )

        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.count(), 1)


class DocumentModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_document_creation(self):
        user = self.create_user("doc-user")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Doc Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name="Test Document",
            char_length=1000,
            type=KnowledgeType.BASE,
        )

        self.assertEqual(document.name, "Test Document")
        self.assertEqual(document.char_length, 1000)
        self.assertEqual(document.knowledge, knowledge)


class ParagraphModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_paragraph_creation(self):
        user = self.create_user("para-user")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Para Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        document = Document.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            name="Para Document",
            char_length=100,
            type=KnowledgeType.BASE,
        )
        paragraph = Paragraph.objects.create(
            id=uuid.uuid7(),
            document=document,
            knowledge=knowledge,
            content="Test paragraph content",
            title="Test Title",
            position=1,
        )

        self.assertEqual(paragraph.content, "Test paragraph content")
        self.assertEqual(paragraph.title, "Test Title")
        self.assertEqual(paragraph.position, 1)


class ProblemModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_problem_creation(self):
        user = self.create_user("prob-user")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Prob Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        problem = Problem.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            content="What is this about?",
        )

        self.assertEqual(problem.content, "What is this about?")
        self.assertEqual(problem.hit_num, 0)


class TagModelTests(TestCase):
    def create_user(self, username: str):
        return User.objects.create(
            id=uuid.uuid7(),
            email=f"{username}@example.com",
            phone="",
            nick_name=f"{username}-nick",
            username=username,
            password=password_encrypt("Secret1!"),
            role="ADMIN",
            source="LOCAL",
            is_active=True,
        )

    def test_tag_creation(self):
        user = self.create_user("tag-user")
        knowledge = Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Tag Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )
        tag = Tag.objects.create(
            id=uuid.uuid7(),
            knowledge=knowledge,
            key="category",
            value="important",
        )

        self.assertEqual(tag.key, "category")
        self.assertEqual(tag.value, "important")
