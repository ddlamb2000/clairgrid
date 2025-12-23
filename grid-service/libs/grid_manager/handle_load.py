from .. import metadata
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt

@echo
@validate_jwt
def handle_load(self, request):
    grid_uuid = request.get('gridUuid')
    if not grid_uuid:
        return {
            "status": metadata.FailedStatus,
            "message": "No grid UUID provided"
        }

    grid = None
    try:
        grid = self.all_grids.get(grid_uuid)
        if not grid:
            grid = self._load_grid(grid_uuid)
            if not grid:
                print(f"⚠️ Grid not found: {grid_uuid}")
                return {
                    "status": metadata.FailedStatus,
                    "message": "Grid not found",
                }
            self.all_grids[grid_uuid] = grid
            print(f"Grid added to memory: {grid_uuid} {grid.name}")
            self._load_rows(grid)
        else:
            print(f"Grid already in memory: {grid_uuid} {grid.name}")
    except Exception as e:
        print(f"❌ Error loading grid {grid_uuid}: {e}")
        return {
            "status": metadata.FailedStatus,
            "message": "Error loading grid: " + str(e)
        }

    return {
        "status": metadata.SuccessStatus,
        "dataSet": {
            "grid": grid.to_json(),
            "countRows": len(self.all_rows[grid.uuid]),
            "rows": [row.to_json() for row in self.all_rows[grid.uuid].values()]
        }
    }

