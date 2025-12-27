from .. import metadata
from ..metadata import SystemIds
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt
from .handle_load import _get_grid
from ..model.row import Row
from ..utils.report_exception import report_exception

def _get_grid_column_row(self, change):
    grid, column, row = None, None, None
    gridUuid, columnUuid, rowUuid = change.get('gridUuid'), change.get('columnUuid'), change.get('rowUuid')

    if gridUuid:
        grid = _get_grid(self, gridUuid)

        if grid and columnUuid:
            column = grid.get_column_by_uuid(columnUuid)

        if grid and rowUuid:
            row = self.allRows[gridUuid].get(rowUuid)
    
    return (gridUuid, columnUuid, rowUuid), (grid, column, row)

def _add_row(self, gridUuid, grid, rowUuid):
    print(f"✏️ Add row {rowUuid} in grid {grid}")
    if not gridUuid or not grid:
        print(f"❌ No grid provided for update")
        return {
            "status": metadata.FailedStatus,
            "message": "No grid provided for update"
        } 

    if not rowUuid:
        print(f"❌ No row UUID provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No row UUID provided for update"
        }

    newItem = []
    for column in grid.columns:
        if column.typeUuid and str(column.typeUuid) == SystemIds.ReferenceColumnType:
            newItem.append([])
        elif column.typeUuid and str(column.typeUuid) == SystemIds.IntColumnType:
            newItem.append(0)
        else:
            newItem.append("")

    row = Row(grid, uuid = rowUuid, revision = 1, values = newItem)
    self.allRows[str(grid.uuid)][str(rowUuid)] = row
    print(f"New row: {row}")

def _update_row(self, gridUuid, grid, columnUuid, column, rowUuid, row, changeValue):
    print(f"✏️ Update row {row} in grid {grid} for column {column}")
    if not gridUuid or not grid:
        print(f"❌ No grid provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No grid provided for update"
        }                

    if not columnUuid or not column:
        print(f"❌ No column provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No column provided for update"
        }

    if str(column.typeUuid) == SystemIds.ReferenceColumnType:
        print(f"❌ Column {column} is a reference column, not supported for update")
        return {
            "status": metadata.FailedStatus,
            "message": "Column is a reference column, not supported for update"
        }

    if not rowUuid or not row:
        print(f"❌ No row provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No row provided for update"
        }

    row.values[column.index] = changeValue
    row._set_display_string(grid)
    print(f"✅ Row updated: {row}")

@echo
@validate_jwt
def handle_change(self, request):
    try:
        for change in request.get('changes', []):
            changeType = change.get('changeType')
            (gridUuid, columnUuid, rowUuid), (grid, column, row) = self._get_grid_column_row(change)
            if changeType == metadata.ChangeAdd:
                error = self._add_row(gridUuid, grid, rowUuid)
                if error: return error
            elif changeType == metadata.ChangeUpdate:
                error = self._update_row(gridUuid, grid, columnUuid, column, rowUuid, row, change.get('changeValue'))
                if error: return error
            elif changeType == metadata.ChangeAddReference:
                print(f"✏️ Add reference: {change}")
            elif changeType == metadata.ChangeLoad:
                print(f"⚙️ Load: {change}")
        return {
            "status": metadata.SuccessStatus
        }
    except Exception as e:
        report_exception(e, f"Error handling change")
        return {
            "status": metadata.FailedStatus,
            "message": "Error handling change: " + str(e)
        }
