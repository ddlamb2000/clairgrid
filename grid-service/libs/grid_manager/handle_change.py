from .. import metadata
from ..metadata import SystemIds
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt
from ..utils.report_exception import report_exception

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
