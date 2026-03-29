from django.test import TestCase

from oss.serializers.file import is_private_ip, validate_url, mime_types, audio_types


class IsPrivateIpTests(TestCase):
    def test_private_10_x(self):
        self.assertTrue(is_private_ip("10.0.0.1"))
        self.assertTrue(is_private_ip("10.255.255.255"))

    def test_private_172_16_x(self):
        self.assertTrue(is_private_ip("172.16.0.1"))
        self.assertTrue(is_private_ip("172.31.255.255"))

    def test_private_192_168_x(self):
        self.assertTrue(is_private_ip("192.168.0.1"))
        self.assertTrue(is_private_ip("192.168.255.255"))

    def test_loopback(self):
        self.assertTrue(is_private_ip("127.0.0.1"))
        self.assertTrue(is_private_ip("127.255.255.255"))

    def test_reserved(self):
        self.assertTrue(is_private_ip("0.0.0.0"))

    def test_link_local(self):
        self.assertTrue(is_private_ip("169.254.1.1"))

    def test_multicast(self):
        self.assertTrue(is_private_ip("224.0.0.1"))

    def test_public_ip(self):
        self.assertFalse(is_private_ip("8.8.8.8"))
        self.assertFalse(is_private_ip("1.1.1.1"))

    def test_public_hostname(self):
        self.assertFalse(is_private_ip("google.com"))

    def test_invalid_hostname_returns_true(self):
        self.assertTrue(is_private_ip("this-host-does-not-exist-12345.invalid"))


class ValidateUrlTests(TestCase):
    def test_valid_http_url(self):
        parsed = validate_url("http://example.com/path")
        self.assertEqual(parsed.scheme, "http")
        self.assertEqual(parsed.hostname, "example.com")

    def test_valid_https_url(self):
        parsed = validate_url("https://example.com/path?q=1")
        self.assertEqual(parsed.scheme, "https")

    def test_empty_url_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("")
        self.assertIn("required", str(ctx.exception))

    def test_none_url_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url(None)
        self.assertIn("required", str(ctx.exception))

    def test_ftp_scheme_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("ftp://example.com/file")
        self.assertIn("http and https", str(ctx.exception))

    def test_file_scheme_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("file:///etc/passwd")
        self.assertIn("http and https", str(ctx.exception))

    def test_no_host_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("http://")
        self.assertIn("Invalid URL", str(ctx.exception))

    def test_private_ip_blocked(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("http://10.0.0.1/admin")
        self.assertIn("internal IP", str(ctx.exception))

    def test_loopback_blocked(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("http://127.0.0.1:8080/api")
        self.assertIn("internal IP", str(ctx.exception))

    def test_localhost_blocked(self):
        with self.assertRaises(ValueError) as ctx:
            validate_url("http://localhost/admin")
        self.assertIn("internal IP", str(ctx.exception))


class AudioTypesTests(TestCase):
    def test_common_audio_types(self):
        self.assertIn("mp3", audio_types)
        self.assertIn("wav", audio_types)
        self.assertIn("ogg", audio_types)
        self.assertIn("flac", audio_types)
        self.assertIn("aac", audio_types)
        self.assertIn("opus", audio_types)
        self.assertIn("m4a", audio_types)

    def test_non_audio_types_not_in_audio(self):
        self.assertNotIn("pdf", audio_types)
        self.assertNotIn("mp4", audio_types)
        self.assertNotIn("txt", audio_types)


class MimeTypesTests(TestCase):
    def test_common_types(self):
        self.assertEqual(mime_types.get("pdf"), "application/pdf")
        self.assertEqual(mime_types.get("json"), "application/json")
        self.assertEqual(mime_types.get("html"), "text/html")
        self.assertEqual(mime_types.get("txt"), "text/plain")
        self.assertEqual(mime_types.get("png"), "image/png")
        self.assertEqual(mime_types.get("jpg"), "image/jpeg")

    def test_office_types(self):
        self.assertEqual(mime_types.get("docx"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertEqual(mime_types.get("xlsx"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def test_unknown_extension_returns_none(self):
        self.assertIsNone(mime_types.get("xyz"))
        self.assertIsNone(mime_types.get(""))
