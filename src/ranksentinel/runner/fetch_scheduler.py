"""Fair round-robin fetch scheduler with per-domain cooldown.

Implements a scheduler that:
- Interleaves fetches across multiple customers
- Respects per-domain rate limit cooldowns (HTTP 429)
- Tracks retry attempts per URL
- Caps total 429 responses per domain
- Prevents unbounded sleep/blocking
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterator
from urllib.parse import urlparse


@dataclass
class FetchTask:
    """A single URL fetch task."""
    
    customer_id: int
    url: str
    attempt: int = 1
    
    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        return urlparse(self.url).netloc


class FetchScheduler:
    """Round-robin scheduler with per-domain cooldown for HTTP 429 handling.
    
    Args:
        max_attempts_per_url: Maximum retry attempts for a single URL (default: 3)
        max_429s_per_domain: Maximum total 429s per domain before skipping remaining URLs (default: 10)
        initial_backoff_seconds: Initial cooldown after first 429 (default: 5)
        max_backoff_seconds: Maximum cooldown cap (default: 60)
        backoff_multiplier: Exponential backoff multiplier (default: 2)
        backoff_jitter: Random jitter as fraction of backoff (default: 0.1)
    """
    
    def __init__(
        self,
        max_attempts_per_url: int = 3,
        max_429s_per_domain: int = 10,
        initial_backoff_seconds: float = 5.0,
        max_backoff_seconds: float = 60.0,
        backoff_multiplier: float = 2.0,
        backoff_jitter: float = 0.1,
    ):
        self.max_attempts_per_url = max_attempts_per_url
        self.max_429s_per_domain = max_429s_per_domain
        self.initial_backoff_seconds = initial_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds
        self.backoff_multiplier = backoff_multiplier
        self.backoff_jitter = backoff_jitter
        
        # Per-domain state
        self.domain_next_allowed_at: dict[str, float] = {}
        self.domain_429_count: dict[str, int] = defaultdict(int)
        self.domain_consecutive_429s: dict[str, int] = defaultdict(int)
        
        # Task queues (per-customer round-robin)
        self.customer_queues: dict[int, deque[FetchTask]] = defaultdict(deque)
        self.customer_order: deque[int] = deque()
        
    def add_tasks(self, customer_id: int, urls: list[str]) -> None:
        """Add URLs for a customer to the scheduler.
        
        Args:
            customer_id: Customer identifier
            urls: List of URLs to fetch
        """
        if not urls:
            return
            
        for url in urls:
            task = FetchTask(customer_id=customer_id, url=url, attempt=1)
            self.customer_queues[customer_id].append(task)
        
        # Add to round-robin order if new customer
        if customer_id not in self.customer_order:
            self.customer_order.append(customer_id)
    
    def next_task(self) -> FetchTask | None:
        """Get the next task to fetch, respecting domain cooldowns.
        
        Uses round-robin across customers to ensure fairness.
        Skips tasks if domain is cooling down or has exceeded 429 threshold.
        
        Returns:
            Next FetchTask to process, or None if no tasks are ready
        """
        if not self.customer_order:
            return None
        
        now = time.time()
        checked_customers = 0
        total_customers = len(self.customer_order)
        
        # Try to find a ready task by cycling through customers
        while checked_customers < total_customers:
            # Get next customer in round-robin order
            customer_id = self.customer_order[0]
            queue = self.customer_queues[customer_id]
            
            if not queue:
                # Customer has no more tasks, remove from rotation
                self.customer_order.popleft()
                del self.customer_queues[customer_id]
                total_customers -= 1
                continue
            
            # Peek at next task for this customer
            task = queue[0]
            domain = task.domain
            
            # Check if domain has exceeded 429 threshold
            if self.domain_429_count[domain] >= self.max_429s_per_domain:
                # Skip this task permanently
                queue.popleft()
                continue
            
            # Check if domain is still cooling down
            if domain in self.domain_next_allowed_at:
                if now < self.domain_next_allowed_at[domain]:
                    # Not ready yet, try next customer
                    self.customer_order.rotate(-1)
                    checked_customers += 1
                    continue
            
            # Task is ready! Remove and return it
            task = queue.popleft()
            
            # Rotate customer to end for fairness
            self.customer_order.rotate(-1)
            
            return task
        
        # All customers checked but no tasks ready (all cooling down)
        return None
    
    def has_ready_tasks(self) -> bool:
        """Check if any tasks exist (ready or cooling down)."""
        return bool(self.customer_queues)
    
    def record_success(self, task: FetchTask) -> None:
        """Record successful fetch, resetting consecutive 429 counter.
        
        Args:
            task: The task that succeeded
        """
        domain = task.domain
        self.domain_consecutive_429s[domain] = 0
    
    def record_429(self, task: FetchTask) -> None:
        """Record a 429 response and apply cooldown.
        
        Args:
            task: The task that received a 429 response
        """
        domain = task.domain
        
        # Increment counters
        self.domain_429_count[domain] += 1
        self.domain_consecutive_429s[domain] += 1
        
        # Calculate exponential backoff with jitter
        consecutive = self.domain_consecutive_429s[domain]
        backoff = min(
            self.initial_backoff_seconds * (self.backoff_multiplier ** (consecutive - 1)),
            self.max_backoff_seconds
        )
        
        # Add jitter (±10% by default)
        import random
        jitter = backoff * self.backoff_jitter * random.uniform(-1, 1)
        backoff = max(0, backoff + jitter)
        
        # Set cooldown
        self.domain_next_allowed_at[domain] = time.time() + backoff
        
        # Requeue if under retry limit and domain hasn't exceeded threshold
        if (task.attempt < self.max_attempts_per_url and 
            self.domain_429_count[domain] < self.max_429s_per_domain):
            retry_task = FetchTask(
                customer_id=task.customer_id,
                url=task.url,
                attempt=task.attempt + 1
            )
            self.customer_queues[task.customer_id].append(retry_task)
    
    def record_non_429_error(self, task: FetchTask) -> None:
        """Record a non-429 error (don't apply cooldown, don't retry).
        
        Args:
            task: The task that encountered an error
        """
        # For non-429 errors, we don't retry or apply cooldown
        # This follows the existing retry logic in http_client.py
        pass
    
    def get_domain_stats(self) -> dict[str, dict]:
        """Get statistics for all domains.
        
        Returns:
            Dict mapping domain to stats (429_count, consecutive_429s, cooling_down)
        """
        now = time.time()
        stats = {}
        
        for domain in set(list(self.domain_429_count.keys()) + 
                         list(self.domain_next_allowed_at.keys())):
            cooling_down = (domain in self.domain_next_allowed_at and 
                          now < self.domain_next_allowed_at[domain])
            stats[domain] = {
                "http_429_count": self.domain_429_count[domain],
                "consecutive_429s": self.domain_consecutive_429s[domain],
                "cooling_down": cooling_down,
                "cooldown_seconds": (self.domain_next_allowed_at.get(domain, 0) - now) 
                                  if cooling_down else 0,
            }
        
        return stats
