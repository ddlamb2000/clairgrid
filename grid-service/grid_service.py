'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Grid Service for the clairgrid application.
'''

from queue_listener import QueueListener
from database_manager import DatabaseManager

def main():
    """
    Main entry point for the Grid Service.

    Initializes the service, connects to the database, runs migrations,
    and enters a keep-alive loop.
    """
    print("\nStarting Grid Service...", flush=True)
    try:
        db_manager = DatabaseManager()        
        try:
            listener = QueueListener(db_manager)
            listener.start()
        finally:
            db_manager.close()            
    except Exception as e:
        print(f"Service failed to start: {e}")
    print("Grid Service stopped.", flush=True)
    
if __name__ == "__main__":
    main()
