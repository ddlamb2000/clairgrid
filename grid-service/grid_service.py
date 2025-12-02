import os
import time
import psycopg
from migration_steps import migration_steps

def get_db_connection_info():
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user_name = os.getenv("DB_USER_NAME")
    db_password_file = os.getenv("DB_PASSWORD_FILE")
    
    if not db_password_file:
        raise ValueError("DB_PASSWORD_FILE environment variable is not set")
        
    try:
        with open(db_password_file) as f:
            db_password = f.read().strip()
    except FileNotFoundError:
         raise ValueError(f"Password file not found at {db_password_file}")

    return f"host={db_host} port={db_port} dbname={db_name} user={db_user_name} password={db_password} sslmode=disable connect_timeout=10", db_name

def run_migrations(conn, db_name):
    with conn.cursor() as cur:
        latestMigrationSequence = 0
        try:
            cur.execute("SELECT max(sequence) FROM migrations")
            result = cur.fetchone()
            if result and result[0] is not None:
                latestMigrationSequence = result[0]
            print(f"Latest migration sequence: {latestMigrationSequence}")
        except psycopg.Error as e:
            print(f"Error checking migration status (it might be the first run): {e}")
            conn.rollback()

        try:
            for sequence, statement in migration_steps.items():
                if sequence > latestMigrationSequence:
                    print(f"Update database {db_name} with {sequence}: {statement}")
                    cur.execute(statement)

                    cur.execute(
                        "INSERT INTO migrations (sequence, statement) VALUES (%s, %s)",
                        (sequence, statement))
                    conn.commit()

        except psycopg.Error as e:
            print(f"Error executing migration sequence {sequence}: {e}")
            raise e

def main():
    print("Starting Grid Service", flush=True)
    try:
        psql_info, db_name = get_db_connection_info()
        print(f"Starting grid service on database {db_name}", flush=True)
        
        # Connect to an existing database
        with psycopg.connect(psql_info) as conn:
            run_migrations(conn, db_name)

        while True:
            print(f"Running grid service on database {db_name}", flush=True)
            time.sleep(10)
            
    except Exception as e:
        print(f"Service failed to start: {e}")

if __name__ == "__main__":
    main()
