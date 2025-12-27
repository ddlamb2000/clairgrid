from .. import metadata
from ..model.grid import Grid
from ..utils.decorators import echo
from ..utils.report_exception import report_exception

@echo
def _load_grid(self, gridUuid, loadReferenceGrid = True):
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
            AND rows.uuid = ''' + f"'{gridUuid}'" + '''
            AND rows.enabled = true
        '''
        )
        if result:
            grid = Grid(gridUuid, name = result[0], description = result[1], revision = result[2])
            self.allGrids[gridUuid] = grid
            self._load_columns(grid, loadReferenceGrid)
            print(f"New grid: {grid}")
            return grid
    except Exception as e:
        report_exception(e, f"Error loading grid {gridUuid}")
        raise e
