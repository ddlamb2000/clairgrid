from .. import metadata
from ..metadata import SystemIds

def _update_row(self, request, gridUuid, grid, columnUuid, column, rowUuid, row, changeValue):
    print(f"✏️ Update row {row} in grid {grid} for column {column} with value '{changeValue}'")
    if not gridUuid or not grid:
        print(f"❌ No grid provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No grid provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }                

    if not columnUuid or not column:
        print(f"❌ No column provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No column provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    if str(column.typeUuid) == SystemIds.ReferenceColumnType:
        print(f"❌ Column {column} is a reference column, not supported for update")
        return {
            "status": metadata.FailedStatus,
            "message": "Column is a reference column, not supported for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    if not rowUuid or not row:
        print(f"❌ No row provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No row provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    row.values[column.index] = changeValue
    row._set_display_string(grid)
    print(f"✅ Row updated: {row}")

    if gridUuid == SystemIds.Grids:
        (relatedGrid, relatedColumn, relatedRow) = self._get_grid_column_row(rowUuid)
        if columnUuid == SystemIds.GridColumnName:
            relatedGrid.name = changeValue
        elif columnUuid == SystemIds.GridColumnDesc:
            relatedGrid.description = changeValue
        print(f"✅ Grid updated: {grid}")

