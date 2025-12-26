from .. import metadata
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt

@echo
@validate_jwt
def handle_locate_grid(self, request):
    return {
        "status": metadata.SuccessStatus,
        "gridUuid": request.get('gridUuid'),
        "columnUuid": request.get('columnUuid'),
        "rowUuid": request.get('rowUuid')
    }

