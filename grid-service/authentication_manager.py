'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Authentication Manager for the clairgrid Grid Service.
'''

import metadata
from decorators import echo

class AuthenticationManager:
    """
    Manages authentication requests.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager

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
            return { 
                "status": metadata.SuccessStatus, 
                "message": "Authentication successful", 
                "loginId": login_id,
                "userUuid": str(result[0]),
                "firstName": result[1],
                "lastName": result[2]
            }
        else:
            return { 
                "status": metadata.FailedStatus,
                "loginId": login_id,
                "message": "Invalid username or passphrase" }

