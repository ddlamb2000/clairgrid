'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the script to purge the test database.
'''

from libs.database_manager import DatabaseManager
from libs.utils.report_exception import report_exception

def main():
    """
    Purges the test database if configured to do so.
    """
    print("⚠️ Starting Purge Test Database Script...", flush=True)
    try:
        # Initialize DatabaseManager. This loads config, connects, and runs migrations.
        db_manager = DatabaseManager("clairgrid_test", seedData=True, purgeDatabase=True)
        db_manager.close()
        
    except Exception as e:
        report_exception(e, "Purge script failed")

if __name__ == "__main__":
    main()

