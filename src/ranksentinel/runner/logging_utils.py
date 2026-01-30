"""Structured logging utilities for RankSentinel runners."""

import time
import uuid
from contextlib import contextmanager
from typing import Any


def generate_run_id() -> str:
    """Generate a unique run ID for tracking."""
    return str(uuid.uuid4())


def log_structured(run_id: str, **kwargs: Any) -> None:
    """Log structured data with run_id and additional fields.

    Args:
        run_id: Unique identifier for the run
        **kwargs: Additional key-value pairs to log (customer_id, stage, elapsed_ms, etc.)
    """
    parts = [f"run_id={run_id}"]
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}={value}")
    print(" ".join(parts))


@contextmanager
def log_stage(run_id: str, stage: str, **extra: Any):
    """Context manager to log a stage with timing.

    Args:
        run_id: Unique identifier for the run
        stage: Name of the stage being executed
        **extra: Additional context (e.g., customer_id, url)
    """
    start_time = time.time()
    log_structured(run_id, stage=stage, status="start", **extra)
    try:
        yield
        elapsed_ms = int((time.time() - start_time) * 1000)
        log_structured(run_id, stage=stage, status="complete", elapsed_ms=elapsed_ms, **extra)
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        log_structured(
            run_id,
            stage=stage,
            status="error",
            elapsed_ms=elapsed_ms,
            error=f"{type(e).__name__}: {e}",
            **extra,
        )
        raise


def log_summary(
    run_id: str, run_type: str, total: int, succeeded: int, failed: int, elapsed_ms: int
) -> None:
    """Log final run summary in a cron-friendly format.

    Args:
        run_id: Unique identifier for the run
        run_type: Type of run (daily or weekly)
        total: Total number of customers processed
        succeeded: Number of successful customers
        failed: Number of failed customers
        elapsed_ms: Total elapsed time in milliseconds
    """
    print(
        f"SUMMARY run_id={run_id} run_type={run_type} "
        f"total_customers={total} succeeded={succeeded} failed={failed} "
        f"elapsed_ms={elapsed_ms}"
    )
