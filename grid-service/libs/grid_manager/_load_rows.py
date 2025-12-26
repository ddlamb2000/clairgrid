from ..model.row import Row
from ..utils.decorators import echo

@echo
def _load_rows(self, grid):
    print(f"Loading rows for grid {grid.uuid}")
    self.allRows[grid.uuid] = { } # dictionary of rows by uuid
    dbSelectClauses = [column.dbSelectClause for column in grid.columns]
    dbSelectColumns = (',\n' if len(dbSelectClauses) > 1 else '') + ',\n'.join(dbSelectClauses)
    dbJoinClauses = ''.join(list(dict.fromkeys([column.dbJoinClause for column in grid.columns])))
    try:
        result = self.db_manager.select_all('''
            -- Load rows
            SELECT rows.uuid::text,
            rows.revision''' + dbSelectColumns + '''
            FROM rows''' +  dbJoinClauses + '''
            -- Filter by grid uuid and enabled
            WHERE rows.gridUuid = ''' + f"'{grid.uuid}' -- {grid.name}" + '''
            AND rows.enabled = true
        '''
        )
        for item in result:
            row = Row(grid, item[0], revision = item[1], values = item[2:])
            print(f"New row: {row}")
            self.allRows[grid.uuid][row.uuid] = row
        print(f"Rows loaded: {len(self.allRows[grid.uuid])}")
    except Exception as e:
        print(f"❌ Error loading rows for grid {grid.uuid}: {e}")
        raise e

