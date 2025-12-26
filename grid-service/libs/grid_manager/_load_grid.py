from .. import metadata
from ..model.grid import Grid
from ..utils.decorators import echo

@echo
def _load_grid(self, grid_uuid, load_reference_grid = True):
    try:
        result = self.db_manager.select_one('''
            -- Load grid
            SELECT texts.text0, -- name
                texts.text1, -- description
                rows.revision
            FROM rows
            -- Join texts to get name and description
            LEFT OUTER JOIN texts ON rows.uuid = texts.uuid AND texts.partition = 0
            -- Filter by grid uuid and enabled
            WHERE rows.gridUuid = ''' + f"'{metadata.SystemIds.Grids}' -- Grids" + '''
            AND rows.uuid = ''' + f"'{grid_uuid}'" + '''
            AND rows.enabled = true
        '''
        )
        if result:
            grid = self.all_grids.get(grid_uuid)
            if not grid:
                grid = Grid(grid_uuid,
                            name = result[0],
                            description = result[1],
                            revision = result[2])
                print(f"New grid: {grid}")
                self.all_grids[grid_uuid] = grid
            else:
                print(f"👍🏻 Grid already in memory: {grid_uuid} {result[0]}")
            self._load_columns(grid, load_reference_grid)
            print(f"Grid loaded: {grid}")
            return grid
    except Exception as e:
        print(f"❌ Error loading grid {grid_uuid}: {e}")
        raise e

