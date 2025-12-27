'''
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the script to export the database to a JSON file.
'''

import argparse
from libs.database_manager import DatabaseManager
from libs.utils.report_exception import report_exception

def main(db_name, file_name):
    print(f"Starting export database {db_name} to {file_name}...", flush=True)
    try:
        db_manager = DatabaseManager(db_name)
        db_manager.export_database(file_name)
        db_manager.close()
        
    except Exception as e:
        report_exception(e, f"Export script failed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export database")
    parser.add_argument("db_name", help="Name of the database")
    parser.add_argument("file_name", help="Output file name")
    args = parser.parse_args()
    main(args.db_name, args.file_name)
