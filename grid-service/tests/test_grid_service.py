import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import grid_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grid_service

@pytest.fixture
def mock_db_env(monkeypatch, tmp_path):
    password_file = tmp_path / "db_password"
    password_file.write_text("secret_password")
    
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER_NAME", "user")
    monkeypatch.setenv("DB_PASSWORD_FILE", str(password_file))

def test_get_db_connection_info(mock_db_env):
    conn_info, db_name = grid_service.get_db_connection_info()
    assert "password=secret_password" in conn_info
    assert "host=localhost" in conn_info
    assert db_name == "test_db"

@patch("psycopg.connect")
def test_run_migrations_no_previous_migrations(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    
    # Mock finding max sequence - returns None for first run
    mock_cur.fetchone.return_value = (None,)
    
    grid_service.run_migrations(mock_conn, "test_db")
    
    # Verify execute was called for migrations
    # We can check if it attempted to insert into migrations table
    assert mock_cur.execute.call_count > 0
    # Check that it tried to commit
    assert mock_conn.commit.called

@patch("psycopg.connect")
def test_run_migrations_up_to_date(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    
    # Mock finding max sequence - let's say it matches the highest in migrationSteps
    # We need to know the max key in migrationSteps
    from migration_steps import migration_steps
    max_seq = max(migration_steps.keys()) if migration_steps else 0
    
    mock_cur.fetchone.return_value = (max_seq,)
    
    grid_service.run_migrations(mock_conn, "test_db")
    
    # Verify no INSERT INTO migrations happened for new migrations
    # This is a bit loose, but we check that we didn't execute migration statements
    # We can inspect the calls to execute
    for call in mock_cur.execute.call_args_list:
        args = call[0]
        statement = args[0]
        if "INSERT INTO migrations" in statement:
             # Should not happen if up to date
             assert False, "Should not run migrations if up to date"

