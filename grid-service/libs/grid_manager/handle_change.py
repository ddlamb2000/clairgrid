from .. import metadata
from ..metadata import SystemIds
from ..model.grid import Grid
from ..model.column import Column
from ..model.row import Row, ReferenceRow
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt
from .handle_load import _get_grid
from ..utils.report_exception import report_exception

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

def _add_relationship(self, request, gridUuid, grid, columnUuid, column, rowUuid, row, changeValue):
    print(f"✏️ Add relationship for row {row} in grid {grid} for column {column} with value '{changeValue}'")
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

    if str(column.typeUuid) != SystemIds.ReferenceColumnType:
        print(f"❌ Column {column} is not a reference column, not supported for update")
        return {
            "status": metadata.FailedStatus,
            "message": "Column is not a reference column, not supported for update",
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

    if not changeValue:
        print(f"❌ No change value provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No change value provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    referenceUuid = changeValue.get('uuid')
    if not referenceUuid:
        print(f"❌ No reference UUID provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No reference UUID provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    referenceValues = changeValue.get('values')
    if not referenceValues:
        print(f"❌ No reference values provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No reference values provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    referenceRow = ReferenceRow(column.referenceGrid, uuid =referenceUuid, values = referenceValues)
    row.values[column.index] += [referenceRow.to_json()]
    print(f"✅ Relationship added: {row}")

    if gridUuid == SystemIds.Grids and columnUuid == SystemIds.GridColumnColumns:
        print(f"Updating columns usage for grid {grid}")
        (relatedGrid, relatedColumn, relatedRow) = self._get_grid_column_row(rowUuid)
        (relatedColumnGrid, relatedColumnColumn, relatedColumnRow) = self._get_grid_column_row(SystemIds.Columns, None, referenceUuid)
        if relatedGrid and relatedColumnRow:
            columnType = relatedColumnRow.values[2]
            typeUuid = columnType[0].get('uuid')
            column = Column(referenceUuid,
                    index = 0,
                    fieldIndex = 0,
                    order = relatedColumnRow.values[0],
                    name = relatedColumnRow.values[1],
                    typeUuid = typeUuid,
                    columnIndex = relatedColumnRow.values[3],
                    display = relatedColumnRow.values[5])

            relatedGrid.columns.append(column)

def _remove_relationship(self, request, gridUuid, grid, columnUuid, column, rowUuid, row, changeValue):  
    print(f"✏️ Remove relationship for row {row} in grid {grid} for column {column} with value '{changeValue}'")
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

    if str(column.typeUuid) != SystemIds.ReferenceColumnType:
        print(f"❌ Column {column} is not a reference column, not supported for update")
        return {
            "status": metadata.FailedStatus,
            "message": "Column is not a reference column, not supported for update",
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

    if not changeValue:
        print(f"❌ No change value provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No change value provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    referenceUuid = changeValue.get('uuid')
    if not referenceUuid:
        print(f"❌ No reference UUID provided")
        return {
            "status": metadata.FailedStatus,
            "message": "No reference UUID provided for update",
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    values = row.values[column.index]
    for value in values:
        if value.get('uuid') == referenceUuid:
            values.remove(value)
            break
    print(f"✅ Relationship removed for uuid={referenceUuid}: {row}")

@echo
@validate_jwt
def handle_change(self, request):
    try:
        for change in request.get('changes', []):
            changeType = change.get('changeType')
            gridUuid, columnUuid, rowUuid = change.get('gridUuid'), change.get('columnUuid'), change.get('rowUuid')
            (grid, column, row) = self._get_grid_column_row(gridUuid, columnUuid, rowUuid)
            if changeType == metadata.ChangeAdd:
                error = self._add_row(request, gridUuid, grid, rowUuid)
                if error: return error
            elif changeType == metadata.ChangeUpdate:
                error = self._update_row(request, gridUuid, grid, columnUuid, column, rowUuid, row, change.get('changeValue'))
                if error: return error
            elif changeType == metadata.ChangeAddRelationship:
                error = self._add_relationship(request, gridUuid, grid, columnUuid, column, rowUuid, row, change.get('changeValue'))
                if error: return error
            elif changeType == metadata.ChangeRemoveRelationship:
                error = self._remove_relationship(request, gridUuid, grid, columnUuid, column, rowUuid, row, change.get('changeValue'))
                if error: return error
            elif changeType == metadata.ChangeLoad:
                return self.handle_load({
                    "gridUuid": gridUuid,
                    "userUuid": request.get('userUuid'),
                    "user": request.get('user'),
                    "jwt": request.get('jwt')
                })

        return {
            "status": metadata.SuccessStatus,
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }

    except Exception as e:
        report_exception(e, f"Error handling change")
        return {
            "status": metadata.FailedStatus,
            "message": "Error handling change: " + str(e),
            "userUuid": request.get('userUuid'),
            "user": request.get('user')
        }
