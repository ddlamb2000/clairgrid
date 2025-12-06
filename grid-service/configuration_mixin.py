'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Configuration Mixin for the clairgrid Grid Service.
'''

class ConfigurationMixin:
    """
    Mixin class providing helper methods for loading configuration.
    """

    def _read_password_file(self, file_path, env_var_name):
        """
        Reads a password from a file.

        Args:
            file_path (str): The path to the password file.
            env_var_name (str): The name of the environment variable (for error messages).

        Returns:
            str: The password read from the file.

        Raises:
            ValueError: If the file path is not provided or the file is not found.
        """
        if not file_path:
            raise ValueError(f"{env_var_name} environment variable is not set")
        try:
            with open(file_path) as f:
                return f.read().strip()
        except FileNotFoundError:
             raise ValueError(f"Password file not found at {file_path}")

