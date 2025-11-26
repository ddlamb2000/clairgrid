import os
import psycopg

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user_name = os.getenv("DB_USER_NAME")
db_password_file = os.getenv("DB_PASSWORD_FILE")

print(f"{db_host=} {db_port=} {db_name=} {db_user_name=} {db_password_file=}")

f = open(db_password_file)
db_password = f.read()
f.close()

print(f"{db_password=}")

psql_info = f"host={db_host} port={db_port} dbname={db_name} user={db_user_name} password={db_password} sslmode=disable connect_timeout=10"
# Connect to an existing database
with psycopg.connect(psql_info) as conn:

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