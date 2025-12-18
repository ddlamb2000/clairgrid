'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the script to import the database from a JSON file.
'''

import argparse
from libs.database_manager import DatabaseManager

def main(db_name, file_name):
    print(f"Starting import database {db_name}...")
    try:
        db_manager = DatabaseManager(db_name)
        db_manager.import_database(file_name)
        db_manager.close()
        
    except Exception as e:
        print(f"Import script failed: {e}", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import database")
    parser.add_argument("db_name", help="Name of the database")
    parser.add_argument("file_name", help="Input file name")
    args = parser.parse_args()
    main(args.db_name, args.file_name)

