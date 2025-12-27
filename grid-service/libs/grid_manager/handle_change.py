from .. import metadata
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
            elif changeType == metadata.ChangeAddReference:
                print(f"✏️ Add reference: {change}")
            elif changeType == metadata.ChangeLoad:
                print(f"⚙️ Load: {change}")
        return {
            "status": metadata.SuccessStatus,
            "message": "Changes applied"
        }
    except Exception as e:
        print(f"❌ Error handling change: {e}")
        return {
            "status": metadata.FailedStatus,
            "message": "Error handling change: " + str(e)
        }
