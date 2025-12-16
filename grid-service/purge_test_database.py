'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the script to purge the test database.
'''

from database_manager import DatabaseManager

def main():
    """
    Purges the test database if configured to do so.
    """
    print("Starting Purge Test Database Script...", flush=True)
    try:
        # Initialize DatabaseManager. This loads config, connects, and runs migrations.
        db_manager = DatabaseManager("clairgrid_test", purge_database=True)
        db_manager.close()
        
    except Exception as e:
        print(f"Purge script failed: {e}", flush=True)

if __name__ == "__main__":
    main()

