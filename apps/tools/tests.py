import io
import json
import pickle
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

import uuid_utils.compat as uuid

from common.auth.handle.impl.user_token import get_auth
from common.constants.permission_constants import Group
from knowledge.models.knowledge_action import State
from system_manage.models import Workspace
from system_manage.models.resource_mapping import ResourceMapping
from tools.serializers.tool import encryption, to_dict, RestrictedUnpickler, ALLOWED_CLASSES
from tools.models import Tool, ToolFolder, ToolRecord, ToolScope, ToolType
from tools.views.system_resource_tool import SystemResourceToolView
from users.models import User


ADMIN_API_PREFIX = '/admin/api'


def create_authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user, token=get_auth(user))
    return client


class EncryptionTests(TestCase):
    def test_empty_string(self):
        self.assertEqual(encryption(""), "")

    def test_short_string(self):
        result = encryption("abc")
        self.assertIn("*", result)
        self.assertNotEqual(result, "abc")

    def test_long_string(self):
        result = encryption("1234567890abcdef")
        self.assertIn("*", result)
        self.assertTrue(result.startswith("1234"))
        self.assertTrue(result.endswith("cdef"))

    def test_non_string_returned_as_is(self):
        self.assertEqual(encryption(12345), 12345)
        self.assertIsNone(encryption(None))
        self.assertEqual(encryption(["a"]), ["a"])

    def test_password_like_string(self):
        result = encryption("SecretPassword123!")
        self.assertNotEqual(result, "SecretPassword123!")
        self.assertIn("*", result)


class ToDictTests(TestCase):
    def test_converts_pylint_message(self):
        message = SimpleNamespace(
            line=10,
            column=5,
            end_line=10,
            end_column=20,
            msg="Name 'foo' is undefined",
            category="error"
        )
        result = to_dict(message, "myfile.py")
        self.assertEqual(result["line"], 10)
        self.assertEqual(result["column"], 5)
        self.assertEqual(result["endLine"], 10)
        self.assertEqual(result["endColumn"], 20)
        self.assertEqual(result["message"], "Name 'foo' is undefined")
        self.assertEqual(result["type"], "error")

    def test_replaces_file_name_with_code(self):
        message = SimpleNamespace(
            line=1, column=0, end_line=1, end_column=10,
            msg="Error in /tmp/pylint/abc123.py on line 1",
            category="error"
        )
        result = to_dict(message, "/tmp/pylint/abc123.py")
        self.assertNotIn("/tmp/pylint/abc123.py", result["message"])
        self.assertIn("code", result["message"])

    def test_handles_none_message(self):
        message = SimpleNamespace(
            line=1, column=0, end_line=1, end_column=0,
            msg=None,
            category="convention"
        )
        result = to_dict(message, "test.py")
        self.assertEqual(result["message"], "")


class RestrictedUnpicklerTests(TestCase):
    def test_allowed_classes_can_unpickle(self):
        data = {"key": "value", "num": 42}
        pickled = pickle.dumps(data)
        result = RestrictedUnpickler(io.BytesIO(pickled)).load()
        self.assertEqual(result, data)

    def test_allowed_uuid_can_unpickle(self):
        import uuid_utils.compat as uuid
        test_uuid = uuid.uuid7()
        pickled = pickle.dumps(test_uuid)
        result = RestrictedUnpickler(io.BytesIO(pickled)).load()
        self.assertEqual(result, test_uuid)

    def test_allowed_classes_are_limited(self):
        self.assertIn(("builtins", "dict"), ALLOWED_CLASSES)
        self.assertIn(("uuid", "UUID"), ALLOWED_CLASSES)
        self.assertNotIn(("builtins", "eval"), ALLOWED_CLASSES)
        self.assertNotIn(("os", "system"), ALLOWED_CLASSES)


class SystemResourceToolPageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(
            id=uuid.uuid7(),
            email='system-tool-admin@example.com',
            phone='',
            nick_name='system-tool-admin',
            username='system-tool-admin',
            password='hashed',
            role='ADMIN',
            source='LOCAL',
            is_active=True,
        )
        self.creator = User.objects.create(
            id=uuid.uuid7(),
            email='system-tool-creator@example.com',
            phone='',
            nick_name='system-tool-creator',
            username='system-tool-creator',
            password='hashed',
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        self.other_creator = User.objects.create(
            id=uuid.uuid7(),
            email='system-tool-other@example.com',
            phone='',
            nick_name='system-tool-other',
            username='system-tool-other',
            password='hashed',
            role='USER',
            source='LOCAL',
            is_active=True,
        )
        Workspace.objects.create(id='workspace-a', name='Workspace A')
        Workspace.objects.create(id='workspace-b', name='Workspace B')
        self.folder_a = ToolFolder.objects.create(
            id='tool-folder-a',
            name='Tool Folder A',
            user=self.creator,
            workspace_id='workspace-a',
        )
        self.folder_b = ToolFolder.objects.create(
            id='tool-folder-b',
            name='Tool Folder B',
            user=self.other_creator,
            workspace_id='workspace-b',
        )
        self.factory = APIRequestFactory()
        self.client = create_authenticated_client(self.admin)

    def create_tool(self, **kwargs):
        defaults = {
            'id': uuid.uuid7(),
            'name': 'System Tool',
            'workspace_id': 'workspace-a',
            'desc': 'System tool description',
            'code': 'print(1)',
            'scope': ToolScope.WORKSPACE,
            'tool_type': ToolType.CUSTOM,
            'folder': self.folder_a,
            'user': self.creator,
            'icon': '',
            'is_active': True,
            'template_id': None,
            'init_field_list': [{'field': 'token', 'label': 'Token'}],
        }
        defaults.update(kwargs)
        return Tool.objects.create(**defaults)

    def create_tool_record(self, tool, **kwargs):
        defaults = {
            'workspace_id': tool.workspace_id,
            'tool': tool,
            'source_type': 'APPLICATION',
            'source_id': uuid.uuid7(),
            'meta': {'input': {'name': 'world'}, 'output': 'hello world'},
            'state': State.SUCCESS,
            'run_time': 0.42,
        }
        defaults.update(kwargs)
        return ToolRecord.objects.create(**defaults)

    def test_admin_can_page_system_resource_tools(self):
        tool = self.create_tool(name='Alpha Tool')
        self.create_tool(
            name='Beta Tool',
            workspace_id='workspace-b',
            folder=self.folder_b,
            user=self.other_creator,
            tool_type=ToolType.MCP,
            init_field_list=[],
        )
        ResourceMapping.objects.create(
            source_type=Group.APPLICATION.value,
            target_type=Group.TOOL.value,
            source_id='application-1',
            target_id=str(tool.id),
        )

        response = self.client.get(f'{ADMIN_API_PREFIX}/system/resource/tool/1/20')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertGreaterEqual(payload['data']['total'], 2)
        returned_ids = {item['id'] for item in payload['data']['records']}
        self.assertIn(str(tool.id), returned_ids)
        record = next(item for item in payload['data']['records'] if item['id'] == str(tool.id))
        self.assertEqual(record['name'], 'Alpha Tool')
        self.assertEqual(record['workspace_id'], 'workspace-a')
        self.assertEqual(record['workspace_name'], 'Workspace A')
        self.assertEqual(record['nick_name'], self.creator.nick_name)
        self.assertEqual(record['tool_type'], ToolType.CUSTOM)
        self.assertIsNone(record['template_id'])
        self.assertTrue(record['is_active'])
        self.assertEqual(record['init_field_list'], [{'field': 'token', 'label': 'Token'}])
        self.assertEqual(record['resource_count'], 1)
        self.assertIn('create_time', record)
        self.assertIn('update_time', record)

    def test_admin_can_filter_system_resource_tools(self):
        matched_tool = self.create_tool(
            name='Store MCP Tool',
            tool_type=ToolType.MCP,
            template_id='template-1',
        )
        self.create_tool(name='Custom Tool', template_id=None)
        self.create_tool(
            name='Other Workspace Store Tool',
            workspace_id='workspace-b',
            folder=self.folder_b,
            user=self.other_creator,
            tool_type=ToolType.MCP,
            template_id='template-2',
        )

        response = self.client.get(
            f'{ADMIN_API_PREFIX}/system/resource/tool/1/20',
            {
                'name': 'Store',
                'create_user': str(self.creator.id),
                'tool_type': ToolType.MCP,
                'source': 'TOOL_STORE',
                'workspace_ids': json.dumps(['workspace-a']),
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        self.assertEqual(payload['data']['records'][0]['id'], str(matched_tool.id))

    def test_custom_source_filter_returns_only_tools_without_template(self):
        custom_tool = self.create_tool(name='Custom Filter Tool', template_id=None)
        self.create_tool(name='Store Filter Tool', template_id='template-3')

        response = self.client.get(
            f'{ADMIN_API_PREFIX}/system/resource/tool/1/20',
            {'source': 'CUSTOM'},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        returned_ids = {item['id'] for item in payload['data']['records']}
        self.assertIn(str(custom_tool.id), returned_ids)
        self.assertNotIn('template-3', [item['template_id'] for item in payload['data']['records'] if item['template_id']])

    def test_admin_can_get_update_and_delete_system_resource_tool(self):
        tool = self.create_tool(name='Operate Tool')

        get_response = self.client.get(f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}')

        self.assertEqual(get_response.status_code, 200)
        get_payload = json.loads(get_response.content)
        self.assertEqual(get_payload['data']['id'], str(tool.id))
        self.assertEqual(get_payload['data']['name'], 'Operate Tool')
        self.assertEqual(get_payload['data']['workspace_id'], 'workspace-a')

        put_response = self.client.put(
            f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}',
            {'name': 'Updated Tool', 'desc': 'updated description'},
            format='json',
        )

        self.assertEqual(put_response.status_code, 200)
        put_payload = json.loads(put_response.content)
        self.assertEqual(put_payload['data']['name'], 'Updated Tool')
        tool.refresh_from_db()
        self.assertEqual(tool.name, 'Updated Tool')
        self.assertEqual(tool.desc, 'updated description')

        delete_response = self.client.delete(f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}')

        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Tool.objects.filter(id=tool.id).exists())

    def test_admin_can_edit_system_resource_tool_icon(self):
        tool = self.create_tool(name='Icon Tool')
        image_buffer = io.BytesIO()
        Image.new('RGB', (1, 1), color='white').save(image_buffer, format='PNG')
        image = SimpleUploadedFile('icon.png', image_buffer.getvalue(), content_type='image/png')

        request = self.factory.put(
            f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}/edit_icon',
            {'file': image},
            format='multipart',
        )
        force_authenticate(request, user=self.admin, token=get_auth(self.admin))
        response = SystemResourceToolView.EditIcon.as_view()(request, tool_id=str(tool.id))

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['data'].startswith('./oss/file/'))
        tool.refresh_from_db()
        self.assertEqual(tool.icon, payload['data'])

    def test_admin_can_export_system_resource_tool(self):
        tool = self.create_tool(name='Export Tool')

        response = self.client.get(f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}/export')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="Export Tool.tool"')
        self.assertGreater(len(response.content), 0)

    def test_admin_can_debug_system_resource_tool(self):
        response = self.client.post(
            f'{ADMIN_API_PREFIX}/system/resource/tool/debug',
            {
                'code': 'def main(name):\n    return f"hello {name}"',
                'input_field_list': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'source': 'custom',
                        'is_required': True,
                    }
                ],
                'init_field_list': [],
                'init_params': {},
                'debug_field_list': [
                    {
                        'name': 'name',
                        'value': 'world',
                    }
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data'], 'hello world')

    def test_admin_can_pylint_system_resource_tool_code(self):
        response = self.client.post(
            f'{ADMIN_API_PREFIX}/system/resource/tool/pylint',
            {'code': 'print(missing_name)\n'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertIsInstance(payload['data'], list)
        self.assertTrue(any(item['type'] == 'error' for item in payload['data']))

    def test_admin_can_upload_system_resource_skill_file(self):
        skill_file = SimpleUploadedFile('skill.zip', b'PK\x03\x04skill-bytes', content_type='application/zip')

        response = self.client.put(
            f'{ADMIN_API_PREFIX}/system/resource/tool/upload_skill_file',
            {'file': skill_file},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertTrue(payload['data'])

    def test_admin_can_test_system_resource_tool_connection(self):
        with patch('tools.serializers.tool.validate_mcp_config') as validate_mcp_config:
            response = self.client.post(
                f'{ADMIN_API_PREFIX}/system/resource/tool/test_connection',
                {
                    'code': json.dumps(
                        {
                            'demo': {
                                'transport': 'streamable_http',
                                'url': 'http://example.com/mcp',
                            }
                        }
                    )
                },
                format='json',
            )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertTrue(payload['data'])
        validate_mcp_config.assert_called_once()

    def test_admin_can_page_system_resource_tool_records(self):
        tool = self.create_tool(name='Record Tool')
        matched_record = self.create_tool_record(tool, state=State.SUCCESS, meta={'input': {'query': 'one'}, 'output': 'ok'})
        self.create_tool_record(tool, state=State.FAILURE, meta={'input': {'query': 'two'}, 'output': 'bad'})

        response = self.client.get(
            f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}/tool_record/1/20',
            {'state': State.SUCCESS},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['total'], 1)
        self.assertEqual(len(payload['data']['records']), 1)
        record = payload['data']['records'][0]
        self.assertEqual(record['id'], str(matched_record.id))
        self.assertEqual(record['tool_id'], str(tool.id))
        self.assertEqual(record['workspace_id'], tool.workspace_id)
        self.assertEqual(record['state'], State.SUCCESS)
        self.assertEqual(record['tool_name'], tool.name)
        self.assertEqual(record['tool_icon'], tool.icon)

    def test_admin_can_get_system_resource_tool_record_detail(self):
        tool = self.create_tool(name='Record Detail Tool')
        record = self.create_tool_record(tool, meta={'input': {'query': 'detail'}, 'output': 'done'}, run_time=1.25)

        response = self.client.get(f'{ADMIN_API_PREFIX}/system/resource/tool/{tool.id}/tool_record/{record.id}')

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 200)
        self.assertEqual(payload['data']['id'], str(record.id))
        self.assertEqual(payload['data']['tool_id'], str(tool.id))
        self.assertEqual(payload['data']['workspace_id'], tool.workspace_id)
        self.assertEqual(payload['data']['meta'], {'input': {'query': 'detail'}, 'output': 'done'})
        self.assertEqual(payload['data']['state'], State.SUCCESS)
        self.assertEqual(payload['data']['run_time'], 1.25)
