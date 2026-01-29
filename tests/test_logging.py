"""Tests for structured logging utilities."""
import re
from io import StringIO
from unittest.mock import patch

from ranksentinel.runner.logging_utils import (
    generate_run_id,
    log_stage,
    log_structured,
    log_summary,
)


def test_generate_run_id():
    """Test run_id generation produces valid UUID."""
    run_id = generate_run_id()
    assert run_id
    # UUID v4 format check
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    assert re.match(uuid_pattern, run_id, re.IGNORECASE)


def test_log_structured():
    """Test structured logging output format."""
    run_id = "test-run-123"
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        log_structured(run_id, customer_id=1, stage="test", status="start")
        output = mock_stdout.getvalue()
    
    # Check all expected fields are present
    assert "run_id=test-run-123" in output
    assert "customer_id=1" in output
    assert "stage=test" in output
    assert "status=start" in output


def test_log_summary():
    """Test SUMMARY line format."""
    run_id = "test-run-456"
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        log_summary(run_id, "daily", 10, 8, 2, 5000)
        output = mock_stdout.getvalue()
    
    # Must start with SUMMARY
    assert output.startswith("SUMMARY")
    
    # Check all required fields
    assert "run_id=test-run-456" in output
    assert "run_type=daily" in output
    assert "total_customers=10" in output
    assert "succeeded=8" in output
    assert "failed=2" in output
    assert "elapsed_ms=5000" in output


def test_log_stage_success():
    """Test log_stage context manager for successful execution."""
    run_id = "test-run-789"
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        with log_stage(run_id, "test_stage", customer_id=1):
            pass  # Simulate successful work
        output = mock_stdout.getvalue()
    
    lines = output.strip().split("\n")
    assert len(lines) == 2
    
    # Start line
    assert "run_id=test-run-789" in lines[0]
    assert "stage=test_stage" in lines[0]
    assert "status=start" in lines[0]
    assert "customer_id=1" in lines[0]
    
    # Complete line
    assert "run_id=test-run-789" in lines[1]
    assert "stage=test_stage" in lines[1]
    assert "status=complete" in lines[1]
    assert "elapsed_ms=" in lines[1]
    assert "customer_id=1" in lines[1]


def test_log_stage_error():
    """Test log_stage context manager captures errors."""
    run_id = "test-run-error"
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        try:
            with log_stage(run_id, "failing_stage", customer_id=2):
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected
        
        output = mock_stdout.getvalue()
    
    lines = output.strip().split("\n")
    assert len(lines) == 2
    
    # Error line
    assert "run_id=test-run-error" in lines[1]
    assert "stage=failing_stage" in lines[1]
    assert "status=error" in lines[1]
    assert "error=ValueError: Test error" in lines[1]
    assert "customer_id=2" in lines[1]
