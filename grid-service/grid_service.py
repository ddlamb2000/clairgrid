"""
Grid Service Module

This module handles the initialization and maintenance of the Grid Service.
It manages database connections, executes migrations, and keeps the service running.
"""

import os
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
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            listener.start(rabbitmq_host)
        finally:
            db_manager.close()            
    except Exception as e:
        print(f"Service failed to start: {e}")
    print("Grid Service stopped.", flush=True)
    
if __name__ == "__main__":
    main()
