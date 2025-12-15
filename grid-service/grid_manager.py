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
from grid import Grid
from row import Row

class GridManager(ConfigurationMixin):
    """
    Manages grid-related requests.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.all_grids = {} # dictionary of grids by uuid
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
        grid_uuid = request.get('gridUuid')
        if not grid_uuid:
            return {
                "status": metadata.FailedStatus,
                "message": "No grid UUID provided"
            }

        grid = None
        try:
            grid = self.all_grids.get(grid_uuid)
            if not grid:
                grid = self._load_grid(grid_uuid)
                if not grid:
                    return {
                        "status": metadata.FailedStatus,
                        "message": "Grid not found"
                    }
                self.all_grids[grid_uuid] = grid
            else:
                print(f"Grid already in memory: {grid_uuid} {grid.name}")
        except Exception as e:
            return {
                "status": metadata.FailedStatus,
                "message": "Error loading grid: " + str(e)
            }

        if grid:
            reply = {
                "dataSet": {
                    "grid": grid.to_json(),
                    "rows": []
                }
            }
            error = self._load_rows(grid, reply)
            if error:
                return {
                    "status": metadata.FailedStatus,
                    "message": "Error loading rows: " + str(error)
                }
            reply['status'] = metadata.SuccessStatus
            return reply

    def _load_rows(self, grid, reply):
        try:
            result = self.db_manager.select_all('''
                SELECT rows.uuid, rows.created, rows.createdByUuid, rows.updated, rows.updatedByuuid
                FROM rows
                WHERE rows.gridUuid = %s
                AND rows.enabled = true
            ''', (grid.uuid,)
            )
            for row in result:
                reply['dataSet']['rows'].append(Row(row[0]).to_json())
        except Exception as e:
            return e

    @echo
    def _load_grid(self, grid_uuid):
        try:
            result = self.db_manager.select_one('''
                SELECT texts.text0, rows.created, rows.createdByUuid, rows.updated, rows.updatedByuuid
                FROM rows
                LEFT OUTER JOIN texts
                ON rows.uuid = texts.uuid
                AND texts.partition = 0
                WHERE rows.gridUuid = %s
                AND rows.uuid = %s
                AND rows.enabled = true
            ''', (metadata.UuidGrids, grid_uuid)
            )
            if result:
                grid = self.all_grids.get(grid_uuid)
                if not grid:
                    grid = Grid(grid_uuid, name = result[0])
                    self.all_grids[grid_uuid] = grid
                else:
                    print(f"Grid already in memory: {grid_uuid} {result[0]}")
                return grid
        except Exception as e:
            raise e
        
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

