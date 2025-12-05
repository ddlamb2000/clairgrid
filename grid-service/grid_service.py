"""
Grid Service Module

This module handles the initialization and maintenance of the Grid Service.
It manages database connections, executes migrations, and keeps the service running.
"""

from queue_listener import QueueListener
from database_manager import DatabaseManager

def main():
    """
    Main entry point for the Grid Service.

    Initializes the service, connects to the database, runs migrations,
    and enters a keep-alive loop.
    """
    print("Starting Grid Service...", flush=True)
    try:
        db_manager = DatabaseManager()        
        try:
            listener = QueueListener(db_manager.conn, db_manager.db_name)
            listener.start()
        finally:
            db_manager.close()            
    except Exception as e:
        print(f"Service failed to start: {e}")
    print("Grid Service stopped.", flush=True)
    
if __name__ == "__main__":
    main()
