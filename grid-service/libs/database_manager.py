'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Database Manager for the clairgrid Grid Service.
'''

import json
import os
import psycopg
import datetime
from decimal import Decimal
from uuid import UUID
from .metadata.migration_steps import get_migration_steps, get_deletion_steps
from .utils.configuration_mixin import ConfigurationMixin
from .utils.decorators import echo
from . import metadata

class DatabaseManager(ConfigurationMixin):
    """
    Manages database connection and migrations for the Grid Service.
    """

    def __init__(self, db_name, purge_database=False):
        """
        Initializes the DatabaseManager by loading configuration from environment variables.
        Establishes database connection and runs migrations.

        Args:
            purge_database (bool): If True, purges the database before running migrations.
        """
        self.conn = None
        self.db_name = db_name
        self.purge_database = purge_database
        self.load_configuration()        
        self.connect()
        if self.purge_database and self.db_name == "clairgrid_test": self.run_deletions() # purge the test database
        self.run_migrations()
        self.import_database(self.seed_data_file)

    def load_configuration(self):
        """
        Loads configuration from environment variables.
        """
        self.db_host = os.getenv(f"DB_HOST_{self.db_name}", "db")
        self.db_port = os.getenv(f"DB_PORT_{self.db_name}", "5432")
        self.db_user_name = os.getenv(f"DB_USER_NAME_{self.db_name}", "clairgrid")
        self.db_password_file = os.getenv(f"DB_PASSWORD_FILE_{self.db_name}", "/run/secrets/db-password")
        self.db_password = self._read_password_file(self.db_password_file, f"DB_PASSWORD_{self.db_name}")
        self.timeout_threshold_milliseconds = os.getenv(f"TIMEOUT_THRESHOLD_MILLISECONDS_{self.db_name}", "5000")
        self.root_user_name = os.getenv(f"ROOT_USER_NAME_{self.db_name}", "root")
        self.root_password_file = os.getenv(f"ROOT_PASSWORD_FILE_{self.db_name}", "/run/secrets/root-password")
        self.root_password = self._read_password_file(self.root_password_file, f"ROOT_PASSWORD_{self.db_name}")
        self.seed_data_file = os.getenv(f"SEED_DATA_FILE_{self.db_name}", "seed_data.yml")

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
                print(f"Error selecting from database {self.db_name} with statement {statement} and params {params}: {e}")
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
                print(f"Error selecting from database {self.db_name} with statement {statement} and params {params}: {e}")
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

    def export_database(self, file_name):
        """
        Exports the database to a JSON file.

        Args:
            file_name (str): The name of the file to export to.
        """
        print(f"Exporting database {self.db_name} to {file_name}...", flush=True)
        
        tables = ["rows", "texts", "ints", "relationships"]
        export_data = {}

        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            with self.conn.cursor() as cur:
                for table in tables:
                    query = f"SELECT * FROM {table} WHERE uuid != '{metadata.SystemIds.RootUser}'" 
                    cur.execute(query)                    
                    columns = [desc[0] for desc in cur.description]                    
                    rows = []
                    for row in cur.fetchall():
                        row_dict = dict(zip(columns, row))
                        clean_row_dict = {}
                        for k, v in row_dict.items():
                            if v is None:
                                continue
                            if 'uuid' in k.lower():
                                system_name = metadata.SystemIds.get_name(str(v))
                                if system_name:
                                    clean_row_dict[f"{k}_metadata"] = system_name
                                else:
                                    clean_row_dict[k] = v
                            else:
                                clean_row_dict[k] = v
                        rows.append(clean_row_dict)
                    
                    export_data[table] = rows

            with open(file_name, 'w') as f:
                json.dump(export_data, f, default=json_serial, indent=4)
                
            print(f"Database {self.db_name} exported successfully to {file_name}.", flush=True)

        except Exception as e:
            print(f"Error exporting database: {e}", flush=True)
            raise e

    def import_database(self, file_name):
        """
        Imports the database from a JSON file.

        Args:
            file_name (str): The name of the file to import from.
        """
        print(f"Importing database {self.db_name} from {file_name}...", flush=True)

        try:
            with open(file_name, 'r') as f:
                import_data = json.load(f)

            tables = ["rows", "texts", "ints", "relationships"]
            pk_map = {
                "rows": ["uuid"],
                "texts": ["uuid", "partition"],
                "ints": ["uuid", "partition"],
                "relationships": ["uuid", "partition"]
            }

            with self.conn.cursor() as cur:
                with self.conn.transaction():
                    for table in tables:
                        if table in import_data:
                            rows = import_data[table]
                            print(f"Importing database {self.db_name} with {len(rows)} rows into {table}...", flush=True)
                            
                            for row in rows:
                                for key in list(row.keys()):
                                    if key.endswith('_metadata'):
                                        system_name = row.pop(key)
                                        original_key = key[:-9]  # Remove '_metadata' suffix
                                        row[original_key] = getattr(metadata.SystemIds, system_name)
                                    
                                columns = list(row.keys())
                                values = [row[col] for col in columns]
                                
                                cols_str = ', '.join(columns)
                                placeholders = ', '.join(['%s'] * len(columns))
                                
                                # Determine Conflict Target and Update Clause
                                pk_cols = pk_map.get(table, [])
                                conflict_target = ", ".join(pk_cols)
                                update_cols = [c for c in columns if c not in pk_cols]

                                if update_cols:
                                    update_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])
                                    query = f"""
                                        INSERT INTO {table} ({cols_str}) VALUES ({placeholders})
                                        ON CONFLICT ({conflict_target})
                                        DO UPDATE SET {update_clause}
                                    """
                                else:
                                    query = f"""
                                        INSERT INTO {table} ({cols_str}) VALUES ({placeholders})
                                        ON CONFLICT ({conflict_target})
                                        DO NOTHING
                                    """
                                
                                cur.execute(query, values)
            
            print(f"Database {self.db_name} imported successfully from {file_name}.", flush=True)

        except Exception as e:
            print(f"Error importing database {self.db_name} from {file_name}: {e}", flush=True)
            raise e
