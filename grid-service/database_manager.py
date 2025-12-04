import os
import psycopg
from migration_steps import get_migration_steps

class DatabaseManager:
    """
    Manages database connection and migrations for the Grid Service.
    """

    @staticmethod
    def get_db_connection_info():
        """
        Retrieves database connection information from environment variables.

        Reads various environment variables to construct the PostgreSQL connection string
        and other configuration parameters.

        Returns:
            tuple: A tuple containing:
                - str: The PostgreSQL connection string.
                - str: The database name.
                - str: The root user name.
                - str: The root password.

        Raises:
            ValueError: If required environment variables or password files are missing.
        """
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user_name = os.getenv("DB_USER_NAME")
        db_password_file = os.getenv("DB_PASSWORD_FILE")
        timeout_threshold_milliseconds = os.getenv("TIMEOUT_THRESHOLD_MILLISECONDS")
        root_user_name = os.getenv("ROOT_USER_NAME")
        root_password_file = os.getenv("ROOT_PASSWORD_FILE")

        if not db_password_file:
            raise ValueError("DB_PASSWORD_FILE environment variable is not set")        
        try:
            with open(db_password_file) as f:
                db_password = f.read().strip()
        except FileNotFoundError:
             raise ValueError(f"Password file not found at {db_password_file}")

        if not root_password_file:
            raise ValueError("ROOT_PASSWORD_FILE environment variable is not set")
        try:
            with open(root_password_file) as f:
                root_password = f.read().strip()
        except FileNotFoundError:
            raise ValueError(f"Password file not found at {root_password_file}")

        return (f"host={db_host} port={db_port} dbname={db_name} user={db_user_name} password={db_password} sslmode=disable connect_timeout={int(timeout_threshold_milliseconds) // 1000}", 
                db_name, root_user_name, root_password)

    @staticmethod
    def run_migrations(conn, db_name, root_user_name, root_password):
        """
        Executes database migrations.

        Checks the current migration sequence in the database and applies any
        new steps defined in `migration_steps`.

        Args:
            conn (psycopg.Connection): The active database connection.
            db_name (str): The name of the database being updated.
            root_user_name (str): The name of the root user (unused in current logic but passed).
            root_password (str): The password of the root user (unused in current logic but passed).

        Raises:
            psycopg.Error: If a database error occurs during migration.
        """
        with conn.cursor() as cur:
            latestMigrationSequence = 0
            migration_steps = get_migration_steps(root_user_name, root_password)
            
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

