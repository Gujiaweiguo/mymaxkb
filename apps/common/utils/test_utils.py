import uuid_utils.compat as uuid
from django.test import TestCase

from common.utils.common import (
    password_encrypt,
    password_verify,
    get_sha256_hash,
    get_random_string,
)
from common.utils.rsa_util import (
    generate_rsa_key_pair,
    rsa_encrypt,
    rsa_decrypt,
)


class PasswordUtilsTests(TestCase):
    def test_password_encrypt_and_verify(self):
        password = "SecretPassword123!"
        encrypted = password_encrypt(password)

        self.assertNotEqual(encrypted, password)
        self.assertTrue(password_verify(password, encrypted))
        self.assertFalse(password_verify("WrongPassword", encrypted))

    def test_password_encrypt_different_hashes(self):
        password = "SamePassword"
        hash1 = password_encrypt(password)
        hash2 = password_encrypt(password)

        self.assertNotEqual(hash1, hash2)


class HashUtilsTests(TestCase):
    def test_get_sha256_hash(self):
        data = b"test data"
        hash1 = get_sha256_hash(data)
        hash2 = get_sha256_hash(data)

        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_get_sha256_hash_different_data(self):
        data1 = b"data one"
        data2 = b"data two"
        hash1 = get_sha256_hash(data1)
        hash2 = get_sha256_hash(data2)

        self.assertNotEqual(hash1, hash2)


class RandomStringTests(TestCase):
    def test_get_random_string_length(self):
        random_str = get_random_string(10)

        self.assertEqual(len(random_str), 10)

    def test_get_random_string_uniqueness(self):
        strings = [get_random_string(20) for _ in range(10)]

        self.assertEqual(len(strings), len(set(strings)))


class RSAUtilTests(TestCase):
    def test_generate_rsa_key_pair(self):
        private_key, public_key = generate_rsa_key_pair()

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIn("BEGIN PRIVATE KEY", private_key)
        self.assertIn("BEGIN PUBLIC KEY", public_key)

    def test_rsa_encrypt_decrypt(self):
        private_key, public_key = generate_rsa_key_pair()
        plaintext = "Hello, World!"

        encrypted = rsa_encrypt(plaintext, public_key)
        decrypted = rsa_decrypt(encrypted, private_key)

        self.assertEqual(plaintext, decrypted)

    def test_rsa_encrypt_different_ciphertexts(self):
        private_key, public_key = generate_rsa_key_pair()
        plaintext = "Same message"

        encrypted1 = rsa_encrypt(plaintext, public_key)
        encrypted2 = rsa_encrypt(plaintext, public_key)

        self.assertNotEqual(encrypted1, encrypted2)
