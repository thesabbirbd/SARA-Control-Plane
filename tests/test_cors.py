import pytest
import os
import sqlite3
import tempfile
from fastapi.testclient import TestClient

# Mock environment variables before importing app
os.environ["SARA_CORS_ORIGINS"] = "http://example.com,http://test.com"

# Create a temporary file for the database
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
os.environ["SARA_DB_PATH"] = temp_db_path

from app.api import app

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            status TEXT,
            created_at TEXT,
            workflow_id TEXT,
            instruction TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_active_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    yield
    os.close(temp_db_fd)
    os.remove(temp_db_path)

client = TestClient(app)

def test_cors_middleware_allowed_origin():
    """Test that CORS headers are applied for allowed origins."""
    response = client.options(
        "/api/tasks",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Example",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_cors_headers_on_get_allowed_origin():
    """Test that GET requests from allowed origin return the correct CORS headers."""
    response = client.get(
        "/api/tasks",
        headers={"Origin": "http://example.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://example.com"

def test_cors_middleware_disallowed_origin():
    """Test that CORS headers are not applied or deny for disallowed origins."""
    response = client.options(
        "/api/tasks",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # FastAPI/Starlette CORS returns 400 for disallowed preflight requests
    assert response.status_code == 400
