import os
import time
import psycopg
from migrationSteps import migrationSteps

dbHost, dbPort, dbName = os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME")
dbUserName, dbPasswordFile = os.getenv("DB_USER_NAME"), os.getenv("DB_PASSWORD_FILE")

dbPassword = open(dbPasswordFile).read().strip()
psqlInfo = f"host={dbHost} port={dbPort} dbname={dbName} user={dbUserName} password={dbPassword} sslmode=disable connect_timeout=10"

print(f"Starting grid service on database {dbName}", flush=True)
# Connect to an existing database
with psycopg.connect(psqlInfo) as conn:
    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        latestMigrationSequence = 0
        try:
            cur.execute("SELECT max(sequence) FROM migrations")
            latestMigrationSequence = cur.fetchone()[0]
            print(f"Latest migration sequence: {latestMigrationSequence}")
        except psycopg.Error as e:
            print(f"Error checking migration status (it might be the first run): {e}")
            conn.rollback()

        try:
            for sequence, statement in migrationSteps.items():
                if sequence > latestMigrationSequence:
                    print(f"Update database {dbName} with {sequence}: {statement}")
                    cur.execute(statement)

                    cur.execute(
                        "INSERT INTO migrations (sequence, statement) VALUES (%s, %s)",
                        (sequence, statement))
                    conn.commit()

        except psycopg.Error as e:
            print(f"Error executing migration sequence {sequence}: {e}")

while True:
    print(f"Running grid service on database {dbName}", flush=True)
    time.sleep(10)
