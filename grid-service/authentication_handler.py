import metadata
from decorators import echo

@echo
class AuthenticationHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    @echo
    def handle(self, request):
        result = self.db_manager.select(
            '''SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'migrations'
            '''
		# "SELECT uuid, " +
		# 	"text2, " +
		# 	"text3 " +
		# 	"FROM users " +
		# 	"WHERE gridUuid = $1 " +
		# 	"AND enabled = true " +
		# 	"AND text1 = $2 " +
		# 	"AND text4 = crypt($3, text4)"


        )
        if result:
            return { 
                "status": metadata.SuccessStatus, 
                "message": "Authentication successful", 
                "loginId": request['loginId'] 
            }
        else:
            return { 
                "status": metadata.FailedStatus,
                "loginId": request['loginId'],
                "message": "Invalid username or passphrase" }
