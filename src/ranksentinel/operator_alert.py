"""Operator failure alerting for RankSentinel jobs.

Sends alerts to configured operator email when jobs fail, without exposing
customer data or secrets.
"""

import logging
from datetime import datetime, timezone
from typing import Literal

from ranksentinel.config import Settings
from ranksentinel.mailgun import MailgunClient

logger = logging.getLogger(__name__)

RunType = Literal["daily", "weekly"]


def send_operator_alert(
    settings: Settings,
    run_type: RunType,
    error_type: str,
    error_message: str,
    context: dict[str, str] | None = None,
) -> bool:
    """Send a failure alert to the operator email if configured.

    Args:
        settings: Application settings
        run_type: Type of run that failed ('daily' or 'weekly')
        error_type: Error type/category (e.g., 'LockError', 'DatabaseError')
        error_message: Error message (sanitized, no secrets)
        context: Optional additional context (must not contain secrets/PII)

    Returns:
        True if alert was sent successfully (or skipped because no operator email),
        False if sending failed
    """
    operator_email = settings.RANKSENTINEL_OPERATOR_EMAIL.strip()

    # Skip if no operator email configured
    if not operator_email:
        logger.debug("No RANKSENTINEL_OPERATOR_EMAIL configured, skipping operator alert")
        return True

    # Check if Mailgun is configured
    if not settings.MAILGUN_API_KEY or not settings.MAILGUN_DOMAIN:
        logger.warning("Cannot send operator alert: Mailgun not configured")
        return False

    # Build alert content
    timestamp = datetime.now(timezone.utc).isoformat()
    subject = f"[RankSentinel] {run_type.capitalize()} job failure"

    # Text body
    lines = [
        f"RankSentinel {run_type} job failed",
        f"Time: {timestamp}",
        f"Error Type: {error_type}",
        f"Error: {error_message}",
    ]

    if context:
        lines.append("\nContext:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")

    lines.append("\nThis is an automated alert. Check logs for full details.")
    text_body = "\n".join(lines)

    # Send via Mailgun
    try:
        client = MailgunClient(settings)
        success, message_id, error = client.send_email(
            to=operator_email,
            subject=subject,
            text_body=text_body,
        )

        if success:
            logger.info(f"Operator alert sent to {operator_email}, message_id={message_id}")
            return True
        else:
            logger.error(f"Failed to send operator alert: {error}")
            return False

    except Exception as e:
        logger.error(f"Unexpected error sending operator alert: {e}")
        return False
