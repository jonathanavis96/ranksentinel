"""Test schedule token generation, validation, and rotation."""

from datetime import datetime, timedelta, timezone

import pytest

from ranksentinel.db import (
    connect,
    create_schedule_token,
    execute,
    fetch_one,
    init_db,
    mark_schedule_token_used,
    update_customer_schedule,
    validate_schedule_token,
)


@pytest.fixture
def conn(tmp_path):
    """Create a temporary in-memory database for testing."""
    from ranksentinel.config import Settings

    settings = Settings(RANKSENTINEL_DB_PATH=":memory:")
    conn = connect(settings)
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def customer_id(conn):
    """Create a test customer."""
    ts = datetime.now(timezone.utc).isoformat()
    customer_id = execute(
        conn,
        "INSERT INTO customers(name,status,created_at,updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", ts, ts),
    )
    return customer_id


def test_create_schedule_token(conn, customer_id):
    """Test that schedule tokens are created correctly."""
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)

    # Token should be a URL-safe string
    assert isinstance(token, str)
    assert len(token) > 20  # secrets.token_urlsafe(32) produces ~43 chars

    # Token should be stored in database
    row = fetch_one(
        conn,
        "SELECT customer_id, token, expires_at, used_at FROM schedule_tokens WHERE token=?",
        (token,),
    )
    assert row is not None
    assert row["customer_id"] == customer_id
    assert row["token"] == token
    assert row["used_at"] is None


def test_validate_schedule_token_valid(conn, customer_id):
    """Test that valid tokens are validated correctly."""
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)

    # Should validate successfully
    result = validate_schedule_token(conn, token)
    assert result is not None
    assert result["customer_id"] == customer_id


def test_validate_schedule_token_expired(conn, customer_id):
    """Test that expired tokens are rejected."""
    # Create a token that expires in the past
    expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)

    # Should not validate
    result = validate_schedule_token(conn, token)
    assert result is None


def test_validate_schedule_token_used(conn, customer_id):
    """Test that used tokens are rejected."""
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)

    # Mark token as used
    mark_schedule_token_used(conn, token)

    # Should not validate anymore
    result = validate_schedule_token(conn, token)
    assert result is None


def test_validate_schedule_token_nonexistent(conn):
    """Test that nonexistent tokens are rejected."""
    result = validate_schedule_token(conn, "nonexistent_token_12345")
    assert result is None


def test_mark_schedule_token_used(conn, customer_id):
    """Test that tokens can be marked as used."""
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    token = create_schedule_token(conn, customer_id, expires_at)

    # Initially not used
    row = fetch_one(conn, "SELECT used_at FROM schedule_tokens WHERE token=?", (token,))
    assert row["used_at"] is None

    # Mark as used
    mark_schedule_token_used(conn, token)

    # Should now have used_at timestamp
    row = fetch_one(conn, "SELECT used_at FROM schedule_tokens WHERE token=?", (token,))
    assert row["used_at"] is not None


def test_update_customer_schedule(conn, customer_id):
    """Test that customer schedule preferences are updated correctly."""
    update_customer_schedule(
        conn,
        customer_id,
        digest_weekday=1,  # Tuesday
        digest_time_local="09:00",
        digest_timezone="America/New_York",
    )

    # Verify the schedule was saved
    row = fetch_one(
        conn,
        "SELECT digest_weekday, digest_time_local, digest_timezone FROM customers WHERE id=?",
        (customer_id,),
    )
    assert row["digest_weekday"] == 1
    assert row["digest_time_local"] == "09:00"
    assert row["digest_timezone"] == "America/New_York"


def test_token_rotation_workflow(conn, customer_id):
    """Test the complete token rotation workflow."""
    # 1. Create initial token
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    token1 = create_schedule_token(conn, customer_id, expires_at)

    # 2. Validate token1 (should work)
    result = validate_schedule_token(conn, token1)
    assert result is not None

    # 3. Use token1 to update schedule
    mark_schedule_token_used(conn, token1)
    update_customer_schedule(conn, customer_id, 1, "09:00", "America/New_York")

    # 4. token1 should no longer validate
    result = validate_schedule_token(conn, token1)
    assert result is None

    # 5. Create new token for next update
    token2 = create_schedule_token(conn, customer_id, expires_at)

    # 6. token2 should validate, token1 should not
    assert validate_schedule_token(conn, token2) is not None
    assert validate_schedule_token(conn, token1) is None


def test_multiple_tokens_per_customer(conn, customer_id):
    """Test that a customer can have multiple tokens (e.g., from different emails)."""
    expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    # Create multiple tokens
    token1 = create_schedule_token(conn, customer_id, expires_at)
    token2 = create_schedule_token(conn, customer_id, expires_at)

    # Both should be valid
    assert validate_schedule_token(conn, token1) is not None
    assert validate_schedule_token(conn, token2) is not None

    # Mark one as used
    mark_schedule_token_used(conn, token1)

    # Only token2 should be valid now
    assert validate_schedule_token(conn, token1) is None
    assert validate_schedule_token(conn, token2) is not None
