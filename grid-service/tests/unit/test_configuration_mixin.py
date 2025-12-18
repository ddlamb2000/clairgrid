import unittest
from unittest.mock import patch, mock_open
from libs.utils.configuration_mixin import ConfigurationMixin

class TestConfigurationMixin(unittest.TestCase):

    def setUp(self):
        self.mixin = ConfigurationMixin()

    def test_read_password_file_success(self):
        """Test reading a password from a valid file."""
        with patch("builtins.open", mock_open(read_data="secret_password")):
            password = self.mixin._read_password_file("/path/to/secret", "MY_VAR")
            self.assertEqual(password, "secret_password")

    def test_read_password_file_strip_whitespace(self):
        """Test that whitespace is stripped from the password."""
        with patch("builtins.open", mock_open(read_data="  secret_password  \n")):
            password = self.mixin._read_password_file("/path/to/secret", "MY_VAR")
            self.assertEqual(password, "secret_password")

    def test_read_password_file_missing_path(self):
        """Test that ValueError is raised if file path is None/empty."""
        with self.assertRaises(ValueError) as cm:
            self.mixin._read_password_file(None, "MY_VAR")
        self.assertIn("MY_VAR environment variable is not set", str(cm.exception))

    def test_read_password_file_not_found(self):
        """Test that ValueError is raised if file does not exist."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(ValueError) as cm:
                self.mixin._read_password_file("/non/existent/path", "MY_VAR")
            self.assertIn("Password file not found", str(cm.exception))

