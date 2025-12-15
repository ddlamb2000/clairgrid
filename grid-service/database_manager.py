'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Database Manager for the clairgrid Grid Service.
'''

import os
import psycopg
from migration_steps import get_migration_steps, get_deletion_steps
from configuration_mixin import ConfigurationMixin
from decorators import echo

class DatabaseManager(ConfigurationMixin):
    """
    Manages database connection and migrations for the Grid Service.
    """

    def __init__(self, purge_database=False):
        """
        Initializes the DatabaseManager by loading configuration from environment variables.
        Establishes database connection and runs migrations.

        Args:
            purge_database (bool): If True, purges the database before running migrations.
        """
        self.conn = None
        self.purge_database = purge_database
        self.load_configuration()        
        self.connect()
        if self.purge_database and self.db_name == "clairgrid_test": self.run_deletions() # purge the test database
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
        self.db_password = self._read_password_file(self.db_password_file, "DB_PASSWORD_FILE")
        self.timeout_threshold_milliseconds = os.getenv("TIMEOUT_THRESHOLD_MILLISECONDS", "5000")
        self.root_user_name = os.getenv("ROOT_USER_NAME", "root")
        self.root_password_file = os.getenv("ROOT_PASSWORD_FILE")
        self.root_password = self._read_password_file(self.root_password_file, "ROOT_PASSWORD_FILE")

    def get_connection_string(self):
        """
        Constructs the PostgreSQL connection string.

        Returns:
            str: The PostgreSQL connection string.
        """
        return (
            f"host={self.db_host} "
            f"port={self.db_port} "
            f"dbname={self.db_name} "
            f"user={self.db_user_name} "
            f"password={self.db_password} "
            f"sslmode=disable "
            f"connect_timeout={int(self.timeout_threshold_milliseconds) // 1000}"
        )

    def connect(self):
        """
        Establishes a connection to the database.

        Returns:
            psycopg.Connection: The active database connection.
        """
        if self.conn is None or self.conn.closed:
            print(f"Connecting to database {self.db_name}...", flush=True)
            self.conn = psycopg.connect(self.get_connection_string(), autocommit=True)
            print(f"Connected to database {self.db_name}.", flush=True)
        return self.conn

    def close(self):
        """
        Closes the database connection if it exists.
        """
        if self.conn and not self.conn.closed:
            self.conn.close()
            print(f"Database connection to {self.db_name} closed.", flush=True)

    def _get_migration_table_exists(self):
        """
        Checks if the 'migrations' table exists in the public schema.

        Args:
            cur (psycopg.Cursor): The database cursor.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        migrationTableExists = False
        with self.conn.cursor() as cur:
            try:
                cur.execute('''
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = 'migrations'
                        )
                ''')
                result = cur.fetchone()
                if result and result[0] is not None:
                    migrationTableExists = result[0]
            except psycopg.Error as e:
                print(f"Error checking if migration table exists: {e}", flush=True)

        return migrationTableExists

    def _get_latest_migration_sequence(self):
        """
        Retrieves the latest migration sequence applied to the database.

        Args:
            cur (psycopg.Cursor): The database cursor.

        Returns:
            int: The latest migration sequence number.
        """
        migrationTableExists = self._get_migration_table_exists()
        if not migrationTableExists:
            return 0

        latestMigrationSequence = 0
        with self.conn.cursor() as cur:
            try:
                cur.execute("SELECT max(sequence) FROM migrations")
                result = cur.fetchone()
                if result and result[0] is not None:
                    latestMigrationSequence = result[0]
                print(f"Latest migration sequence is {latestMigrationSequence}.")
            except psycopg.Error as e:  
                print(f"Error getting latest migration sequence: {e}", flush=True)

        return latestMigrationSequence

    @echo
    def select_one(self, statement, params=None):
        if self.conn is None or self.conn.closed:
             raise Exception("Database connection not established. Call connect() first.")

        with self.conn.cursor() as cur:
            try:
                cur.execute(statement, params)
                return cur.fetchone()
            except psycopg.Error as e:
                print(f"Error selecting from database: {e}")
                raise e

    @echo
    def select_all(self, statement, params=None):
        if self.conn is None or self.conn.closed:
             raise Exception("Database connection not established. Call connect() first.")

        with self.conn.cursor() as cur:
            try:
                cur.execute(statement, params)
                for row in cur: yield row
            except psycopg.Error as e:
                print(f"Error selecting from database: {e}")
                raise e

    def _execute_migration_step(self, sequence, statement):
        """
        Executes a single migration step and records it.

        Args:
            cur (psycopg.Cursor): The database cursor.
            sequence (int): The migration sequence number.
            statement (str): The SQL statement to execute.
        """
        with self.conn.cursor() as cur:
            with self.conn.transaction():
                cur.execute(statement)
                cur.execute(
                    "INSERT INTO migrations (sequence, statement) VALUES (%s, %s)",
                    (sequence, statement))

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
            latestMigrationSequence = self._get_latest_migration_sequence()
            try:
                for sequence, statement in get_migration_steps(self.root_user_name, self.root_password).items():
                    if sequence > latestMigrationSequence:
                        print(f"Update database {self.db_name} with migration step {sequence}")
                        self._execute_migration_step(sequence, statement)
            except psycopg.Error as e:
                print(f"Error executing migration sequence {sequence}: {e}", flush=True)
                raise e

    def run_deletions(self):
        """
        Executes database deletions using the internal connection.

        Applies steps defined in `deletion_steps`.

        Raises:
            psycopg.Error: If a database error occurs during deletion.
            Exception: If database connection is not established.
        """
        if self.conn is None or self.conn.closed:
            raise Exception("Database connection not established. Call connect() first.")
        for sequence, statement in get_deletion_steps().items():
            with self.conn.cursor() as cur:
                try:
                    print(f"Update database {self.db_name} with deletion step {sequence}", flush=True)
                    cur.execute(statement)
                except psycopg.Error as e:
                    print(f"Error executing deletion sequence {sequence}: {e}", flush=True)
