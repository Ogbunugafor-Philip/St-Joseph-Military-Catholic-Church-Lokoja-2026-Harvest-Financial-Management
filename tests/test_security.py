import os
import unittest
from unittest.mock import patch

from security import ConfigurationError, hash_password, integer_setting, required_password_hash, verify_password


class PasswordSecurityTests(unittest.TestCase):
    def test_hash_round_trip_and_wrong_password(self):
        encoded = hash_password("synthetic-test-password", iterations=100_000)
        self.assertTrue(verify_password("synthetic-test-password", encoded))
        self.assertFalse(verify_password("wrong", encoded))
        self.assertNotIn("synthetic-test-password", encoded)

    def test_missing_and_plaintext_configuration_fail_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                required_password_hash("TEST_PASSWORD_HASH")
        with patch.dict(os.environ, {"TEST_PASSWORD_HASH": "plaintext"}, clear=True):
            with self.assertRaises(ConfigurationError):
                required_password_hash("TEST_PASSWORD_HASH")

    def test_integer_setting_bounds(self):
        with patch.dict(os.environ, {"TEST_LIMIT": "2"}, clear=True):
            with self.assertRaises(ConfigurationError):
                integer_setting("TEST_LIMIT", 5, minimum=3, maximum=20)


if __name__ == "__main__":
    unittest.main()
