"""Integration test for First Insight email delivery."""

import sqlite3
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from ranksentinel.db import execute, init_db
from ranksentinel.runner.first_insight import trigger_first_insight_report


@pytest.fixture
def test_conn():
    """Create an in-memory test database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    # Insert test customer with timestamps
    now = datetime.now(timezone.utc).isoformat()
    execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("Test Customer", "active", now, now),
    )

    # Insert test settings with sitemap
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (1, "https://example.com/sitemap.xml", 10),
    )

    yield conn
    conn.close()


def test_first_insight_email_sent_with_mailgun(test_conn):
    """Test that first insight email is sent and delivery is logged."""
    # Mock Mailgun client
    mock_client = MagicMock()
    mock_client.send_email.return_value = (True, "test-message-id-123", None)

    # Trigger first insight with email
    result = trigger_first_insight_report(
        test_conn,
        customer_id=1,
        mailgun_client=mock_client,
        recipient_email="test@example.com",
    )

    # Verify email was sent
    assert result["email_sent"] is True
    assert "email_error" not in result

    # Verify Mailgun client was called
    mock_client.send_email.assert_called_once()
    call_kwargs = mock_client.send_email.call_args[1]
    assert call_kwargs["to"] == "test@example.com"
    assert "First" in call_kwargs["subject"] and "Insight" in call_kwargs["subject"]

    # Verify delivery was logged
    cursor = test_conn.execute(
        "SELECT * FROM deliveries WHERE customer_id=? AND run_type='first_insight'",
        (1,),
    )
    deliveries = cursor.fetchall()
    assert len(deliveries) == 1

    delivery = deliveries[0]
    assert delivery["status"] == "sent"
    assert delivery["provider_message_id"] == "test-message-id-123"
    assert delivery["recipient"] == "test@example.com"
    assert "First" in delivery["subject"] and "Insight" in delivery["subject"]


def test_first_insight_email_idempotency(test_conn):
    """Test that only one email is sent per customer per day."""
    # Mock Mailgun client
    mock_client = MagicMock()
    mock_client.send_email.return_value = (True, "test-message-id-1", None)

    # First call - should send email
    result1 = trigger_first_insight_report(
        test_conn,
        customer_id=1,
        mailgun_client=mock_client,
        recipient_email="test@example.com",
    )

    assert result1["email_sent"] is True
    assert mock_client.send_email.call_count == 1

    # Second call same day - should skip email
    mock_client.send_email.return_value = (True, "test-message-id-2", None)
    result2 = trigger_first_insight_report(
        test_conn,
        customer_id=1,
        mailgun_client=mock_client,
        recipient_email="test@example.com",
    )

    assert result2["email_sent"] is False
    assert result2["dedupe_reason"] == "Already sent today"
    assert mock_client.send_email.call_count == 1  # Not called again

    # Verify only one delivery in database
    cursor = test_conn.execute(
        "SELECT COUNT(*) as count FROM deliveries WHERE customer_id=? AND run_type='first_insight' AND DATE(sent_at) = DATE(?)",
        (1, datetime.now(timezone.utc).date().isoformat()),
    )
    count = cursor.fetchone()["count"]
    assert count == 1


def test_first_insight_email_without_mailgun(test_conn):
    """Test that first insight works without Mailgun client (no email sent)."""
    # Trigger without mailgun_client
    result = trigger_first_insight_report(
        test_conn,
        customer_id=1,
        mailgun_client=None,
        recipient_email=None,
    )

    # Verify report was generated but no email sent
    assert result["email_sent"] is False
    assert "findings_count" in result
    assert "report" in result

    # Verify no delivery logged
    cursor = test_conn.execute(
        "SELECT COUNT(*) as count FROM deliveries WHERE customer_id=? AND run_type='first_insight'",
        (1,),
    )
    count = cursor.fetchone()["count"]
    assert count == 0


def test_first_insight_email_failure_logged(test_conn):
    """Test that email failures are logged properly."""
    # Mock Mailgun client with failure
    mock_client = MagicMock()
    mock_client.send_email.return_value = (False, None, "Mailgun API error 500")

    # Trigger first insight
    result = trigger_first_insight_report(
        test_conn,
        customer_id=1,
        mailgun_client=mock_client,
        recipient_email="test@example.com",
    )

    # Verify email was attempted but failed
    assert result["email_sent"] is False

    # Verify delivery was logged with failure status
    cursor = test_conn.execute(
        "SELECT * FROM deliveries WHERE customer_id=? AND run_type='first_insight'",
        (1,),
    )
    deliveries = cursor.fetchall()
    assert len(deliveries) == 1

    delivery = deliveries[0]
    assert delivery["status"] == "failed"
    assert delivery["error"] == "Mailgun API error 500"
    assert delivery["provider_message_id"] is None
