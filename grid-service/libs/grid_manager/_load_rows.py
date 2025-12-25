from ..model.row import Row

def _load_rows(self, grid):
    print(f"Loading rows for grid {grid.uuid}")
    self.all_rows[grid.uuid] = { } # dictionary of rows by uuid
    db_select_clauses = [column.db_select_clause for column in grid.columns]
    db_select_columns = (',\n' if len(db_select_clauses) > 1 else '') + ',\n'.join(db_select_clauses)
    db_join_clauses = '\n'.join(list(dict.fromkeys([column.db_join_clause for column in grid.columns])))
    try:
        result = self.db_manager.select_all('''
            SELECT rows.uuid::text, rows.revision
        ''' + db_select_columns + '''
            FROM rows
        ''' + db_join_clauses + '''
            WHERE rows.gridUuid = %s
            AND rows.enabled = true
        ''', (grid.uuid,)
        )
        for item in result:
            print(f"Loading row: {item[0]}")
            row = Row(grid, item[0], revision = item[1], values = item[2:])
            print(f"New row: {row}")
            self.all_rows[grid.uuid][row.uuid] = row
        print(f"Rows loaded: {len(self.all_rows[grid.uuid])}")
    except Exception as e:
        print(f"❌ Error loading rows for grid {grid.uuid}: {e}")
        raise e

