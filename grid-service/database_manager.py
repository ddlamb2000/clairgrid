import os
import psycopg
from migration_steps import get_migration_steps

class DatabaseManager:
    """
    Manages database connection and migrations for the Grid Service.
    """

    def __init__(self):
        """
        Initializes the DatabaseManager by loading configuration from environment variables.
        Establishes database connection and runs migrations.
        """
        self.conn = None
        self.load_configuration()        
        self.connect()
        self.run_migrations()

    def load_configuration(self):
        """
        Loads configuration from environment variables.
        """
        self.db_host = os.getenv("DB_HOST", "db")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "clairgrid_master")
        self.db_user_name = os.getenv("DB_USER_NAME", "clairgrid")
        self.db_password_file = os.getenv("DB_PASSWORD_FILE")
        self.timeout_threshold_milliseconds = os.getenv("TIMEOUT_THRESHOLD_MILLISECONDS", "5000")
        self.root_user_name = os.getenv("ROOT_USER_NAME", "root")
        self.root_password_file = os.getenv("ROOT_PASSWORD_FILE")

        if not self.db_password_file:
            raise ValueError("DB_PASSWORD_FILE environment variable is not set")
        try:
            with open(self.db_password_file) as f:
                self.db_password = f.read().strip()
        except FileNotFoundError:
             raise ValueError(f"Password file not found at {self.db_password_file}")

        if not self.root_password_file:
            raise ValueError("ROOT_PASSWORD_FILE environment variable is not set")
        try:
            with open(self.root_password_file) as f:
                self.root_password = f.read().strip()
        except FileNotFoundError:
            raise ValueError(f"Password file not found at {self.root_password_file}")

    def get_connection_string(self):
        """
        Constructs the PostgreSQL connection string.

        Returns:
            str: The PostgreSQL connection string.
        """
        return f"host={self.db_host} port={self.db_port} dbname={self.db_name} user={self.db_user_name} password={self.db_password} sslmode=disable connect_timeout={int(self.timeout_threshold_milliseconds) // 1000}"

    def connect(self):
        """
        Establishes a connection to the database.

        Returns:
            psycopg.Connection: The active database connection.
        """
        if self.conn is None or self.conn.closed:
            print(f"Connecting to database {self.db_name}...", flush=True)
            self.conn = psycopg.connect(self.get_connection_string())
            print(f"Connected to database {self.db_name}.", flush=True)
        return self.conn

    def close(self):
        """
        Closes the database connection if it exists.
        """
        if self.conn and not self.conn.closed:
            self.conn.close()
            print(f"Database connection to {self.db_name} closed.", flush=True)

    def run_migrations(self):
        """
        Executes database migrations using the internal connection.

        Checks the current migration sequence in the database and applies any
        new steps defined in `migration_steps`.

        Raises:
            psycopg.Error: If a database error occurs during migration.
            Exception: If database connection is not established.
        """
        if self.conn is None or self.conn.closed:
             raise Exception("Database connection not established. Call connect() first.")

        with self.conn.cursor() as cur:
            latestMigrationSequence = 0
            migration_steps = get_migration_steps(self.root_user_name, self.root_password)
            
            try:
                cur.execute("SELECT max(sequence) FROM migrations")
                result = cur.fetchone()
                if result and result[0] is not None:
                    latestMigrationSequence = result[0]
                print(f"Latest migration sequence: {latestMigrationSequence}")
            except psycopg.Error as e:
                print(f"Error checking migration status (it might be the first run): {e}")
                self.conn.rollback()

            try:
                for sequence, statement in migration_steps.items():
                    if sequence > latestMigrationSequence:
                        print(f"Update database {self.db_name} with {sequence}: {statement}")
                        cur.execute(statement)

                        cur.execute(
                            "INSERT INTO migrations (sequence, statement) VALUES (%s, %s)",
                            (sequence, statement))
                        self.conn.commit()

            except psycopg.Error as e:
                print(f"Error executing migration sequence {sequence}: {e}")
                raise e
