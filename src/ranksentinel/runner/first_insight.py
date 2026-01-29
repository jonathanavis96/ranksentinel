"""First Insight report generation.

This module provides functionality to generate and send an immediate
onboarding report for new customers, helping them see value quickly
without waiting for the weekly schedule.

Business logic will be implemented in task 4.6b.
"""

from sqlite3 import Connection


def trigger_first_insight_report(conn: Connection, customer_id: int) -> None:
    """Trigger generation and delivery of a First Insight report.
    
    Args:
        conn: Database connection
        customer_id: ID of the customer to generate report for
        
    Note:
        This is a stub implementation. Full business logic (data collection,
        report composition, email sending) will be implemented in tasks 4.6b and 4.6c.
    """
    # TODO(4.6b): Implement data collection
    # - Fetch key pages (status/redirect/title/canonical/noindex)
    # - Collect robots.txt + sitemap hash
    # - Optional PSI on key pages (respect caps)
    # - Write findings with run_type='first_insight'
    
    # TODO(4.6c): Implement email delivery
    # - Generate email using report composer
    # - Send via Mailgun with idempotency
    # - Record delivery in database
    
    pass
