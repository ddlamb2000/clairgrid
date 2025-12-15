import unittest
from unittest.mock import MagicMock, patch
import uuid
import json
import metadata
import jwt
from authentication_manager import AuthenticationManager

class TestAuthenticationManager(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch('authentication_manager.os.getenv')
        self.mock_getenv = self.env_patcher.start()
        self.mock_getenv.side_effect = lambda k, d=None: {
            "JWT_SECRET_FILE": "/tmp/secret",
            "JWT_EXPIRATION": "60"
        }.get(k, d)

        self.pwd_patcher = patch('authentication_manager.AuthenticationManager._read_password_file')
        self.mock_read_pwd = self.pwd_patcher.start()
        self.mock_read_pwd.return_value = "supersecretkey"

        self.mock_db_manager = MagicMock()
        self.auth_manager = AuthenticationManager(self.mock_db_manager)

    def tearDown(self):
        self.pwd_patcher.stop()
        self.env_patcher.stop()

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
        
        # Verify JWT
        self.assertIn('jwt', response)
        decoded = jwt.decode(response['jwt'], "supersecretkey", algorithms=["HS256"])
        self.assertEqual(decoded['userUuid'], str(user_uuid))
        self.assertEqual(decoded['firstName'], "John")
        self.assertEqual(decoded['lastName'], "Doe")

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
