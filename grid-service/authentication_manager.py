'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Authentication Manager for the clairgrid Grid Service.
'''

import metadata
import os
import jwt
import datetime
from configuration_mixin import ConfigurationMixin
from decorators import echo

class AuthenticationManager(ConfigurationMixin):
    """
    Manages authentication requests.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.jwt_secret_file = os.getenv("JWT_SECRET_FILE")
        self.jwt_secret = self._read_password_file(self.jwt_secret_file, "JWT_SECRET_FILE")
        self.jwt_expiration = os.getenv("JWT_EXPIRATION", "120")

    def _generate_jwt_token(self, login_id, user_uuid, first_name, last_name):
        """
        Generates a JWT token for the authenticated user.
        """
        expiration_minutes = int(self.jwt_expiration)
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiration_minutes)
        payload = {
            "loginId": login_id,
            "userUuid": str(user_uuid),
            "firstName": first_name,
            "lastName": last_name,
            "expires": expiration_time.isoformat()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS512")

    @echo
    def handle_authentication(self, request):
        login_id = request.get('loginId')
        password = request.get('passwordHash')
        result = self.db_manager.select(
            "SELECT rows.uuid, texts.text1, texts.text2"
            " FROM rows, texts"
            " WHERE rows.gridUuid = %s"
            " AND rows.enabled = true"
            " AND rows.uuid = texts.uuid"
            " AND texts.partition = 0"
            " AND texts.text0 = %s"
            " AND texts.text3 = crypt(%s, texts.text3)",
            (metadata.UuidUsers, login_id, password)
        )
        if result:
            try:
                token = self._generate_jwt_token(login_id, result[0], result[1], result[2])
            except Exception as e:
                return { 
                    "status": metadata.FailedStatus,
                    "message": "Error generating JWT token: " + str(e)
                }
            return { 
                "status": metadata.SuccessStatus, 
                "message": "User authenticated", 
                "jwt": token
            }
        else:
            return { 
                "status": metadata.FailedStatus,
                "message": "Invalid username or passphrase" }
