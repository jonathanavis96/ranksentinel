"""Tests for POST /public/schedule endpoint."""

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from ranksentinel.api import app
from ranksentinel.db import connect, init_db, create_schedule_token


@pytest.fixture
def client_and_conn(tmp_path):
    """Create test client with temporary database and connection."""
    db_path = tmp_path / "test.db"
    
    # Override get_conn dependency
    def override_get_conn():
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        init_db(conn)
        try:
            yield conn
        finally:
            conn.close()

    from ranksentinel.api import get_conn
    app.dependency_overrides[get_conn] = override_get_conn

    # Create a connection for test setup
    setup_conn = sqlite3.connect(str(db_path), check_same_thread=False)
    setup_conn.row_factory = sqlite3.Row
    init_db(setup_conn)
    
    yield TestClient(app), setup_conn

    setup_conn.close()
    app.dependency_overrides.clear()


def test_schedule_update_success(client_and_conn):
    """Test successful schedule update with valid token."""
    client, conn = client_and_conn
    
    # Create a customer with schedule token
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        ("test@example.com", "test@example.com", "test@example.com", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.commit()
    
    # Create a valid schedule token
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)
    
    # Make request
    response = client.post(
        "/public/schedule",
        json={
            "token": token,
            "digest_weekday": 1,  # Tuesday
            "digest_time_local": "09:00",
            "digest_timezone": "America/New_York",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["message"] == "Schedule updated successfully"
    assert data["timezone"] == "America/New_York"
    assert data["utc_offset_minutes"] == -300  # EST offset
    assert "next_run_at_utc" in data
    assert "next_run_at_local" in data
    
    # Verify next_run is a valid ISO timestamp
    next_run_utc = datetime.fromisoformat(data["next_run_at_utc"])
    next_run_local = datetime.fromisoformat(data["next_run_at_local"])
    
    # Verify the local time is Tuesday at 09:00
    assert next_run_local.weekday() == 1  # Tuesday
    assert next_run_local.hour == 9
    assert next_run_local.minute == 0
    
    # Verify database was updated
    cursor.execute(
        "SELECT digest_weekday, digest_time_local, digest_timezone FROM customers WHERE id=?",
        (customer_id,),
    )
    row = cursor.fetchone()
    assert row["digest_weekday"] == 1
    assert row["digest_time_local"] == "09:00"
    assert row["digest_timezone"] == "America/New_York"


def test_schedule_update_invalid_token(client_and_conn):
    """Test schedule update with invalid token."""
    client, conn = client_and_conn
    
    response = client.post(
        "/public/schedule",
        json={
            "token": "invalid-token",
            "digest_weekday": 1,
            "digest_time_local": "09:00",
            "digest_timezone": "America/New_York",
        },
    )
    
    assert response.status_code == 404
    assert "Invalid or expired token" in response.json()["detail"]


def test_schedule_update_invalid_timezone(client_and_conn):
    """Test schedule update with invalid timezone."""
    client, conn = client_and_conn
    
    # Create a customer with schedule token
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        ("test@example.com", "test@example.com", "test@example.com", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.commit()
    
    # Create a valid schedule token
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)
    
    response = client.post(
        "/public/schedule",
        json={
            "token": token,
            "digest_weekday": 1,
            "digest_time_local": "09:00",
            "digest_timezone": "Invalid/Timezone",
        },
    )
    
    assert response.status_code == 400
    assert "Invalid timezone" in response.json()["detail"]


def test_schedule_update_invalid_time_format(client_and_conn):
    """Test schedule update with invalid time format."""
    client, conn = client_and_conn
    
    # Create a customer with schedule token
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        ("test@example.com", "test@example.com", "test@example.com", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.commit()
    
    # Create a valid schedule token
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)
    
    # Test with invalid time (out of range)
    response = client.post(
        "/public/schedule",
        json={
            "token": token,
            "digest_weekday": 1,
            "digest_time_local": "25:00",  # Invalid hour
            "digest_timezone": "America/New_York",
        },
    )
    
    assert response.status_code == 400
    assert "Invalid time format" in response.json()["detail"]


def test_schedule_update_dst_aware(client_and_conn):
    """Test that schedule calculation is DST-aware."""
    client, conn = client_and_conn
    
    # Create a customer with schedule token
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        ("test@example.com", "test@example.com", "test@example.com", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.commit()
    
    # Create a valid schedule token
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)
    
    response = client.post(
        "/public/schedule",
        json={
            "token": token,
            "digest_weekday": 1,  # Tuesday
            "digest_time_local": "09:00",
            "digest_timezone": "America/New_York",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # The UTC offset should be calculated for the next run time, not current time
    # This ensures DST transitions are handled correctly
    next_run_local = datetime.fromisoformat(data["next_run_at_local"])
    tz = ZoneInfo("America/New_York")
    expected_offset = int(next_run_local.utcoffset().total_seconds() / 60)
    
    assert data["utc_offset_minutes"] == expected_offset


def test_schedule_update_weekday_validation(client_and_conn):
    """Test schedule update with invalid weekday."""
    client, conn = client_and_conn
    
    response = client.post(
        "/public/schedule",
        json={
            "token": "test-token-123",
            "digest_weekday": 7,  # Invalid (should be 0-6)
            "digest_time_local": "09:00",
            "digest_timezone": "America/New_York",
        },
    )
    
    # Should fail Pydantic validation
    assert response.status_code == 422
