"""Tests for First Insight admin endpoint."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException

from ranksentinel.api import send_first_insight
from ranksentinel.db import execute


def test_send_first_insight_success(db_conn):
    """Test successful First Insight trigger for existing customer."""
    # Create a customer
    customer_id = execute(
        db_conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    db_conn.commit()
    
    # Mock the service function (imported dynamically in the endpoint)
    with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
        result = send_first_insight(customer_id=customer_id, conn=db_conn)
    
    # Verify response
    assert result["status"] == "ok"
    assert "First Insight report triggered" in result["message"]
    
    # Verify service was called with correct parameters
    mock_trigger.assert_called_once()
    call_args = mock_trigger.call_args
    assert call_args[0][0] == db_conn
    assert call_args[0][1] == customer_id


def test_send_first_insight_customer_not_found(db_conn):
    """Test First Insight trigger fails for non-existent customer."""
    with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
        with pytest.raises(HTTPException) as exc_info:
            send_first_insight(customer_id=999, conn=db_conn)
    
    # Verify 404 exception
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "customer not found"
    
    # Verify service was NOT called
    mock_trigger.assert_not_called()


def test_send_first_insight_canceled_customer(db_conn):
    """Test First Insight can be triggered even for canceled customers (admin override)."""
    # Create a canceled customer
    customer_id = execute(
        db_conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("Canceled Customer", "canceled", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    db_conn.commit()
    
    # Mock the service function
    with patch("ranksentinel.runner.first_insight.trigger_first_insight_report") as mock_trigger:
        result = send_first_insight(customer_id=customer_id, conn=db_conn)
    
    # Admin endpoint should work regardless of customer status
    assert result["status"] == "ok"
    mock_trigger.assert_called_once()
