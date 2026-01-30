"""Tests for weekly page fetcher."""

from unittest.mock import patch

from ranksentinel.http_client import ErrorType, FetchResult
from ranksentinel.runner.page_fetcher import (
    PageFetchResult,
    fetch_pages,
    persist_fetch_results,
)


def test_page_fetch_result_ok():
    """Test PageFetchResult.ok property."""
    result = PageFetchResult(
        url="https://example.com",
        status_code=200,
        final_url="https://example.com",
        body="<html>content</html>",
        error=None,
        error_type=None,
    )
    assert result.ok is True
    assert result.is_404 is False


def test_page_fetch_result_404():
    """Test PageFetchResult.is_404 property."""
    result = PageFetchResult(
        url="https://example.com/notfound",
        status_code=404,
        final_url="https://example.com/notfound",
        body="Not Found",
        error="HTTP 404",
        error_type="http_4xx",
    )
    assert result.ok is False
    assert result.is_404 is True


def test_page_fetch_result_error():
    """Test PageFetchResult with network error."""
    result = PageFetchResult(
        url="https://example.com",
        status_code=None,
        final_url=None,
        body=None,
        error="Connection timeout",
        error_type="timeout",
    )
    assert result.ok is False
    assert result.is_404 is False


@patch("ranksentinel.runner.page_fetcher.fetch_text")
def test_fetch_pages_enforces_crawl_limit(mock_fetch_text):
    """Test that crawl_limit is enforced."""
    # Mock successful fetches
    mock_fetch_text.return_value = FetchResult(
        status_code=200,
        final_url="https://example.com",
        body="<html>content</html>",
    )

    urls = [f"https://example.com/page{i}" for i in range(200)]
    crawl_limit = 50

    results = fetch_pages(
        run_id="test-run",
        customer_id=1,
        urls=urls,
        crawl_limit=crawl_limit,
    )

    # Should only fetch up to crawl_limit
    assert len(results) == crawl_limit
    assert mock_fetch_text.call_count == crawl_limit


@patch("ranksentinel.runner.page_fetcher.fetch_text")
def test_fetch_pages_handles_errors(mock_fetch_text):
    """Test that fetch_pages handles various error types."""
    # Create mixed results
    mock_results = [
        FetchResult(status_code=200, final_url="https://example.com/page1", body="ok"),
        FetchResult(
            status_code=404,
            final_url="https://example.com/page2",
            body="not found",
            error="HTTP 404",
            error_type=ErrorType.HTTP_4XX,
        ),
        FetchResult(
            status_code=500,
            final_url="https://example.com/page3",
            body="error",
            error="HTTP 500",
            error_type=ErrorType.HTTP_5XX,
        ),
        FetchResult(error="timeout", error_type=ErrorType.TIMEOUT),
    ]

    mock_fetch_text.side_effect = mock_results

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
        "https://example.com/page4",
    ]

    results = fetch_pages(
        run_id="test-run",
        customer_id=1,
        urls=urls,
        crawl_limit=100,
    )

    assert len(results) == 4
    assert results[0].ok is True
    assert results[1].is_404 is True
    assert results[2].status_code == 500
    assert results[3].error == "timeout"


@patch("ranksentinel.runner.page_fetcher.fetch_text")
def test_fetch_pages_uses_retry_params(mock_fetch_text):
    """Test that fetch_pages passes timeout and attempts to fetch_text."""
    mock_fetch_text.return_value = FetchResult(status_code=200, body="ok")

    urls = ["https://example.com"]

    fetch_pages(
        run_id="test-run",
        customer_id=1,
        urls=urls,
        crawl_limit=10,
        timeout=30,
        attempts=5,
    )

    # Verify fetch_text was called with correct parameters
    mock_fetch_text.assert_called_once_with(
        url="https://example.com",
        timeout=30,
        attempts=5,
    )


@patch("ranksentinel.runner.page_fetcher.fetch_text")
def test_fetch_pages_returns_empty_for_empty_urls(mock_fetch_text):
    """Test that fetch_pages handles empty URL list."""
    results = fetch_pages(
        run_id="test-run",
        customer_id=1,
        urls=[],
        crawl_limit=100,
    )

    assert len(results) == 0
    mock_fetch_text.assert_not_called()


def test_persist_fetch_results_placeholder(tmp_path):
    """Test persist_fetch_results placeholder (logs only for now)."""
    import sqlite3
    from ranksentinel.db import init_db

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))

    # Initialize schema before using snapshots table
    init_db(conn)

    results = [
        PageFetchResult(
            url="https://example.com",
            status_code=200,
            final_url="https://example.com",
            body="ok",
            error=None,
            error_type=None,
        )
    ]

    # Should not raise an error (just logs for now)
    persist_fetch_results(
        conn=conn,
        run_id="test-run",
        customer_id=1,
        results=results,
    )

    conn.close()


@patch("ranksentinel.runner.page_fetcher.fetch_text")
def test_fetch_pages_records_fetch_status(mock_fetch_text):
    """Test that fetch_pages records status for all fetched pages."""
    mock_fetch_text.side_effect = [
        FetchResult(status_code=200, final_url="https://example.com/page1", body="ok"),
        FetchResult(
            status_code=404,
            final_url="https://example.com/page2",
            body="not found",
            error="HTTP 404",
            error_type=ErrorType.HTTP_4XX,
        ),
    ]

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
    ]

    results = fetch_pages(
        run_id="test-run",
        customer_id=1,
        urls=urls,
        crawl_limit=10,
    )

    # Verify all results have status recorded
    assert all(r.status_code is not None or r.error is not None for r in results)
    assert results[0].status_code == 200
    assert results[1].status_code == 404
