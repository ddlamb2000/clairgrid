import os
import psycopg

dbHost = os.getenv("DB_HOST")
dbPort = os.getenv("DB_PORT")
dbName = os.getenv("DB_NAME")
dbUserName = os.getenv("DB_USER_NAME")
dbPasswordFile = os.getenv("DB_PASSWORD_FILE")

print(f"{dbHost=} {dbPort=} {dbName=} {dbUserName=} {dbPasswordFile=}")

f = open(dbPasswordFile)
dbPassword = f.read()
f.close()

print(f"{dbPassword=}")

migrationStep = {
    1: "CREATE TABLE migrations ("
			"gridUuid uuid NOT NULL, "
			"uuid uuid NOT NULL, "
			"created timestamp with time zone NOT NULL, "
			"createdBy uuid NOT NULL, "
			"updated timestamp with time zone NOT NULL, "
			"updatedBy uuid NOT NULL, "
			"enabled boolean NOT NULL, "
			"text1 text,"
			"int1 integer,"
			"revision integer NOT NULL CHECK (revision > 0), "
			"PRIMARY KEY (gridUuid, uuid)"
			")",
}

psqlInfo = f"host={dbHost} port={dbPort} dbname={dbName} user={dbUserName} password={dbPassword} sslmode=disable connect_timeout=10"
# Connect to an existing database
with psycopg.connect(psqlInfo) as conn:

    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        # Execute a command: this creates a new table
        cur.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)
        cur.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM test")
        print(cur.fetchone())
        # will print (1, 100, "abc'def")

        # You can use `cur.executemany()` to perform an operation in batch
        cur.executemany(
            "INSERT INTO test (num) values (%s)",
            [(33,), (66,), (99,)])

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        cur.execute("SELECT id, num FROM test order by num")
        for record in cur:
            print(record)

        # Make the changes to the database persistent
        conn.commit()