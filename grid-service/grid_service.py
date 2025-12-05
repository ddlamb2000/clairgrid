"""
Grid Service Module

This module handles the initialization and maintenance of the Grid Service.
It manages database connections, executes migrations, and keeps the service running.
"""

import os
import psycopg
from queue_listener import QueueListener
from database_manager import DatabaseManager

def main():
    """
    Main entry point for the Grid Service.

    Initializes the service, connects to the database, runs migrations,
    and enters a keep-alive loop.
    """
    print("Starting Grid Service", flush=True)
    try:
        db_manager = DatabaseManager()
        
        with psycopg.connect(db_manager.get_connection_string()) as conn:
            db_manager.run_migrations(conn)
            
            print(f"Grid service on database {db_manager.db_name} initialized", flush=True)

            # Start RabbitMQ listener
            listener = QueueListener(conn, db_manager.db_name)
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            listener.start(rabbitmq_host)
            
    except Exception as e:
        print(f"Service failed to start: {e}")

if __name__ == "__main__":
    main()
