from ..model.row import Row
from ..utils.decorators import echo

@echo
def _load_rows(self, grid):
    print(f"Loading rows for grid {grid.uuid}")
    self.all_rows[grid.uuid] = { } # dictionary of rows by uuid
    db_select_clauses = [column.db_select_clause for column in grid.columns]
    db_select_columns = (',\n' if len(db_select_clauses) > 1 else '') + ',\n'.join(db_select_clauses)
    db_join_clauses = ''.join(list(dict.fromkeys([column.db_join_clause for column in grid.columns])))
    try:
        result = self.db_manager.select_all('''
            -- Load rows
            SELECT rows.uuid::text,
            rows.revision''' + db_select_columns + '''
            FROM rows''' +  db_join_clauses + '''
            -- Filter by grid uuid and enabled
            WHERE rows.gridUuid = ''' + f"'{grid.uuid}' -- {grid.name}" + '''
            AND rows.enabled = true
        '''
        )
        number_of_rows = 0
        for item in result:
            row = Row(grid, item[0], revision = item[1], values = item[2:])
            print(f"New row: {row}")
            number_of_rows += 1
            self.all_rows[grid.uuid][row.uuid] = row
        print(f"Rows loaded: {number_of_rows}")
    except Exception as e:
        print(f"❌ Error loading rows for grid {grid.uuid}: {e}")
        raise e

