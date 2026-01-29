"""Trial expiry logic for RankSentinel.

This module handles automatic trial expiry and transition to paywalled status.
Trial ends after 7 days OR 1 weekly digest (whichever comes first).
"""

from datetime import datetime, timedelta, timezone
import sqlite3


def check_and_expire_trials(conn: sqlite3.Connection) -> list[int]:
    """Check all trial customers and expire those that meet expiry conditions.
    
    Trial expiry rules:
    - 7 days have passed since trial_started_at, OR
    - 1 weekly digest has been sent (weekly_digest_sent_count >= 1)
    
    This function is idempotent - calling it multiple times will not create duplicate transitions.
    
    Args:
        conn: Database connection
        
    Returns:
        List of customer IDs that were transitioned from trial to paywalled
    """
    cursor = conn.cursor()
    now_utc = datetime.now(timezone.utc)
    seven_days_ago = (now_utc - timedelta(days=7)).isoformat()
    
    # Find all trial customers that should expire
    # Conditions: (trial_started_at <= 7 days ago) OR (weekly_digest_sent_count >= 1)
    cursor.execute("""
        SELECT id, trial_started_at, weekly_digest_sent_count
        FROM customers
        WHERE status = 'trial'
        AND (
            trial_started_at IS NOT NULL AND trial_started_at <= ?
            OR weekly_digest_sent_count >= 1
        )
    """, (seven_days_ago,))
    
    expired_trials = cursor.fetchall()
    expired_ids = []
    
    for row in expired_trials:
        customer_id = row[0]
        
        # Transition trial → paywalled (idempotent update)
        cursor.execute("""
            UPDATE customers
            SET status = 'paywalled',
                paywalled_since = ?,
                updated_at = ?
            WHERE id = ? AND status = 'trial'
        """, (now_utc.isoformat(), now_utc.isoformat(), customer_id))
        
        # Only add to result if we actually updated (prevents duplicate reporting)
        if cursor.rowcount > 0:
            expired_ids.append(customer_id)
    
    conn.commit()
    return expired_ids


def manually_expire_trial(conn: sqlite3.Connection, customer_id: int) -> bool:
    """Manually expire a trial customer (for testing or admin operations).
    
    Args:
        conn: Database connection
        customer_id: Customer ID to expire
        
    Returns:
        True if customer was transitioned, False if customer was not in trial status
    """
    cursor = conn.cursor()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        UPDATE customers
        SET status = 'paywalled',
            paywalled_since = ?,
            updated_at = ?
        WHERE id = ? AND status = 'trial'
    """, (now_utc, now_utc, customer_id))
    
    conn.commit()
    return cursor.rowcount > 0
