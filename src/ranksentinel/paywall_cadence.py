"""Paywall email cadence logic for RankSentinel.

This module handles the weekly paywall email cadence for post-trial customers:
- Weeks 1-4 after trial end: 1 paywalled email/week
- After week 4: status → 'previously_interested'
- previously_interested: 1 locked reminder/month on the same weekday/time

Monthly scheduling rule: First occurrence of digest weekday on/after the 1st of the month.
"""

from datetime import datetime, timedelta, timezone
import sqlite3


def should_send_paywall_digest(
    conn: sqlite3.Connection,
    customer_id: int,
    current_time: datetime | None = None,
) -> tuple[bool, str]:
    """Determine if a paywalled customer should receive a digest this week.

    Logic:
    - paywalled status: Send weekly for first 4 weeks (weekly_digest_sent_count < 4)
    - previously_interested: Send monthly on same weekday (first occurrence on/after 1st of month)

    Args:
        conn: Database connection
        customer_id: Customer ID to check
        current_time: Current UTC time (for testing; defaults to now)

    Returns:
        Tuple of (should_send: bool, reason: str)
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    cursor = conn.cursor()

    # Fetch customer status and cadence tracking data
    # Note: Using existing columns (digest_weekday, digest_time_local, digest_timezone)
    # last_digest_sent_at needs to be added to schema
    cursor.execute(
        """
        SELECT
            status,
            paywalled_since,
            weekly_digest_sent_count,
            digest_weekday,
            digest_time_local,
            digest_timezone
        FROM customers
        WHERE id = ?
    """,
        (customer_id,),
    )

    row = cursor.fetchone()
    if not row:
        return (False, "customer_not_found")

    status = row[0]
    paywalled_since = row[1]
    weekly_digest_sent_count = row[2] or 0
    digest_schedule_day = row[3]  # weekday 0-6 (Monday=0)
    digest_schedule_hour_str = row[4]  # hour:minute in local time (e.g., "09:00")
    digest_schedule_tz = row[5]  # timezone string

    # Only process paywalled and previously_interested customers
    if status not in ("paywalled", "previously_interested"):
        return (False, f"status={status}")

    # paywalled: weekly emails for first 4 weeks
    if status == "paywalled":
        if weekly_digest_sent_count >= 4:
            return (False, "paywalled_max_4_reached")

        # For paywalled, check last deliveries entry for this customer
        cursor.execute(
            """
            SELECT sent_at
            FROM deliveries
            WHERE customer_id = ? AND run_type = 'weekly'
            ORDER BY sent_at DESC
            LIMIT 1
        """,
            (customer_id,),
        )

        last_email_row = cursor.fetchone()
        if last_email_row:
            last_sent = datetime.fromisoformat(last_email_row[0])
            days_since_last = (current_time - last_sent).days
            if days_since_last < 7:
                return (False, f"paywalled_too_soon_days={days_since_last}")

        return (True, "paywalled_weekly")

    # previously_interested: monthly on same weekday
    if status == "previously_interested":
        if digest_schedule_day is None:
            return (False, "previously_interested_no_schedule")

        # Check if already sent this month (via deliveries)
        cursor.execute(
            """
            SELECT sent_at
            FROM deliveries
            WHERE customer_id = ? AND run_type = 'weekly'
            ORDER BY sent_at DESC
            LIMIT 1
        """,
            (customer_id,),
        )

        last_email_row = cursor.fetchone()
        if last_email_row:
            last_sent = datetime.fromisoformat(last_email_row[0])
            # Same year and month = already sent this month
            if last_sent.year == current_time.year and last_sent.month == current_time.month:
                return (False, "previously_interested_already_sent_this_month")

        # Find first occurrence of digest_schedule_day on/after 1st of current month
        first_of_month = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        target_weekday = digest_schedule_day

        # Calculate days until target weekday
        days_ahead = (target_weekday - first_of_month.weekday()) % 7
        target_date = first_of_month + timedelta(days=days_ahead)

        # Check if we've reached or passed the target date
        if current_time.date() >= target_date.date():
            return (True, "previously_interested_monthly")
        else:
            return (False, f"previously_interested_waiting_until={target_date.date()}")

    return (False, "unknown_state")


def increment_digest_count_and_check_transition(
    conn: sqlite3.Connection,
    customer_id: int,
    current_time: datetime | None = None,
) -> bool:
    """Increment weekly_digest_sent_count and transition paywalled → previously_interested after 4 sends.

    This should be called after successfully sending a paywall digest email.

    Args:
        conn: Database connection
        customer_id: Customer ID
        current_time: Current UTC time (for testing; defaults to now)

    Returns:
        True if customer was transitioned to previously_interested, False otherwise
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    cursor = conn.cursor()
    now_iso = current_time.isoformat()

    # Increment count (last_digest_sent_at tracked via deliveries)
    cursor.execute(
        """
        UPDATE customers
        SET weekly_digest_sent_count = weekly_digest_sent_count + 1,
            updated_at = ?
        WHERE id = ? AND status = 'paywalled'
    """,
        (now_iso, customer_id),
    )

    if cursor.rowcount == 0:
        # Customer not paywalled, nothing to do
        conn.commit()
        return False

    # Check if we need to transition to previously_interested (count >= 4)
    cursor.execute(
        """
        SELECT weekly_digest_sent_count
        FROM customers
        WHERE id = ?
    """,
        (customer_id,),
    )

    row = cursor.fetchone()
    if row and row[0] >= 4:
        # Transition to previously_interested
        cursor.execute(
            """
            UPDATE customers
            SET status = 'previously_interested',
                updated_at = ?
            WHERE id = ? AND status = 'paywalled'
        """,
            (now_iso, customer_id),
        )

        conn.commit()
        return cursor.rowcount > 0

    conn.commit()
    return False
