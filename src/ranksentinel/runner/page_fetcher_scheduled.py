"""Scheduled page fetching with round-robin 429 handling across customers."""

import time

from ranksentinel.http_client import FetchResult, fetch_text
from ranksentinel.runner.fetch_scheduler import FetchScheduler
from ranksentinel.runner.logging_utils import log_structured
from ranksentinel.runner.page_fetcher import PageFetchResult


def fetch_pages_scheduled(
    run_id: str,
    customer_urls: dict[int, list[str]],
    crawl_limits: dict[int, int],
    timeout: int = 20,
    max_idle_seconds: float = 30.0,
) -> dict[int, list[PageFetchResult]]:
    """Fetch pages across multiple customers with fair round-robin and 429 handling.

    Args:
        run_id: Unique run identifier for logging
        customer_urls: Dict mapping customer_id to list of URLs to fetch
        crawl_limits: Dict mapping customer_id to max pages to fetch
        timeout: Request timeout in seconds
        max_idle_seconds: Max time to wait when all domains are cooling down

    Returns:
        Dict mapping customer_id to list of PageFetchResult objects
    """
    log_structured(
        run_id,
        run_type="weekly",
        stage="fetch_scheduled",
        status="start",
        total_customers=len(customer_urls),
    )

    # Initialize scheduler
    scheduler = FetchScheduler(
        max_attempts_per_url=3,
        max_429s_per_domain=10,
        initial_backoff_seconds=5.0,
        max_backoff_seconds=60.0,
    )

    # Add all tasks to scheduler (respecting crawl limits)
    for customer_id, urls in customer_urls.items():
        limit = crawl_limits.get(customer_id, 100)
        urls_to_fetch = urls[:limit]
        scheduler.add_tasks(customer_id, urls_to_fetch)

        log_structured(
            run_id,
            run_type="weekly",
            stage="fetch_scheduled",
            status="queued",
            customer_id=customer_id,
            url_count=len(urls_to_fetch),
        )

    # Fetch tasks using round-robin scheduling
    results: dict[int, list[PageFetchResult]] = {cid: [] for cid in customer_urls}
    fetch_count = 0
    last_progress_time = time.time()
    idle_start: float | None = None

    while scheduler.has_ready_tasks():
        task = scheduler.next_task()

        if task is None:
            # All domains are cooling down
            now = time.time()

            if idle_start is None:
                idle_start = now
                log_structured(
                    run_id,
                    run_type="weekly",
                    stage="fetch_scheduled",
                    status="cooling_down",
                    message="All domains cooling down, waiting for cooldown to expire",
                )

            # Check if we've been idle too long
            if now - idle_start > max_idle_seconds:
                log_structured(
                    run_id,
                    run_type="weekly",
                    stage="fetch_scheduled",
                    status="timeout",
                    message=f"Exceeded max idle time ({max_idle_seconds}s), stopping",
                )
                break

            # Short sleep and retry
            time.sleep(0.5)
            continue

        # Reset idle timer when we get a task
        idle_start = None
        fetch_count += 1

        # Log progress every 10 fetches
        if fetch_count % 10 == 0 or time.time() - last_progress_time > 10:
            log_structured(
                run_id,
                run_type="weekly",
                stage="fetch_scheduled",
                status="progress",
                fetched_count=fetch_count,
            )
            last_progress_time = time.time()

        # Fetch the URL (no retries here - scheduler handles retry logic)
        log_structured(
            run_id,
            run_type="weekly",
            stage="fetch_scheduled",
            status="fetching",
            customer_id=task.customer_id,
            url=task.url,
            attempt=task.attempt,
        )

        fetch_result: FetchResult = fetch_text(
            url=task.url,
            timeout=timeout,
            attempts=1,  # No retries - scheduler handles this
        )

        # Convert to PageFetchResult
        result = PageFetchResult(
            url=task.url,
            status_code=fetch_result.status_code,
            final_url=fetch_result.final_url,
            body=fetch_result.body,
            error=fetch_result.error,
            error_type=fetch_result.error_type.value if fetch_result.error_type else None,
        )

        # Handle result and update scheduler
        if fetch_result.status_code == 429:
            log_structured(
                run_id,
                run_type="weekly",
                stage="fetch_scheduled",
                status="rate_limited",
                customer_id=task.customer_id,
                url=task.url,
                attempt=task.attempt,
            )
            scheduler.record_429(task)
            # Add 429 result so it gets counted in run_coverage stats
            results[task.customer_id].append(result)
        elif result.ok:
            log_structured(
                run_id,
                run_type="weekly",
                stage="fetch_scheduled",
                status="success",
                customer_id=task.customer_id,
                url=task.url,
                status_code=result.status_code,
            )
            scheduler.record_success(task)
            results[task.customer_id].append(result)
        else:
            log_structured(
                run_id,
                run_type="weekly",
                stage="fetch_scheduled",
                status="error",
                customer_id=task.customer_id,
                url=task.url,
                status_code=result.status_code,
                error=result.error,
                error_type=result.error_type,
            )
            scheduler.record_non_429_error(task)
            results[task.customer_id].append(result)

    # Log final stats
    domain_stats = scheduler.get_domain_stats()
    total_429s = sum(stats["http_429_count"] for stats in domain_stats.values())

    log_structured(
        run_id,
        run_type="weekly",
        stage="fetch_scheduled",
        status="complete",
        total_fetched=fetch_count,
        total_429s=total_429s,
        domains_affected=len([d for d, s in domain_stats.items() if s["http_429_count"] > 0]),
    )

    return results
