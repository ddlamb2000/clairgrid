from .. import metadata
from ..utils.decorators import echo
from ..authentication.jwt_decorator import validate_jwt

@echo
@validate_jwt
def handle_prompt(self, request):
    return { "status": metadata.FailedStatus, "message": "Not implemented" }

