'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Manager for the clairgrid Grid Service.
'''

from . import metadata
import os
import jwt
from datetime import datetime, timezone
from .configuration_mixin import ConfigurationMixin
from .decorators import echo
from .jwt_decorator import validate_jwt
from .model.grid import Grid
from .model.row import Row

class GridManager(ConfigurationMixin):
    """
    Manages grid-related requests.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.all_grids = {} # dictionary of grids by uuid
        self.all_rows = {} # dictionary of rows by grid_uuid and row_uuid
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
                        "message": "Grid not found",
                    }
                self.all_grids[grid_uuid] = grid
                self._load_rows(grid)
            else:
                print(f"Grid already in memory: {grid_uuid} {grid.name}")
        except Exception as e:
            return {
                "status": metadata.FailedStatus,
                "message": "Error loading grid: " + str(e)
            }

        return {
            "status": metadata.SuccessStatus,
            "dataSet": {
                "grid": grid.to_json(),
                "countRows": len(self.all_rows[grid.uuid]),
                "rows": [row.to_json() for row in self.all_rows[grid.uuid].values()]
            }
        }

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
        
    def _load_rows(self, grid):
        self.all_rows[grid.uuid] = { } # dictionary of rows by uuid
        try:
            result = self.db_manager.select_all('''
                SELECT rows.uuid, rows.created, rows.createdByUuid, rows.updated, rows.updatedByuuid
                FROM rows
                WHERE rows.gridUuid = %s
                AND rows.enabled = true
            ''', (grid.uuid,)
            )
            for item in result:
                row = Row(item[0])
                self.all_rows[grid.uuid][row.uuid] = row
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

