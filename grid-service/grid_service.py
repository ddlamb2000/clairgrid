'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Service for the clairgrid application.
'''
import os
import threading

from libs.queue_listener import QueueListener
from libs.database_manager import DatabaseManager

def main():
    """
    Main entry point for the Grid Service.

    Initializes the service, connects to the database, runs migrations,
    and enters a keep-alive loop.
    """
    print("\nStarting Grid Service...", flush=True)
    databases = os.getenv("DATABASES").split(",")
    
    listeners = []
    threads = []

    def run_listener(listener, db_manager):
        try:
            listener.start()
        finally:
            db_manager.close()

    for database in databases:
        db_manager = DatabaseManager(database, seedData = os.getenv("ENABLE_GRID_SERVICE") == "true")
        if os.getenv("ENABLE_GRID_SERVICE") == "true":
            listener = QueueListener(db_manager)
            listeners.append(listener)
            t = threading.Thread(target=run_listener, args=(listener, db_manager))
            t.start()
        if os.getenv("ENABLE_AUTHENTICATION_SERVICE") == "true":
            listenerAuthentication = QueueListener(db_manager, queueNamePrefix="authentication_service")
            listeners.append(listenerAuthentication)
            t = threading.Thread(target=run_listener, args=(listenerAuthentication, db_manager))
            t.start()
            threads.append(t)
        if os.getenv("ENABLE_LOCATE_SERVICE") == "true":
            listenerLocate = QueueListener(db_manager, queueNamePrefix="locate_service")
            listeners.append(listenerLocate)
            t = threading.Thread(target=run_listener, args=(listenerLocate, db_manager))
            t.start()
            threads.append(t)
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n⚠️ Stopping Grid Service...", flush=True)
        for listener in listeners:
            listener.stop()
        for t in threads:
            t.join()

    print("✅ Grid Service stopped.", flush=True)
    
if __name__ == "__main__":
    main()