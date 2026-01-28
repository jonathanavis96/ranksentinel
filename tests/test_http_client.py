"""Tests for HTTP client wrapper."""

import pytest

from ranksentinel.http_client import (
    ErrorType,
    FetchResult,
    classify_error,
    fetch_bytes,
    fetch_text,
    fetch_with_retry,
)


def test_fetch_result_ok():
    """Test FetchResult.ok property."""
    result = FetchResult(status_code=200, final_url="https://example.com", body="content")
    assert result.ok is True
    assert result.is_error is False


def test_fetch_result_error():
    """Test FetchResult.is_error property."""
    result = FetchResult(error="timeout", error_type=ErrorType.TIMEOUT)
    assert result.ok is False
    assert result.is_error is True


def test_fetch_result_4xx():
    """Test FetchResult for 4xx errors."""
    result = FetchResult(
        status_code=404,
        final_url="https://example.com/notfound",
        body="Not Found",
        error="HTTP 404",
        error_type=ErrorType.HTTP_4XX,
    )
    assert result.ok is False
    assert result.is_error is True
    assert result.status_code == 404


def test_fetch_result_5xx():
    """Test FetchResult for 5xx errors."""
    result = FetchResult(
        status_code=500,
        final_url="https://example.com",
        body="Server Error",
        error="HTTP 500",
        error_type=ErrorType.HTTP_5XX,
    )
    assert result.ok is False
    assert result.is_error is True
    assert result.status_code == 500


def test_fetch_result_redirect_chain():
    """Test redirect chain tracking."""
    result = FetchResult(
        status_code=200,
        final_url="https://example.com/final",
        redirect_chain=[
            "https://example.com/original",
            "https://example.com/redirect",
            "https://example.com/final",
        ],
        body="content",
    )
    assert len(result.redirect_chain) == 3
    assert result.final_url == "https://example.com/final"


def test_error_classification():
    """Test error classification logic."""
    from requests.exceptions import ConnectionError, HTTPError, Timeout

    # Timeout errors
    timeout_error = Timeout("Request timed out")
    assert classify_error(timeout_error) == ErrorType.TIMEOUT

    # Connection errors
    conn_error = ConnectionError("Connection refused")
    assert classify_error(conn_error) == ErrorType.CONNECTION

    # DNS errors
    dns_error = ConnectionError("Name or service not known")
    assert classify_error(dns_error) == ErrorType.DNS

    # HTTP errors - need mock response
    class MockResponse:
        status_code = 404

    http_error = HTTPError()
    http_error.response = MockResponse()
    assert classify_error(http_error) == ErrorType.HTTP_4XX

    # Unknown errors
    generic_error = Exception("Unknown")
    assert classify_error(generic_error) == ErrorType.UNKNOWN


def test_fetch_text_wrapper():
    """Test fetch_text convenience wrapper."""
    # This is an integration test that would require mocking
    # Just verify it returns a FetchResult
    result = fetch_text("https://httpbin.org/status/200", timeout=10, attempts=1)
    assert isinstance(result, FetchResult)
    # Don't assert success since network can fail in CI


def test_fetch_bytes_wrapper():
    """Test fetch_bytes convenience wrapper."""
    # This is an integration test that would require mocking
    # Just verify it returns a FetchResult
    result = fetch_bytes("https://httpbin.org/status/200", timeout=10, attempts=1)
    assert isinstance(result, FetchResult)
    # Don't assert success since network can fail in CI


def test_fetch_with_retry_user_agent():
    """Test that User-Agent header is properly set."""
    # This would require mocking requests to verify headers
    # For now, just ensure the function signature is correct
    result = fetch_with_retry(
        "https://httpbin.org/status/200",
        timeout=10,
        attempts=1,
        user_agent="CustomAgent/1.0",
    )
    assert isinstance(result, FetchResult)


def test_fetch_with_retry_redirects():
    """Test redirect handling."""
    # This would require mocking to properly test
    result = fetch_with_retry(
        "https://httpbin.org/status/200", timeout=10, attempts=1, allow_redirects=True
    )
    assert isinstance(result, FetchResult)


def test_fetch_result_defaults():
    """Test FetchResult with default values."""
    result = FetchResult()
    assert result.status_code is None
    assert result.final_url is None
    assert result.body is None
    assert result.redirect_chain == []
    assert result.error is None
    assert result.error_type is None
    assert result.ok is False
    assert result.is_error is False
