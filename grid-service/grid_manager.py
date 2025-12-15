'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Manager for the clairgrid Grid Service.
'''

import metadata
import os
import jwt
from datetime import datetime, timezone
from configuration_mixin import ConfigurationMixin
from decorators import echo, validate_jwt

class GridManager(ConfigurationMixin):
    """
    Manages grid-related requests.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.jwt_secret_file = os.getenv("JWT_SECRET_FILE")
        self.jwt_secret = self._read_password_file(self.jwt_secret_file, "JWT_SECRET_FILE")

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
            return { "status": metadata.FailedStatus, "message": "Invalid JWT: " + str(e) }
        return None

    @echo
    @validate_jwt
    def handle_load(self, request):
        reply = { }
        grid_uuid = request.get('gridUuid')
        if grid_uuid:
            try:
                grid = self.db_manager.select(
                    "SELECT rows.uuid, texts.text1, texts.text2"
                    " FROM rows, texts"
                    " WHERE rows.gridUuid = %s"
                    " AND rows.enabled = true"
                    " AND rows.uuid = texts.uuid"
                    " AND texts.partition = 0"
                    " AND texts.text0 = %s"
                    " AND texts.text3 = crypt(%s, texts.text3)",
                    (metadata.UuidGrids, grid_uuid)
                )
                if grid:
                    reply['status'] = metadata.SuccessStatus
                    reply['gridUuid'] = grid_uuid
                else:
                    reply['status'] = metadata.FailedStatus
                    reply['message'] = "Grid not found"
            except Exception as e:
                reply['status'] = metadata.FailedStatus
                reply['message'] = "Error loading grid: " + str(e)
        else:
            reply['status'] = metadata.FailedStatus
            reply['message'] = "No grid UUID provided"

        return reply

    @echo
    @validate_jwt
    def handle_change_grid(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    @validate_jwt
    def handle_locate_grid(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    @validate_jwt
    def handle_prompt(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

