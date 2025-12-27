from .. import metadata
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt
from ..utils.report_exception import report_exception

def _get_grid(self, gridUuid):
    grid = self.allGrids.get(gridUuid)
    if not grid:
        grid = self._load_grid(gridUuid)
        if not grid:
            print(f"⚠️ Grid {gridUuid} not found")
            return None
        self.allGrids[gridUuid] = grid
        print(f"Grid added to memory: {gridUuid} {grid.name}")
        self._load_rows(grid)
    else:
        print(f"👍🏻 {grid} found in memory")

    return grid

@echo
@validate_jwt
def handle_load(self, request):
    gridUuid = request.get('gridUuid')
    rowUuid = request.get('rowUuid')
    if not gridUuid:
        return {
            "status": metadata.FailedStatus,
            "message": "No grid UUID provided"
        }

    grid = None
    try:
        grid = _get_grid(self, gridUuid)
    except Exception as e:
        report_exception(e, f"Error loading grid {gridUuid}")
        return {
            "status": metadata.FailedStatus,
            "message": "Error loading grid: " + str(e)
        }

    dataSet = {
        "gridUuid": gridUuid,
        "grid": grid.to_json()
    }
    if rowUuid:
        dataSet["rowUuid"] = rowUuid
        dataSet["rows"] = [row.to_json() for row in self.allRows[gridUuid].values() if str(row.uuid) == str(rowUuid)]
        dataSet["countRows"] = 1
    else:
        dataSet["rows"] = [row.to_json() for row in self.allRows[grid.uuid].values()]
        dataSet["countRows"] = len(dataSet["rows"])
    return {
        "status": metadata.SuccessStatus,
        "message": f"'{grid.name}' loaded",
        "dataSet": dataSet
    }
