"""Weekly page fetcher with polite crawling, retries, and limits.

This module fetches sampled pages from a sitemap for weekly link checking.
Features:
- Enforces per-run crawl limits
- Polite crawling with timeouts and retries
- Records fetch status for each URL
- Uses existing http_client for retry/backoff logic
"""

import sqlite3
from typing import Any

from ranksentinel.http_client import FetchResult, fetch_text
from ranksentinel.runner.logging_utils import log_structured


class PageFetchResult:
    """Result of fetching a single page."""
    
    def __init__(
        self,
        url: str,
        status_code: int | None,
        final_url: str | None,
        body: str | None,
        error: str | None,
        error_type: str | None,
    ):
        self.url = url
        self.status_code = status_code
        self.final_url = final_url
        self.body = body
        self.error = error
        self.error_type = error_type
    
    @property
    def ok(self) -> bool:
        """Returns True if fetch was successful (2xx)."""
        return self.status_code is not None and 200 <= self.status_code < 300
    
    @property
    def is_404(self) -> bool:
        """Returns True if page returned 404."""
        return self.status_code == 404


def fetch_pages(
    run_id: str,
    customer_id: int,
    urls: list[str],
    crawl_limit: int,
    timeout: int = 20,
    attempts: int = 3,
) -> list[PageFetchResult]:
    """Fetch a list of URLs with crawl limit enforcement.
    
    Args:
        run_id: Unique run identifier for logging
        customer_id: Customer ID for logging
        urls: List of URLs to fetch
        crawl_limit: Maximum number of pages to fetch
        timeout: Request timeout in seconds
        attempts: Number of retry attempts per URL
    
    Returns:
        List of PageFetchResult objects (up to crawl_limit entries)
    """
    log_structured(
        run_id,
        run_type="weekly",
        stage="page_fetch",
        status="start",
        customer_id=customer_id,
        total_urls=len(urls),
        crawl_limit=crawl_limit,
    )
    
    results = []
    urls_to_fetch = urls[:crawl_limit]
    
    for idx, url in enumerate(urls_to_fetch, start=1):
        log_structured(
            run_id,
            run_type="weekly",
            stage="page_fetch",
            status="fetching",
            customer_id=customer_id,
            url=url,
            progress=f"{idx}/{len(urls_to_fetch)}",
        )
        
        # Use existing http_client for retry/backoff
        fetch_result: FetchResult = fetch_text(
            url=url,
            timeout=timeout,
            attempts=attempts,
        )
        
        # Convert to PageFetchResult
        result = PageFetchResult(
            url=url,
            status_code=fetch_result.status_code,
            final_url=fetch_result.final_url,
            body=fetch_result.body,
            error=fetch_result.error,
            error_type=fetch_result.error_type.value if fetch_result.error_type else None,
        )
        
        results.append(result)
        
        # Log fetch outcome
        if result.ok:
            log_structured(
                run_id,
                run_type="weekly",
                stage="page_fetch",
                status="success",
                customer_id=customer_id,
                url=url,
                status_code=result.status_code,
            )
        else:
            log_structured(
                run_id,
                run_type="weekly",
                stage="page_fetch",
                status="error",
                customer_id=customer_id,
                url=url,
                status_code=result.status_code,
                error=result.error,
                error_type=result.error_type,
            )
    
    log_structured(
        run_id,
        run_type="weekly",
        stage="page_fetch",
        status="complete",
        customer_id=customer_id,
        fetched_count=len(results),
        success_count=sum(1 for r in results if r.ok),
        error_count=sum(1 for r in results if not r.ok),
    )
    
    return results


def persist_fetch_results(
    conn: sqlite3.Connection,
    run_id: str,
    customer_id: int,
    results: list[PageFetchResult],
) -> None:
    """Persist page fetch results to database.
    
    Args:
        conn: Database connection
        run_id: Unique run identifier
        customer_id: Customer ID
        results: List of PageFetchResult objects
    """
    # This will be implemented in a future task when we define the schema
    # For now, just log the results
    log_structured(
        run_id,
        run_type="weekly",
        stage="persist_fetch",
        status="info",
        customer_id=customer_id,
        message=f"Would persist {len(results)} fetch results (schema TBD)",
    )
