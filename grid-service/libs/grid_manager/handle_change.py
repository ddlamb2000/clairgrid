from .. import metadata
from ..metadata import SystemIds
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt

@echo
@validate_jwt
def handle_change(self, request):
    try:
        for change in request.get('changes', []):
            changeType = change.get('changeType')
            if changeType == metadata.ChangeAdd:
                print(f"✏️ Add: {change}")
            elif changeType == metadata.ChangeUpdate:
                print(f"✏️ Update: {change}")
                gridUuid = change.get('gridUuid')
                if not gridUuid:
                    print(f"❌ No grid UUID provided")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "No grid UUID provided for update"
                    }

                grid = self.allGrids.get(gridUuid)
                if not grid:
                    grid = self._load_grid(gridUuid)
                    if not grid:
                        print(f"⚠️ Grid {gridUuid} not found")
                        return {
                            "status": metadata.FailedStatus,
                            "message": "Grid not found",
                        }
                    self.allGrids[gridUuid] = grid
                    print(f"Grid added to memory: {gridUuid} {grid.name}")
                    self._load_rows(grid)
                else:
                    print(f"👍🏻 {grid} already in memory")

                columnUuid = change.get('columnUuid')
                if not columnUuid:
                    print(f"❌ No column UUID provided")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "No column UUID provided for update"
                    }
                column = grid.get_column_by_uuid(columnUuid)
                if not column:
                    print(f"❌ Column {columnUuid} not found")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "Column not found for update"
                    }
                if str(column.typeUuid) == SystemIds.ReferenceColumnType:
                    print(f"❌ Column {columnUuid} is a reference column, not supported for update")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "Column is a reference column, not supported for update"
                    }

                rowUuid = change.get('rowUuid')
                if not rowUuid:
                    print(f"❌ No row UUID provided")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "No row UUID provided for update"
                    }

                row = self.allRows[gridUuid].get(rowUuid)
                if not row:
                    print(f"❌ Row {rowUuid} not found")
                    return {
                        "status": metadata.FailedStatus,
                        "message": "Row not found for update"
                    }

                changeValue = change.get('changeValue')
                row.values[column.index] = changeValue
                row._set_display_string(grid)
                print(f"✅ Row updated: {row}")

            elif changeType == metadata.ChangeAddReference:
                print(f"✏️ Add reference: {change}")
            elif changeType == metadata.ChangeLoad:
                print(f"⚙️ Load: {change}")
        return {
            "status": metadata.SuccessStatus
        }
    except Exception as e:
        print(f"❌ Error handling change: {e}")
        return {
            "status": metadata.FailedStatus,
            "message": "Error handling change: " + str(e)
        }
