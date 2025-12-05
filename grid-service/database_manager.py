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
        """
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.db_user_name = os.getenv("DB_USER_NAME")
        self.db_password_file = os.getenv("DB_PASSWORD_FILE")
        self.timeout_threshold_milliseconds = os.getenv("TIMEOUT_THRESHOLD_MILLISECONDS")
        self.root_user_name = os.getenv("ROOT_USER_NAME")
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

        print(f"DatabaseManager initialized for database {self.db_name}", flush=True)

    def get_connection_string(self):
        """
        Constructs the PostgreSQL connection string.

        Returns:
            str: The PostgreSQL connection string.
        """
        return f"host={self.db_host} port={self.db_port} dbname={self.db_name} user={self.db_user_name} password={self.db_password} sslmode=disable connect_timeout={int(self.timeout_threshold_milliseconds) // 1000}"

    def run_migrations(self, conn):
        """
        Executes database migrations.

        Checks the current migration sequence in the database and applies any
        new steps defined in `migration_steps`.

        Args:
            conn (psycopg.Connection): The active database connection.

        Raises:
            psycopg.Error: If a database error occurs during migration.
        """
        with conn.cursor() as cur:
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
                conn.rollback()

            try:
                for sequence, statement in migration_steps.items():
                    if sequence > latestMigrationSequence:
                        print(f"Update database {self.db_name} with {sequence}: {statement}")
                        cur.execute(statement)

                        cur.execute(
                            "INSERT INTO migrations (sequence, statement) VALUES (%s, %s)",
                            (sequence, statement))
                        conn.commit()

            except psycopg.Error as e:
                print(f"Error executing migration sequence {sequence}: {e}")
                raise e
