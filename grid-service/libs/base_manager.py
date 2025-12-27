'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Base Manager for the clairgrid Grid Service.
'''

import os
import jwt
from datetime import datetime, timezone
from . import metadata
from .utils.configuration_mixin import ConfigurationMixin
from .utils.decorators import echo
from .utils.report_exception import report_exception

class BaseManager(ConfigurationMixin):
    """
    Base manager class for handling common functionality.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.jwt_secret_file = os.getenv(f"JWT_SECRET_FILE_{self.db_manager.db_name}", "/run/secrets/jwt-secret")
        self.jwt_secret = self._read_password_file(self.jwt_secret_file, f"JWT_SECRET_{self.db_manager.db_name}")

    @echo
    def _handle_jwt_validation(self, request):
        token = request.get('jwt')
        if not token:
            return { "status": metadata.FailedStatus, "message": "No JWT provided" }
        try:
            decoded_token = jwt.decode(token, self.jwt_secret, algorithms=["HS512"])
            expires = datetime.fromisoformat(decoded_token.get('expires'))
            if expires < datetime.now(timezone.utc):
                return { "status": metadata.FailedStatus, "message": "Token expired" }
        except Exception as e:
            report_exception(e, "Error validating JWT")
            return { "status": metadata.FailedStatus, "message": "Invalid JWT: " + str(e) }
        return None

