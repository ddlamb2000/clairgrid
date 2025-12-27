from .. import metadata
from ..metadata import SystemIds
from ..model.column import Column
from ..model.row import ReferenceRow

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

    referenceRow = ReferenceRow(column.referenceGrid, uuid = referenceUuid, values = referenceValues)
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

