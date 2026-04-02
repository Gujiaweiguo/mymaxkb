# coding=utf-8
"""
Unit tests for the Config class in maxkb.conf.

Covers placeholder-secret detection, required-secret validation,
required-value checks, and non-sensitive default accessors.
"""

from django.test import TestCase

from maxkb.conf import Config


class IsPlaceholderSecretTests(TestCase):
    """Tests for Config._is_placeholder_secret()."""

    # --- known placeholders (must return True) ---

    def test_change_me_prefix(self):
        self.assertTrue(Config._is_placeholder_secret("change_me_bootstrap_admin_password"))
        self.assertTrue(Config._is_placeholder_secret("change_me_anything"))

    def test_exact_match_maxkb_password(self):
        self.assertTrue(Config._is_placeholder_secret("MaxKB@123.."))

    def test_exact_match_postgres_password(self):
        self.assertTrue(Config._is_placeholder_secret("Password123@postgres"))

    def test_exact_match_redis_password(self):
        self.assertTrue(Config._is_placeholder_secret("Password123@redis"))

    def test_exact_match_mac_kb_password(self):
        self.assertTrue(Config._is_placeholder_secret("mac_kb_password"))

    # --- valid secrets (must return False) ---

    def test_valid_secret_mixed(self):
        self.assertFalse(Config._is_placeholder_secret("MySecurePassword123!"))

    def test_valid_secret_long(self):
        self.assertFalse(Config._is_placeholder_secret("a-real-secret-key-that-is-long"))

    # --- edge cases ---

    def test_none_returns_false(self):
        self.assertFalse(Config._is_placeholder_secret(None))

    def test_int_returns_false(self):
        self.assertFalse(Config._is_placeholder_secret(123))

    def test_empty_string_returns_false(self):
        self.assertFalse(Config._is_placeholder_secret(""))

    def test_whitespace_padded_placeholder_returns_true(self):
        self.assertTrue(Config._is_placeholder_secret("  MaxKB@123..  "))


class GetRequiredSecretTests(TestCase):
    """Tests for Config.get_required_secret()."""

    def test_change_me_prefix_raises(self):
        cfg = Config({"SECRET_KEY": "change_me_please"})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required_secret("SECRET_KEY")
        self.assertIn("Unsafe placeholder", str(ctx.exception))

    def test_exact_placeholder_raises(self):
        cfg = Config({"SECRET_KEY": "MaxKB@123.."})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required_secret("SECRET_KEY")
        self.assertIn("Unsafe placeholder", str(ctx.exception))

    def test_valid_secret_returns_value(self):
        cfg = Config({"SECRET_KEY": "a-valid-secret-key"})
        self.assertEqual(cfg.get_required_secret("SECRET_KEY"), "a-valid-secret-key")

    def test_missing_key_raises(self):
        cfg = Config({})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required_secret("SECRET_KEY")
        self.assertIn("Missing required configuration", str(ctx.exception))

    def test_empty_string_raises(self):
        cfg = Config({"SECRET_KEY": ""})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required_secret("SECRET_KEY")
        self.assertIn("Missing required configuration", str(ctx.exception))


class GetRequiredTests(TestCase):
    """Tests for Config.get_required()."""

    def test_missing_key_raises(self):
        cfg = Config({})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required("DB_NAME")
        self.assertIn("Missing required configuration", str(ctx.exception))

    def test_none_value_raises(self):
        cfg = Config({"DB_NAME": None})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required("DB_NAME")
        self.assertIn("Missing required configuration", str(ctx.exception))

    def test_empty_string_raises(self):
        cfg = Config({"DB_NAME": ""})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required("DB_NAME")
        self.assertIn("Missing required configuration", str(ctx.exception))

    def test_valid_string_returns_value(self):
        cfg = Config({"DB_NAME": "mydb"})
        self.assertEqual(cfg.get_required("DB_NAME"), "mydb")

    def test_display_name_in_error(self):
        cfg = Config({})
        with self.assertRaises(ImportError) as ctx:
            cfg.get_required("DB_NAME", display_name="DATABASE_NAME")
        self.assertIn("DATABASE_NAME", str(ctx.exception))


class DefaultAccessorTests(TestCase):
    """Tests for non-sensitive defaults: get_str, get_int, get_bool."""

    def test_get_str_missing_key_returns_default(self):
        cfg = Config({})
        self.assertEqual(cfg.get_str("MISSING_KEY", "fallback"), "fallback")

    def test_get_str_present_value(self):
        cfg = Config({"HOST": "db.example.com"})
        self.assertEqual(cfg.get_str("HOST", "localhost"), "db.example.com")

    def test_get_int_missing_key_returns_default(self):
        cfg = Config({})
        self.assertEqual(cfg.get_int("MISSING_PORT", 5432), 5432)

    def test_get_int_present_value(self):
        cfg = Config({"PORT": "3306"})
        self.assertEqual(cfg.get_int("PORT", 5432), 3306)

    def test_get_bool_missing_key_returns_default(self):
        cfg = Config({})
        self.assertTrue(cfg.get_bool("MISSING_FLAG", True))
        self.assertFalse(cfg.get_bool("MISSING_FLAG", False))

    def test_get_bool_string_true(self):
        cfg = Config({"FLAG": "true"})
        self.assertTrue(cfg.get_bool("FLAG", False))

    def test_get_bool_string_false(self):
        cfg = Config({"FLAG": "no"})
        self.assertFalse(cfg.get_bool("FLAG", True))

    def test_get_bool_bool_value(self):
        cfg = Config({"FLAG": False})
        self.assertFalse(cfg.get_bool("FLAG", True))
