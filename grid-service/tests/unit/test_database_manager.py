import unittest
from unittest.mock import MagicMock, patch, call
import psycopg
from libs.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    @patch("libs.database_manager.os.getenv")
    @patch("libs.database_manager.DatabaseManager._read_password_file")
    @patch("libs.database_manager.psycopg.connect")
    @patch("libs.database_manager.DatabaseManager.run_migrations")
    def setUp(self, mock_run_migrations, mock_connect, mock_read_pwd, mock_getenv):
        # Setup default mock behaviors for configuration
        mock_getenv.side_effect = lambda key, default=None: {
            "DB_HOST_test_db": "localhost",
            "DB_PORT_test_db": "5432",
            "DB_NAME_test_db": "test_db",
            "DB_USER_NAME_test_db": "test_user",
            "DB_PASSWORD_FILE_test_db": "/run/secrets/db_pass",
            "TIMEOUT_THRESHOLD_MILLISECONDS_test_db": "5000",
            "ROOT_USER_NAME_test_db": "root",
            "ROOT_PASSWORD_FILE_test_db": "/run/secrets/root_pass"
        }.get(key, default)
        
        mock_read_pwd.return_value = "secret"
        
        self.db_manager = DatabaseManager("test_db")
        self.mock_connect = mock_connect
        self.mock_run_migrations = mock_run_migrations

    def test_load_configuration(self):
        """Test that configuration is loaded correctly."""
        self.assertEqual(self.db_manager.db_host, "localhost")
        self.assertEqual(self.db_manager.db_port, "5432")
        self.assertEqual(self.db_manager.db_password, "secret")

    def test_get_connection_string(self):
        """Test the connection string construction."""
        expected = "host=localhost port=5432 dbname=test_db user=test_user password=secret sslmode=disable connect_timeout=5"
        self.assertEqual(self.db_manager.get_connection_string(), expected)

    @patch("libs.database_manager.psycopg.connect")
    def test_connect_success(self, mock_psycopg_connect):
        """Test successful connection."""
        # Reset connection from setUp
        self.db_manager.conn = None
        
        mock_conn = MagicMock()
        mock_psycopg_connect.return_value = mock_conn
        
        conn = self.db_manager.connect()
        
        self.assertEqual(conn, mock_conn)
        mock_psycopg_connect.assert_called_once()

    def test_connect_existing(self):
        """Test that connect returns existing connection if open."""
        self.db_manager.conn = MagicMock()
        self.db_manager.conn.closed = False
        
        # Patch psycopg.connect to ensure it's NOT called
        with patch("libs.database_manager.psycopg.connect") as mock_psycopg_connect:
            conn = self.db_manager.connect()
            self.assertEqual(conn, self.db_manager.conn)
            mock_psycopg_connect.assert_not_called()

    def test_close(self):
        """Test closing the connection."""
        self.db_manager.conn = MagicMock()
        self.db_manager.conn.closed = False
        
        self.db_manager.close()
        
        self.db_manager.conn.close.assert_called_once()

    def test_get_latest_migration_sequence(self):
        """Test fetching the latest migration sequence."""
        # Setup the connection mock to provide a cursor
        self.db_manager.conn = MagicMock()
        mock_cur = MagicMock()
        self.db_manager.conn.cursor.return_value.__enter__.return_value = mock_cur
        
        # Case 1: Table exists, Result found
        # fetchone: 1. check table (True), 2. get max (5)
        mock_cur.fetchone.side_effect = [(True,), (5,)]
        seq = self.db_manager._get_latest_migration_sequence()
        self.assertEqual(seq, 5)
        
        # Case 2: Table exists, No result (None)
        mock_cur.fetchone.side_effect = [(True,), (None,)]
        seq = self.db_manager._get_latest_migration_sequence()
        self.assertEqual(seq, 0)
        
        # Case 3: Table does not exist
        mock_cur.fetchone.side_effect = [(False,)]
        seq = self.db_manager._get_latest_migration_sequence()
        self.assertEqual(seq, 0)
        
        # Case 4: Exception during sequence query
        mock_cur.reset_mock()
        mock_cur.fetchone.side_effect = [(True,)]
        mock_cur.execute.side_effect = [None, psycopg.Error("DB Error")]
        seq = self.db_manager._get_latest_migration_sequence()
        self.assertEqual(seq, 0)

    @patch("libs.database_manager.get_migration_steps")
    def test_run_migrations_integration(self, mock_get_steps):
        # Setup connection mock
        self.db_manager.conn = MagicMock()
        mock_cur = MagicMock()
        self.db_manager.conn.cursor.return_value.__enter__.return_value = mock_cur
        self.db_manager.conn.closed = False
        
        # Patch _get_latest_migration_sequence to return a fixed sequence
        # We also need to patch _get_migration_table_exists indirectly or just mock sequence
        # Since _get_latest_migration_sequence is an instance method, we can patch it on the class or instance.
        # But wait, run_migrations calls self._get_latest_migration_sequence().
        
        with patch.object(self.db_manager, '_get_latest_migration_sequence', return_value=2):
            # Steps available: 1 to 4
            mock_get_steps.return_value = {
                1: "SQL 1",
                2: "SQL 2",
                3: "SQL 3",
                4: "SQL 4"
            }
            
            self.db_manager.run_migrations()
            
            # Filter execute calls for migration statements
            execute_calls = [args[0][0] for args in mock_cur.execute.call_args_list]
            
            self.assertIn("SQL 3", execute_calls)
            self.assertIn("SQL 4", execute_calls)
            self.assertNotIn("SQL 1", execute_calls)
            self.assertNotIn("SQL 2", execute_calls)
            
            # Verify transaction/commit not directly on conn but on cursor or via context
            # In updated code: with self.conn.transaction(): ...
            # We can check if conn.transaction() was called
            self.assertTrue(self.db_manager.conn.transaction.called)

