from .. import metadata
from ..metadata import SystemIds
from ..model.grid import Grid
from ..model.row import Row

def _add_row(self, request, gridUuid, grid, rowUuid):
    print(f"✏️ Add row {rowUuid} in grid {grid}")
    if not gridUuid or not grid:
        print(f"❌ No grid provided for update")
        return {
            "status": metadata.FailedStatus,
            "message": "No grid provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        } 

    if not rowUuid:
        print(f"❌ No row UUID provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No row UUID provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
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
    print(f"self.allRows: {self.allRows[gridUuid]}")
    self.allRows[str(gridUuid)][str(rowUuid)] = row
    print(f"self.allRows: {self.allRows[gridUuid]}")
    print(f"✅ {row} added to grid {grid}")

    if gridUuid == SystemIds.Grids:
        print(f"Creating new grid in memory with uuid {rowUuid}")
        grid = Grid(rowUuid, name = "", description = "", revision = 1)
        self.allGrids[rowUuid] = grid
        self.allRows[rowUuid] = { }
        print(f"✅ New grid added to memory: {grid}")

