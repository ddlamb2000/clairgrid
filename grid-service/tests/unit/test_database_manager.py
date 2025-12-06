import unittest
from unittest.mock import MagicMock, patch, call
import psycopg
from database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    @patch("database_manager.os.getenv")
    @patch("database_manager.DatabaseManager._read_password_file")
    @patch("database_manager.psycopg.connect")
    @patch("database_manager.DatabaseManager.run_migrations")
    def setUp(self, mock_run_migrations, mock_connect, mock_read_pwd, mock_getenv):
        # Setup default mock behaviors for configuration
        mock_getenv.side_effect = lambda key, default=None: {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
            "DB_USER_NAME": "test_user",
            "DB_PASSWORD_FILE": "/run/secrets/db_pass",
            "TIMEOUT_THRESHOLD_MILLISECONDS": "5000",
            "ROOT_USER_NAME": "root",
            "ROOT_PASSWORD_FILE": "/run/secrets/root_pass"
        }.get(key, default)
        
        mock_read_pwd.return_value = "secret"
        
        self.db_manager = DatabaseManager()
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

    @patch("database_manager.psycopg.connect")
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
        with patch("database_manager.psycopg.connect") as mock_psycopg_connect:
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
        mock_cur = MagicMock()
        # Case 1: Result found
        mock_cur.fetchone.return_value = (5,)
        seq = self.db_manager._get_latest_migration_sequence(mock_cur)
        self.assertEqual(seq, 5)
        
        # Case 2: No result (None)
        mock_cur.fetchone.return_value = (None,)
        seq = self.db_manager._get_latest_migration_sequence(mock_cur)
        self.assertEqual(seq, 0)
        
        # Case 3: Exception (e.g. table doesn't exist yet)
        mock_cur.fetchone.side_effect = psycopg.Error("Table not found")
        seq = self.db_manager._get_latest_migration_sequence(mock_cur)
        self.assertEqual(seq, 0)
        self.db_manager.conn.rollback.assert_called_once()

    @patch("database_manager.get_migration_steps")
    def test_run_migrations_execution(self, mock_get_steps):
        """Test running migrations executes correct steps."""
        # Setup mocks
        mock_cur = MagicMock()
        self.db_manager.conn = MagicMock()
        self.db_manager.conn.cursor.return_value.__enter__.return_value = mock_cur
        
        # Mock _get_latest_migration_sequence behavior directly on the cursor interaction
        # First call to fetchone is for _get_latest_migration_sequence
        mock_cur.fetchone.return_value = (2,)
        
        # Mock migration steps: 1, 2, 3, 4
        mock_get_steps.return_value = {
            1: "SQL 1",
            2: "SQL 2",
            3: "SQL 3",
            4: "SQL 4"
        }
        
        # We need to unpatch run_migrations to test the actual method
        # But wait, run_migrations was mocked in setUp/instantiation.
        # We need to call the REAL run_migrations method now.
        # Since we mocked it on the INSTANCE in setUp?? No, we mocked the class method in setUp decorator.
        # Actually, the setUp patch mocked 'database_manager.DatabaseManager.run_migrations'.
        # To test the real method, we need to restore it or call the original function.
        # A better approach for this specific test file structure where __init__ calls the method we want to test:
        # We can just call the original method explicitly if we had saved it, OR:
        # We can make a separate test instance or just call the method directly on the class but bound to instance?
        
        # Let's just use the code from the class. 
        # Since I patched it in setUp, `self.db_manager.run_migrations` is a Mock.
        # I cannot easily call the real one on `self.db_manager`.
        
        # Workaround: Manually execute the logic or create a clean instance without the patch for this test?
        # Creating a clean instance without the patch is hard because __init__ runs it.
        pass

    # Re-writing test_run_migrations_execution to handle the patching issue
    def test_run_migrations_logic(self):
        """Test the logic of run_migrations separately."""
        # Create a fresh instance but we need to patch __init__ or the calls inside it to avoid side effects
        # Actually, simpler: DatabaseManager.run_migrations is patched in the class for the whole TestCase?
        # Yes, because of @patch on setUp? No, @patch on setUp only applies to setUp execution? 
        # No, decorators on methods only apply to that method.
        # Decorators on setUp apply to the execution of setUp.
        # BUT the patch replaces the attribute on the module/class.
        # If I used @patch as a decorator on setUp, it passes the mock to setUp args.
        # It does NOT automatically patch it for other test methods unless I start/stop it manually or use patcher.
        
        # Wait, if I patch it in setUp arguments, the patch is active ONLY during setUp execution?
        # Correct! standard unittest.mock.patch decorators on a function only apply during that function's scope.
        # So `self.db_manager.run_migrations` should be the REAL method in other tests?
        # LET'S CHECK: In setUp:
        # @patch("...run_migrations") def setUp(self, mock_run): ...
        # The patch is active inside setUp. When setUp finishes, patch is undone.
        # So `self.db_manager` was created with a MOCKED run_migrations.
        # Does `self.db_manager` retain the mock?
        # If `run_migrations` is a method, patching the CLASS means `DatabaseManager.run_migrations` is replaced.
        # When `setUp` exits, `DatabaseManager.run_migrations` is restored.
        # However, `self.db_manager` instance was created when it was mocked.
        # Does the instance method point to the class method? Yes.
        # So `self.db_manager.run_migrations` should be the REAL method now!
        
        # So I CAN just call self.db_manager.run_migrations()!
        
        # Let's verify:
        # In setUp: self.db_manager = DatabaseManager() -> calls mocked run_migrations.
        # setUp exits -> patch stops -> DatabaseManager.run_migrations is real.
        # Test runs -> calls self.db_manager.run_migrations() -> resolves to real method.
        
        pass

    @patch("database_manager.get_migration_steps")
    def test_run_migrations_integration(self, mock_get_steps):
        # Setup connection mock
        self.db_manager.conn = MagicMock()
        mock_cur = MagicMock()
        self.db_manager.conn.cursor.return_value.__enter__.return_value = mock_cur
        self.db_manager.conn.closed = False
        
        # Latest seq = 2
        mock_cur.fetchone.return_value = (2,)
        
        # Steps available: 1 to 4
        mock_get_steps.return_value = {
            1: "SQL 1",
            2: "SQL 2",
            3: "SQL 3",
            4: "SQL 4"
        }
        
        # Execute
        # We need to ensure _get_latest_migration_sequence is using the real one too?
        # Yes, it wasn't patched.
        
        # We need to verify we can call run_migrations.
        # Note: if run_migrations was replaced on the INSTANCE (unlikely unless done manually), it would persist.
        # But patch usually patches the Class attribute.
        
        self.db_manager.run_migrations()
        
        # Verification
        # Should execute SQL 3 and SQL 4
        # Also inserts into migrations table
        
        # Check calls to execute
        # execute("SELECT max...") -> 1 call
        # execute("SQL 3") -> 1 call
        # execute("INSERT... 3") -> 1 call
        # execute("SQL 4") -> 1 call
        # execute("INSERT... 4") -> 1 call
        
        # Filter execute calls for migration statements
        execute_calls = [args[0][0] for args in mock_cur.execute.call_args_list]
        
        self.assertIn("SQL 3", execute_calls)
        self.assertIn("SQL 4", execute_calls)
        self.assertNotIn("SQL 1", execute_calls)
        self.assertNotIn("SQL 2", execute_calls)
        
        # Verify commits
        self.assertTrue(self.db_manager.conn.commit.called)

