import io
import json
import pickle
from types import SimpleNamespace

from django.test import TestCase
from common.exception.app_exception import AppApiException
from tools.serializers.tool import encryption, to_dict, RestrictedUnpickler, ALLOWED_CLASSES


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


