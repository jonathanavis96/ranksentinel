"""Tests for round-robin fetch scheduler with 429 handling."""

import time


from ranksentinel.runner.fetch_scheduler import FetchScheduler


def test_scheduler_basic_round_robin():
    """Test basic round-robin scheduling across customers."""
    scheduler = FetchScheduler()

    # Add URLs for two customers
    scheduler.add_tasks(1, ["https://a.com/page1", "https://a.com/page2"])
    scheduler.add_tasks(2, ["https://b.com/page1", "https://b.com/page2"])

    # Should alternate between customers
    task1 = scheduler.next_task()
    assert task1.customer_id == 1
    assert task1.url == "https://a.com/page1"

    task2 = scheduler.next_task()
    assert task2.customer_id == 2
    assert task2.url == "https://b.com/page1"

    task3 = scheduler.next_task()
    assert task3.customer_id == 1
    assert task3.url == "https://a.com/page2"

    task4 = scheduler.next_task()
    assert task4.customer_id == 2
    assert task4.url == "https://b.com/page2"

    # No more tasks
    assert scheduler.next_task() is None


def test_scheduler_429_cooldown():
    """Test that 429 responses trigger domain cooldown."""
    scheduler = FetchScheduler(
        initial_backoff_seconds=1.0,
        max_backoff_seconds=5.0,
    )

    # Add URLs for same domain
    scheduler.add_tasks(1, ["https://example.com/page1", "https://example.com/page2"])

    # First task
    task1 = scheduler.next_task()
    assert task1.url == "https://example.com/page1"

    # Simulate 429 response (requeues task)
    scheduler.record_429(task1)

    # Next task should be None (domain cooling down, both page1 retry and page2 blocked)
    task2 = scheduler.next_task()
    assert task2 is None

    # Wait for cooldown
    time.sleep(1.1)

    # After cooldown, should get next task from queue (page2 comes before page1 retry in queue)
    task3 = scheduler.next_task()
    assert task3 is not None
    # Either page1 retry or page2 is acceptable (queue order)
    assert task3.url in ["https://example.com/page1", "https://example.com/page2"]


def test_scheduler_429_interleaving():
    """Test that 429 on one domain doesn't block other domains."""
    scheduler = FetchScheduler(
        initial_backoff_seconds=10.0,  # Long cooldown
    )

    # Customer A: domain a.com
    scheduler.add_tasks(1, ["https://a.com/page1"])
    # Customer B: domain b.com
    scheduler.add_tasks(2, ["https://b.com/page1", "https://b.com/page2"])
    # Customer C: domain c.com
    scheduler.add_tasks(3, ["https://c.com/page1"])

    # Get task for customer A
    task_a = scheduler.next_task()
    assert task_a.customer_id == 1
    assert task_a.domain == "a.com"

    # Simulate 429 on a.com
    scheduler.record_429(task_a)

    # Should now get task for customer B (domain b.com is not rate-limited)
    task_b1 = scheduler.next_task()
    assert task_b1.customer_id == 2
    assert task_b1.domain == "b.com"
    scheduler.record_success(task_b1)

    # Should get task for customer C
    task_c = scheduler.next_task()
    assert task_c.customer_id == 3
    assert task_c.domain == "c.com"
    scheduler.record_success(task_c)

    # Should get second task for customer B (round-robin continues)
    task_b2 = scheduler.next_task()
    assert task_b2.customer_id == 2
    assert task_b2.domain == "b.com"
    scheduler.record_success(task_b2)

    # Now no tasks ready (only a.com remains, still cooling down)
    assert scheduler.next_task() is None
    assert scheduler.has_ready_tasks()  # But tasks still exist


def test_scheduler_max_attempts():
    """Test that tasks are not retried beyond max attempts."""
    scheduler = FetchScheduler(
        max_attempts_per_url=3,
        initial_backoff_seconds=0.05,  # Short backoff for testing
    )

    scheduler.add_tasks(1, ["https://example.com/page1"])

    # Attempt 1
    task1 = scheduler.next_task()
    assert task1.attempt == 1
    scheduler.record_429(task1)

    # Attempt 2
    time.sleep(0.1)
    task2 = scheduler.next_task()
    assert task2 is not None
    assert task2.attempt == 2
    scheduler.record_429(task2)

    # Attempt 3
    time.sleep(0.2)
    task3 = scheduler.next_task()
    assert task3 is not None
    assert task3.attempt == 3
    scheduler.record_429(task3)

    # No more attempts (max_attempts_per_url=3 reached)
    time.sleep(1.0)
    assert scheduler.next_task() is None
    assert not scheduler.has_ready_tasks()


def test_scheduler_max_429s_per_domain():
    """Test that domain is skipped after exceeding 429 threshold."""
    scheduler = FetchScheduler(
        max_429s_per_domain=2,
        max_attempts_per_url=10,  # High to avoid attempt limit
        initial_backoff_seconds=0.05,  # Short backoff for testing
    )

    # Add multiple URLs for same domain
    scheduler.add_tasks(
        1,
        [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ],
    )

    # First URL: 429 (count=1)
    task1 = scheduler.next_task()
    scheduler.record_429(task1)

    # Wait for cooldown and get retry of page1
    time.sleep(0.1)
    task1_retry = scheduler.next_task()
    assert task1_retry is not None
    scheduler.record_429(task1_retry)  # Second 429 (count=2, threshold reached)

    # Domain has now hit max_429s_per_domain=2
    # All remaining tasks for this domain should be skipped
    time.sleep(1.0)
    assert scheduler.next_task() is None
    assert not scheduler.has_ready_tasks()


def test_scheduler_exponential_backoff():
    """Test that backoff increases exponentially."""
    scheduler = FetchScheduler(
        initial_backoff_seconds=1.0,
        backoff_multiplier=2.0,
        backoff_jitter=0.0,  # No jitter for deterministic test
    )

    scheduler.add_tasks(1, ["https://example.com/page1"])

    # First 429: backoff = 1s
    task1 = scheduler.next_task()
    start1 = time.time()
    scheduler.record_429(task1)
    cooldown1 = scheduler.domain_next_allowed_at["example.com"] - start1
    assert 0.9 <= cooldown1 <= 1.1

    # Second 429: backoff = 2s
    time.sleep(1.1)
    task2 = scheduler.next_task()
    start2 = time.time()
    scheduler.record_429(task2)
    cooldown2 = scheduler.domain_next_allowed_at["example.com"] - start2
    assert 1.9 <= cooldown2 <= 2.1


def test_scheduler_success_resets_consecutive_429s():
    """Test that success resets consecutive 429 counter."""
    scheduler = FetchScheduler(
        initial_backoff_seconds=1.0,
        backoff_multiplier=2.0,
        backoff_jitter=0.0,
    )

    # Add multiple URLs
    scheduler.add_tasks(
        1,
        [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ],
    )

    # First URL: 429 (backoff = 1s)
    task1 = scheduler.next_task()
    scheduler.record_429(task1)

    time.sleep(1.1)

    # Second URL: success (resets consecutive counter)
    task2 = scheduler.next_task()
    assert task2 is not None
    scheduler.record_success(task2)

    # Third URL: 429 (backoff should be 1s again, not 2s)
    task3 = scheduler.next_task()
    assert task3 is not None
    start3 = time.time()
    scheduler.record_429(task3)
    cooldown3 = scheduler.domain_next_allowed_at["example.com"] - start3
    assert 0.9 <= cooldown3 <= 1.1  # Back to initial backoff


def test_scheduler_domain_stats():
    """Test domain statistics reporting."""
    scheduler = FetchScheduler()

    scheduler.add_tasks(1, ["https://a.com/page1"])
    scheduler.add_tasks(2, ["https://b.com/page1"])

    # Process a.com with 429
    task_a = scheduler.next_task()
    scheduler.record_429(task_a)

    # Process b.com with success
    task_b = scheduler.next_task()
    scheduler.record_success(task_b)

    stats = scheduler.get_domain_stats()

    assert "a.com" in stats
    assert stats["a.com"]["http_429_count"] == 1
    assert stats["a.com"]["consecutive_429s"] == 1
    assert stats["a.com"]["cooling_down"] is True

    assert "b.com" in stats
    assert stats["b.com"]["http_429_count"] == 0
    assert stats["b.com"]["consecutive_429s"] == 0
    assert stats["b.com"]["cooling_down"] is False


def test_scheduler_non_429_error_no_retry():
    """Test that non-429 errors don't trigger retry or cooldown."""
    scheduler = FetchScheduler()

    scheduler.add_tasks(
        1,
        [
            "https://example.com/page1",
            "https://example.com/page2",
        ],
    )

    # First URL: non-429 error (e.g., 500)
    task1 = scheduler.next_task()
    scheduler.record_non_429_error(task1)

    # Second URL should be available immediately (no cooldown)
    task2 = scheduler.next_task()
    assert task2 is not None
    assert task2.url == "https://example.com/page2"

    # No retry for page1
    scheduler.record_success(task2)
    assert scheduler.next_task() is None
