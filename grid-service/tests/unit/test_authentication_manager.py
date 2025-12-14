import unittest
from unittest.mock import MagicMock
import uuid
import json
import metadata
from authentication_manager import AuthenticationManager

class TestAuthenticationManager(unittest.TestCase):
    def setUp(self):
        self.mock_db_manager = MagicMock()
        self.auth_manager = AuthenticationManager(self.mock_db_manager)

    def test_handle_authentication_success_json_serialization(self):
        # Setup mock to return a UUID object
        user_uuid = uuid.uuid4()
        self.mock_db_manager.select.return_value = (user_uuid, "John", "Doe")

        request = {
            "loginId": "testuser",
            "passwordHash": "secret"
        }

        # Call the method
        response = self.auth_manager.handle_authentication(request)

        # Verify response contains string UUID, not UUID object
        self.assertEqual(response['userUuid'], str(user_uuid))
        self.assertIsInstance(response['userUuid'], str)

        # Verify it is JSON serializable
        try:
            json.dumps(response)
        except TypeError:
            self.fail("Response is not JSON serializable")

    def test_handle_authentication_failure(self):
        self.mock_db_manager.select.return_value = None

        request = {
            "loginId": "testuser",
            "passwordHash": "wrong"
        }

        response = self.auth_manager.handle_authentication(request)

        self.assertEqual(response['status'], metadata.FailedStatus)

if __name__ == '__main__':
    unittest.main()

