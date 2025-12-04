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
        psql_info, db_name, root_user_name, root_password = DatabaseManager.get_db_connection_info()
        print(f"Starting grid service on database {db_name}", flush=True)
        
        with psycopg.connect(psql_info) as conn:
            DatabaseManager.run_migrations(conn, db_name, root_user_name, root_password)
            
            print(f"Grid service on database {db_name} initialized", flush=True)

            # Start RabbitMQ listener
            listener = QueueListener(conn, db_name)
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            listener.start(rabbitmq_host)
            
    except Exception as e:
        print(f"Service failed to start: {e}")

if __name__ == "__main__":
    main()
