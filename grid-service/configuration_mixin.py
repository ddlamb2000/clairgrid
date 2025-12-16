'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Configuration Mixin for the clairgrid Grid Service.
'''

import os

class ConfigurationMixin:
    """
    Mixin class providing helper methods for loading configuration.
    """

    def _read_password_file(self, file_path, password_env_var_name=None):
        """
        Reads a password from an environment variable or a file.

        Args:
            file_path (str): The path to the password file.
            password_env_var_name (str): The name of the environment variable containing the password.

        Returns:
            str: The password.

        Raises:
            ValueError: If the file path is not set or the file is not found.
        """
        if password_env_var_name and os.getenv(password_env_var_name):
            return os.getenv(password_env_var_name)

        if not file_path:
            raise ValueError(f"Password file path is not set")
        try:
            with open(file_path) as f:
                return f.read().strip()
        except FileNotFoundError:
             raise ValueError(f"Password file not found at {file_path}")

