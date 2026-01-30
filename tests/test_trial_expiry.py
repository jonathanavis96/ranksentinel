"""Tests for trial expiry logic."""

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from ranksentinel.db import connect, execute, fetch_one, init_db
from ranksentinel.trial_expiry import check_and_expire_trials, manually_expire_trial


@pytest.fixture
def conn():
    """Create an in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


def create_trial_customer(conn, trial_started_at=None, weekly_digest_sent_count=0):
    """Helper to create a trial customer with specified attributes."""
    now = datetime.now(timezone.utc).isoformat()
    email = f"test-{datetime.now().timestamp()}@example.com"
    
    customer_id = execute(
        conn,
        """INSERT INTO customers(
            name, email_raw, email_canonical, status, 
            trial_started_at, weekly_digest_sent_count,
            created_at, updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (email, email, email, "trial", trial_started_at, weekly_digest_sent_count, now, now),
    )
    return customer_id


def test_trial_expires_after_7_days(conn):
    """Test that trial expires after 7 days."""
    now = datetime.now(timezone.utc)
    eight_days_ago = (now - timedelta(days=8)).isoformat()
    
    # Create trial customer with trial_started_at 8 days ago
    customer_id = create_trial_customer(conn, trial_started_at=eight_days_ago)
    
    # Run expiry check
    expired_ids = check_and_expire_trials(conn)
    
    # Verify customer was expired
    assert customer_id in expired_ids
    
    # Verify status changed to paywalled
    customer = fetch_one(conn, "SELECT status, paywalled_since FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "paywalled"
    assert customer["paywalled_since"] is not None


def test_trial_does_not_expire_before_7_days(conn):
    """Test that trial does not expire before 7 days if no digest sent."""
    now = datetime.now(timezone.utc)
    five_days_ago = (now - timedelta(days=5)).isoformat()
    
    # Create trial customer with trial_started_at 5 days ago
    customer_id = create_trial_customer(conn, trial_started_at=five_days_ago, weekly_digest_sent_count=0)
    
    # Run expiry check
    expired_ids = check_and_expire_trials(conn)
    
    # Verify customer was NOT expired
    assert customer_id not in expired_ids
    
    # Verify status is still trial
    customer = fetch_one(conn, "SELECT status FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "trial"


def test_trial_expires_after_one_weekly_digest(conn):
    """Test that trial expires after 1 weekly digest, even if less than 7 days."""
    now = datetime.now(timezone.utc)
    two_days_ago = (now - timedelta(days=2)).isoformat()
    
    # Create trial customer with 1 weekly digest sent
    customer_id = create_trial_customer(conn, trial_started_at=two_days_ago, weekly_digest_sent_count=1)
    
    # Run expiry check
    expired_ids = check_and_expire_trials(conn)
    
    # Verify customer was expired
    assert customer_id in expired_ids
    
    # Verify status changed to paywalled
    customer = fetch_one(conn, "SELECT status, paywalled_since FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "paywalled"
    assert customer["paywalled_since"] is not None


def test_expiry_is_idempotent(conn):
    """Test that running expiry check multiple times doesn't cause issues."""
    now = datetime.now(timezone.utc)
    eight_days_ago = (now - timedelta(days=8)).isoformat()
    
    # Create trial customer
    customer_id = create_trial_customer(conn, trial_started_at=eight_days_ago)
    
    # Run expiry check twice
    expired_ids_first = check_and_expire_trials(conn)
    expired_ids_second = check_and_expire_trials(conn)
    
    # First run should expire the customer
    assert customer_id in expired_ids_first
    
    # Second run should not report it again (already paywalled)
    assert customer_id not in expired_ids_second
    
    # Verify status is paywalled
    customer = fetch_one(conn, "SELECT status FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "paywalled"


def test_only_trial_customers_are_expired(conn):
    """Test that only customers with status='trial' are affected."""
    now = datetime.now(timezone.utc)
    eight_days_ago = (now - timedelta(days=8)).isoformat()
    
    # Create active customer with old trial_started_at
    active_customer_id = execute(
        conn,
        """INSERT INTO customers(
            name, email_raw, email_canonical, status, 
            trial_started_at, created_at, updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        ("active@example.com", "active@example.com", "active@example.com", 
         "active", eight_days_ago, now, now),
    )
    
    # Run expiry check
    expired_ids = check_and_expire_trials(conn)
    
    # Verify active customer was NOT expired
    assert active_customer_id not in expired_ids
    
    # Verify status is still active
    customer = fetch_one(conn, "SELECT status FROM customers WHERE id=?", (active_customer_id,))
    assert customer["status"] == "active"


def test_manual_expire_trial(conn):
    """Test manually expiring a trial customer."""
    now = datetime.now(timezone.utc)
    two_days_ago = (now - timedelta(days=2)).isoformat()
    
    # Create trial customer (not yet expired by automatic rules)
    customer_id = create_trial_customer(conn, trial_started_at=two_days_ago, weekly_digest_sent_count=0)
    
    # Manually expire
    result = manually_expire_trial(conn, customer_id)
    
    # Verify it was transitioned
    assert result is True
    
    # Verify status changed to paywalled
    customer = fetch_one(conn, "SELECT status, paywalled_since FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "paywalled"
    assert customer["paywalled_since"] is not None


def test_manual_expire_non_trial_customer_fails(conn):
    """Test that manually expiring a non-trial customer returns False."""
    now = datetime.now(timezone.utc).isoformat()
    
    # Create active customer
    customer_id = execute(
        conn,
        """INSERT INTO customers(
            name, email_raw, email_canonical, status, 
            created_at, updated_at
        ) VALUES(?,?,?,?,?,?)""",
        ("active@example.com", "active@example.com", "active@example.com", 
         "active", now, now),
    )
    
    # Try to manually expire
    result = manually_expire_trial(conn, customer_id)
    
    # Verify it was NOT transitioned
    assert result is False
    
    # Verify status is still active
    customer = fetch_one(conn, "SELECT status FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "active"


def test_trial_expiry_sets_paywalled_since_timestamp(conn):
    """Test that paywalled_since is set when trial expires."""
    now = datetime.now(timezone.utc)
    eight_days_ago = (now - timedelta(days=8)).isoformat()
    
    # Create trial customer
    customer_id = create_trial_customer(conn, trial_started_at=eight_days_ago)
    
    # Run expiry check
    check_and_expire_trials(conn)
    
    # Verify paywalled_since is set and recent
    customer = fetch_one(conn, "SELECT paywalled_since FROM customers WHERE id=?", (customer_id,))
    assert customer["paywalled_since"] is not None
    
    # Parse timestamp and verify it's recent (within last minute)
    paywalled_since = datetime.fromisoformat(customer["paywalled_since"])
    time_diff = now - paywalled_since.replace(tzinfo=timezone.utc)
    assert time_diff.total_seconds() < 60


def test_trial_without_started_at_not_expired(conn):
    """Test that trial customers without trial_started_at are not expired."""
    # Create trial customer without trial_started_at
    customer_id = create_trial_customer(conn, trial_started_at=None, weekly_digest_sent_count=0)
    
    # Run expiry check
    expired_ids = check_and_expire_trials(conn)
    
    # Verify customer was NOT expired
    assert customer_id not in expired_ids
    
    # Verify status is still trial
    customer = fetch_one(conn, "SELECT status FROM customers WHERE id=?", (customer_id,))
    assert customer["status"] == "trial"
