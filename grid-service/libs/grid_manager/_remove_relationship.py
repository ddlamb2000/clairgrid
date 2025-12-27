from .. import metadata
from ..metadata import SystemIds

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

