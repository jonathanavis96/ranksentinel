"""Test payment integration hook for First Insight."""

import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from ranksentinel.api import trigger_first_insight_for_customer
from ranksentinel.config import Settings
from ranksentinel.db import init_db


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        RANKSENTINEL_DB_PATH=":memory:",
        MAILGUN_API_KEY="test-key",
        MAILGUN_DOMAIN="test.example.com",
        MAILGUN_FROM="test@example.com",
        MAILGUN_TO="customer@example.com",
        PSI_API_KEY="test-psi-key",
    )


def test_trigger_first_insight_for_customer_exists(test_db, test_settings):
    """Test that trigger_first_insight_for_customer function exists and is callable."""
    # Create a test customer
    cursor = test_db.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("Test Customer", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    test_db.commit()
    
    # Add a target URL
    test_db.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES(?, ?, ?, ?)",
        (customer_id, "https://example.com", 1, "2026-01-01T00:00:00Z"),
    )
    test_db.commit()
    
    # Mock the actual first insight execution (we're just testing the hook exists)
    with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
        mock_trigger.return_value = {
            "run_id": "test-run-123",
            "customer_id": customer_id,
            "findings_count": 5,
            "email_sent": True,
        }
        
        # Call the hook function
        result = trigger_first_insight_for_customer(customer_id, test_db, test_settings)
        
        # Verify it was called
        assert mock_trigger.called
        assert result["customer_id"] == customer_id
        assert result["email_sent"] is True


def test_trigger_first_insight_for_customer_invalid_customer(test_db, test_settings):
    """Test that trigger_first_insight_for_customer raises ValueError for invalid customer."""
    # Try to trigger for non-existent customer
    with pytest.raises(ValueError, match="Customer 999 not found"):
        trigger_first_insight_for_customer(999, test_db, test_settings)


def test_webhook_handler_can_call_hook(test_db, test_settings):
    """Test that a webhook handler can successfully call the hook."""
    # Simulate a payment webhook handler calling the hook
    def simulated_payment_webhook_handler(stripe_customer_id: str, conn, settings):
        """Simulated future Stripe webhook handler."""
        # In real implementation, would map stripe_customer_id to internal customer_id
        # For this test, we'll just use a direct customer_id
        customer_id = 1
        
        # Create customer
        conn.execute(
            "INSERT INTO customers(id, name, status, created_at, updated_at) VALUES(?, ?, ?, ?, ?)",
            (customer_id, "Paid Customer", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        )
        conn.commit()
        
        # Add target
        conn.execute(
            "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES(?, ?, ?, ?)",
            (customer_id, "https://example.com", 1, "2026-01-01T00:00:00Z"),
        )
        conn.commit()
        
        # Call the hook (this is the key integration point)
        with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
            mock_trigger.return_value = {
                "run_id": "webhook-run-456",
                "customer_id": customer_id,
                "findings_count": 3,
                "email_sent": True,
            }
            
            result = trigger_first_insight_for_customer(customer_id, conn, settings)
            return result
    
    # Execute simulated webhook
    result = simulated_payment_webhook_handler("stripe_cus_test123", test_db, test_settings)
    
    # Verify the hook was called successfully
    assert result["customer_id"] == 1
    assert result["run_id"] == "webhook-run-456"
    assert result["email_sent"] is True


def test_trigger_first_insight_for_customer_without_mailgun(test_db):
    """Test that hook works without Mailgun configured."""
    # Create settings without Mailgun
    settings_no_mailgun = Settings(
        RANKSENTINEL_DB_PATH=":memory:",
        MAILGUN_API_KEY="",
        MAILGUN_DOMAIN="",
        MAILGUN_FROM="",
        MAILGUN_TO="",
        PSI_API_KEY="",
    )
    
    # Create customer
    cursor = test_db.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("No Email Customer", "active", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    test_db.commit()
    
    # Add target
    test_db.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES(?, ?, ?, ?)",
        (customer_id, "https://example.com", 1, "2026-01-01T00:00:00Z"),
    )
    test_db.commit()
    
    # Mock the trigger
    with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
        mock_trigger.return_value = {
            "run_id": "no-email-run-789",
            "customer_id": customer_id,
            "findings_count": 2,
            "email_sent": False,
        }
        
        result = trigger_first_insight_for_customer(customer_id, test_db, settings_no_mailgun)
        
        # Should work without email
        assert result["customer_id"] == customer_id
        assert result["email_sent"] is False
