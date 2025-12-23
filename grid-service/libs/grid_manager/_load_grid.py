from .. import metadata
from ..model.grid import Grid
from ..utils.decorators import echo

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

