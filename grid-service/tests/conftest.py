import os
import pytest
import sys

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Fixture to set up common environment variables for testing.
    """
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER_NAME", "test_user")
    
    # We'll need to mock password file paths, usually we'll mock the _read_password_file method
    # but for integration-like tests we might need these.
    monkeypatch.setenv("DB_PASSWORD_FILE", "/tmp/db_pass")
    monkeypatch.setenv("ROOT_PASSWORD_FILE", "/tmp/root_pass")
    monkeypatch.setenv("RABBITMQ_PASSWORD_FILE", "/tmp/rmq_pass")
    
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_PORT", "5672")
    monkeypatch.setenv("RABBITMQ_USER", "guest")

