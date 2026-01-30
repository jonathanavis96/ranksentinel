"""Test paywall email cadence logic."""

from datetime import datetime, timedelta, timezone

import pytest

from ranksentinel.db import connect, execute, fetch_one, init_db
from ranksentinel.paywall_cadence import (
    increment_digest_count_and_check_transition,
    should_send_paywall_digest,
)


@pytest.fixture
def conn():
    """Create in-memory database for testing."""
    import sqlite3
    db_conn = sqlite3.connect(":memory:")
    db_conn.row_factory = sqlite3.Row
    init_db(db_conn)
    yield db_conn
    db_conn.close()


def create_paywalled_customer(
    conn,
    weekly_digest_sent_count=0,
    paywalled_since=None,
    digest_weekday=1,  # Tuesday
):
    """Create a paywalled customer for testing."""
    now = datetime.now(timezone.utc).isoformat()
    if paywalled_since is None:
        paywalled_since = now

    email = f"test_{now}@example.com"
    execute(
        conn,
        """
        INSERT INTO customers
        (name, email_raw, email_canonical, status, weekly_digest_sent_count,
         paywalled_since, digest_weekday, digest_time_local, digest_timezone,
         created_at, updated_at)
        VALUES (?, ?, ?, 'paywalled', ?, ?, ?, '09:00', 'UTC', ?, ?)
        """,
        (email, email, email, weekly_digest_sent_count, paywalled_since, digest_weekday, now, now),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def create_previously_interested_customer(
    conn,
    digest_weekday=1,
    weekly_digest_sent_count=4,
):
    """Create a previously_interested customer for testing."""
    now = datetime.now(timezone.utc).isoformat()
    paywalled_since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    email = f"test_{now}@example.com"
    execute(
        conn,
        """
        INSERT INTO customers
        (name, email_raw, email_canonical, status, weekly_digest_sent_count,
         paywalled_since, digest_weekday, digest_time_local, digest_timezone,
         created_at, updated_at)
        VALUES (?, ?, ?, 'previously_interested', ?, ?, ?, '09:00', 'UTC', ?, ?)
        """,
        (email, email, email, weekly_digest_sent_count, paywalled_since, digest_weekday, now, now),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def insert_email_log(conn, customer_id, sent_at, run_type="weekly"):
    """Insert delivery entry."""
    execute(
        conn,
        """
        INSERT INTO deliveries
        (customer_id, run_type, recipient, subject, sent_at, provider, status)
        VALUES (?, ?, 'test@example.com', 'Test Subject', ?, 'mailgun', 'sent')
        """,
        (customer_id, run_type, sent_at),
    )


def test_paywalled_should_send_first_digest(conn):
    """Test that paywalled customer with 0 digests sent should receive email."""
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=0)

    should_send, reason = should_send_paywall_digest(conn, customer_id)

    assert should_send is True
    assert reason == "paywalled_weekly"


def test_paywalled_should_send_up_to_4_digests(conn):
    """Test that paywalled customer can receive up to 4 digests."""
    now = datetime.now(timezone.utc)

    for count in range(4):
        customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=count)

        # Simulate previous email if count > 0
        if count > 0:
            last_sent = (now - timedelta(days=7)).isoformat()
            insert_email_log(conn, customer_id, last_sent)

        should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

        assert should_send is True, f"Should send digest #{count + 1}"
        assert reason == "paywalled_weekly"


def test_paywalled_stops_after_4_digests(conn):
    """Test that paywalled customer stops receiving digests after 4 sends."""
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=4)

    should_send, reason = should_send_paywall_digest(conn, customer_id)

    assert should_send is False
    assert reason == "paywalled_max_4_reached"


def test_paywalled_respects_weekly_cadence(conn):
    """Test that paywalled customer can't receive digest before 7 days."""
    now = datetime.now(timezone.utc)
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=1)

    # Last email sent 5 days ago
    last_sent = (now - timedelta(days=5)).isoformat()
    insert_email_log(conn, customer_id, last_sent)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    assert should_send is False
    assert "paywalled_too_soon_days=5" in reason


def test_paywalled_can_send_after_7_days(conn):
    """Test that paywalled customer can receive digest after 7 days."""
    now = datetime.now(timezone.utc)
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=1)

    # Last email sent 7 days ago
    last_sent = (now - timedelta(days=7)).isoformat()
    insert_email_log(conn, customer_id, last_sent)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    assert should_send is True
    assert reason == "paywalled_weekly"


def test_increment_digest_count(conn):
    """Test incrementing digest count."""
    now = datetime.now(timezone.utc)
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=0)

    transitioned = increment_digest_count_and_check_transition(conn, customer_id, current_time=now)

    assert transitioned is False

    customer = fetch_one(
        conn, "SELECT weekly_digest_sent_count FROM customers WHERE id=?", (customer_id,)
    )
    assert customer["weekly_digest_sent_count"] == 1


def test_transition_to_previously_interested_after_4_digests(conn):
    """Test that customer transitions to previously_interested after 4 digests."""
    now = datetime.now(timezone.utc)
    customer_id = create_paywalled_customer(conn, weekly_digest_sent_count=3)

    # Send 4th digest
    transitioned = increment_digest_count_and_check_transition(conn, customer_id, current_time=now)

    assert transitioned is True

    customer = fetch_one(
        conn, "SELECT status, weekly_digest_sent_count FROM customers WHERE id=?", (customer_id,)
    )
    assert customer["status"] == "previously_interested"
    assert customer["weekly_digest_sent_count"] == 4


def test_increment_is_idempotent(conn):
    """Test that incrementing for non-paywalled customer is safe."""
    now = datetime.now(timezone.utc)
    customer_id = create_previously_interested_customer(conn)

    transitioned = increment_digest_count_and_check_transition(conn, customer_id, current_time=now)

    assert transitioned is False

    customer = fetch_one(
        conn, "SELECT weekly_digest_sent_count FROM customers WHERE id=?", (customer_id,)
    )
    # Should not increment for non-paywalled customer
    assert customer["weekly_digest_sent_count"] == 4


def test_previously_interested_monthly_not_yet_time(conn):
    """Test that previously_interested customer waits for monthly schedule."""
    # Set current time to 2nd of month, target weekday to 10th
    now = datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc)  # Thursday Jan 2
    # Set digest weekday to Monday (0) - first Monday of month is Jan 5
    target_weekday = 0  # Monday

    customer_id = create_previously_interested_customer(conn, digest_weekday=target_weekday)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    assert should_send is False
    assert "previously_interested_waiting_until" in reason


def test_previously_interested_monthly_send_on_schedule(conn):
    """Test that previously_interested customer sends on scheduled weekday."""
    now = datetime.now(timezone.utc)
    # Set to current weekday and we're past the 1st of the month
    current_weekday = now.weekday()

    customer_id = create_previously_interested_customer(conn, digest_weekday=current_weekday)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    # Should send if we haven't sent this month yet
    assert should_send is True
    assert reason == "previously_interested_monthly"


def test_previously_interested_already_sent_this_month(conn):
    """Test that previously_interested customer doesn't send twice in same month."""
    now = datetime.now(timezone.utc)
    current_weekday = now.weekday()

    customer_id = create_previously_interested_customer(conn, digest_weekday=current_weekday)

    # Simulate email sent 10 days ago (same month)
    last_sent = (now - timedelta(days=10)).isoformat()
    insert_email_log(conn, customer_id, last_sent)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    assert should_send is False
    assert reason == "previously_interested_already_sent_this_month"


def test_previously_interested_can_send_next_month(conn):
    """Test that previously_interested customer can send in next month."""
    now = datetime.now(timezone.utc)
    current_weekday = now.weekday()

    customer_id = create_previously_interested_customer(conn, digest_weekday=current_weekday)

    # Simulate email sent last month (35 days ago)
    last_sent = (now - timedelta(days=35)).isoformat()
    insert_email_log(conn, customer_id, last_sent)

    should_send, reason = should_send_paywall_digest(conn, customer_id, current_time=now)

    assert should_send is True
    assert reason == "previously_interested_monthly"


def test_active_customer_not_affected(conn):
    """Test that active customer is not checked by paywall cadence."""
    now = datetime.now(timezone.utc).isoformat()
    email = f"active_{now}@example.com"

    execute(
        conn,
        """
        INSERT INTO customers
        (name, email_raw, email_canonical, status, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?)
        """,
        (email, email, email, now, now),
    )
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    should_send, reason = should_send_paywall_digest(conn, customer_id)

    assert should_send is False
    assert reason == "status=active"
