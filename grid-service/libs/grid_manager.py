'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Manager for the clairgrid Grid Service.
'''

from . import metadata
from .base_manager import BaseManager
from .utils.decorators import echo
from .authentication.jwt_decorator import validate_jwt
from .model.grid import Grid
from .model.row import Row
from .model.column import Column

class GridManager(BaseManager):
    """
    Manages grid-related requests.
    """
    def __init__(self, db_manager):
        BaseManager.__init__(self, db_manager)
        self.all_grids = {} # dictionary of grids by uuid
        self.all_rows = {} # dictionary of rows by grid_uuid and row_uuid

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
                    print(f"Grid not found: {grid_uuid}")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "Grid not found",
                    }
                self.all_grids[grid_uuid] = grid
                print(f"Grid added to memory: {grid_uuid} {grid.name}")
                self._load_rows(grid)
            else:
                print(f"Grid already in memory: {grid_uuid} {grid.name}")
        except Exception as e:
            print(f"❌ Error loading grid {grid_uuid}: {e}")
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
                SELECT texts.text0 as name,
                    texts.text1 as description,
                    rows.created,
                    rows.createdByUuid,
                    rows.updated,
                    rows.updatedByuuid
                FROM rows
                LEFT OUTER JOIN texts ON rows.uuid = texts.uuid AND texts.partition = 0
                WHERE rows.gridUuid = %s AND rows.uuid = %s AND rows.enabled = true
            ''', (metadata.SystemIds.Grids, grid_uuid)
            )
            if result:
                grid = self.all_grids.get(grid_uuid)
                if not grid:
                    grid = Grid(grid_uuid,
                                name = result[0],
                                description = result[1],
                                created = result[2],
                                created_by = result[3],
                                updated = result[4],
                                updated_by = result[5])
                    print(f"New grid: {grid}")
                    self.all_grids[grid_uuid] = grid
                else:
                    print(f"Grid already in memory: {grid_uuid} {result[0]}")
                self._load_columns(grid)
                print(f"Grid loaded: {grid}")
                return grid
        except Exception as e:
            print(f"❌ Error loading grid {grid_uuid}: {e}")
            raise e
        
    def _load_columns(self, grid):
        try:
            result = self.db_manager.select_all('''
                SELECT rows.uuid,
                        texts.text0 as order, 
                        texts.text1 as name,
						rel2.toUuid0 as typeUuid,
                        ints.int0 as columnIndex
                FROM relationships rel1
                LEFT OUTER JOIN rows ON rows.gridUuid = %s AND rows.uuid = rel1.toUuid0 AND rows.enabled = true
                LEFT OUTER JOIN texts ON texts.uuid = rows.uuid AND texts.partition = 0
				LEFT OUTER JOIN relationships rel2 ON rel2.fromUuid = rows.uuid AND rel2.partition = 0
                LEFT OUTER JOIN ints ON ints.uuid = rows.uuid AND ints.partition = 0
                WHERE rel1.fromUuid = %s AND rel1.partition = 0
                ORDER BY texts.text0
            ''', (metadata.SystemIds.Columns, grid.uuid)
            )
            index = 0
            for item in result: 
                column = Column(item[0], index, order = item[1], name = item[2], typeUuid = item[3], columnIndex = item[4])
                index += 1
                print(f"New column: {column}")
                grid.columns.append(column)
        except Exception as e:
            print(f"❌ Error loading columns for grid {grid.uuid}: {e}")
            raise e

    def _load_rows(self, grid):
        print(f"Loading rows for grid {grid.uuid}")
        self.all_rows[grid.uuid] = { } # dictionary of rows by uuid
        db_select_clauses = [column.db_select_clause for column in grid.columns]
        db_select_columns = (',\n' if len(db_select_clauses) > 1 else '') + ',\n'.join(db_select_clauses)
        db_join_clauses = '\n'.join(list(dict.fromkeys([column.db_join_clause for column in grid.columns])))
        try:
            result = self.db_manager.select_all('''
                SELECT rows.uuid,
                        rows.created,
                        rows.createdByUuid,
                        rows.updated,
                        rows.updatedByuuid''' + db_select_columns + '''
                FROM rows
            ''' + db_join_clauses + '''
                WHERE rows.gridUuid = %s
                AND rows.enabled = true
            ''', (grid.uuid,)
            )
            for item in result:
                print(f"Loading row: {item[0]}")
                row = Row(item[0], created = item[1], created_by = item[2], updated = item[3], updated_by = item[4], values = item[5:])
                print(f"New row: {row}")
                self.all_rows[grid.uuid][row.uuid] = row
            print(f"Rows loaded: {len(self.all_rows[grid.uuid])}")
        except Exception as e:
            print(f"❌ Error loading rows for grid {grid.uuid}: {e}")
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

