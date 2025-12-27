from .handle_load import _get_grid

def _get_grid_column_row(self, gridUuid, columnUuid = None, rowUuid = None):
    grid, column, row = None, None, None
    if gridUuid:
        grid = _get_grid(self, gridUuid)
        if grid and columnUuid:
            column = grid.get_column_by_uuid(columnUuid)
        if grid and rowUuid:
            rows = self.allRows[gridUuid]
            if rows: row = rows.get(rowUuid)
            else: row = None
    return grid, column, row

