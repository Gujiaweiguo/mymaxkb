import uuid_utils.compat as uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from common.utils.common import password_encrypt
from knowledge.models import (
    State,
    Knowledge,
    KnowledgeFolder,
    KnowledgeType,
    KnowledgeScope,
    Document,
    Paragraph,
    Problem,
    Tag,
)
from knowledge.task.handler import get_sync_web_document_handler, save_problem
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


class KnowledgeTaskHandlerTests(TestCase):
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

    def create_knowledge(self, username: str = 'handler-user'):
        user = self.create_user(username)
        return Knowledge.objects.create(
            id=uuid.uuid7(),
            name="Handler Knowledge",
            desc="Desc",
            user=user,
            workspace_id="default",
            type=KnowledgeType.BASE,
            scope=KnowledgeScope.WORKSPACE,
        )

    def test_save_problem_extracts_question_content_and_workspace_scope(self):
        knowledge = self.create_knowledge()
        document_id = uuid.uuid7()
        paragraph_id = uuid.uuid7()

        with patch('knowledge.serializers.paragraph.ParagraphSerializers') as paragraph_serializers:
            save_problem(
                knowledge.id,
                document_id,
                paragraph_id,
                '1. <question>What is MaxKB?</question>',
            )

        paragraph_serializers.Problem.assert_called_once_with(
            data={
                'workspace_id': 'default',
                'knowledge_id': knowledge.id,
                'document_id': document_id,
                'paragraph_id': paragraph_id,
            }
        )
        paragraph_serializers.Problem.return_value.save.assert_called_once_with(
            instance={'content': 'What is MaxKB?'},
            with_valid=True,
        )

    def test_save_problem_ignores_missing_question_markup(self):
        knowledge = self.create_knowledge('no-question-user')

        with patch('knowledge.serializers.paragraph.ParagraphSerializers') as paragraph_serializers:
            save_problem(knowledge.id, uuid.uuid7(), uuid.uuid7(), '1. ')

        paragraph_serializers.Problem.assert_not_called()

    def test_sync_web_document_handler_marks_failed_document_when_fetch_fails(self):
        knowledge = self.create_knowledge('sync-user')
        source_url = 'https://example.com/reference'
        handler = get_sync_web_document_handler(knowledge.id)

        handler(source_url, '.content', SimpleNamespace(status=500, content=''))

        failure_document = Document.objects.get(knowledge=knowledge, meta__source_url=source_url)
        self.assertEqual(failure_document.name, source_url[:128])
        self.assertEqual(failure_document.status, str(State.FAILURE))
        self.assertEqual(failure_document.type, KnowledgeType.WEB)
        self.assertEqual(failure_document.meta['selector'], '.content')
        self.assertTrue(failure_document.meta['allow_download'])
