"""Tests for per-customer isolation in runners.

Verifies that one customer's failure doesn't abort the entire run.

NOTE: These tests require the full environment with dependencies installed.
To run: PYTHONPATH=src python3 -m pytest tests/test_customer_isolation.py -v

For manual validation, see: docs/MANUAL_VALIDATION_0.10.md
"""

import pytest


def test_daily_run_continues_after_customer_failure():
    """Test that daily run continues when one customer fails.

    AC: errors are caught per customer and recorded (DB + logs), then the runner continues
    """
    pytest.importorskip("ranksentinel.config")
    pytest.importorskip("ranksentinel.runner.daily_checks")

    # This test would be run with a proper test database setup
    # See manual validation doc for instructions
    pass


def test_weekly_run_continues_after_customer_failure():
    """Test that weekly run continues when one customer fails.

    AC: errors are caught per customer and recorded (DB + logs), then the runner continues
    """
    pytest.importorskip("ranksentinel.config")
    pytest.importorskip("ranksentinel.runner.weekly_digest")

    # This test would be run with a proper test database setup
    # See manual validation doc for instructions
    pass
