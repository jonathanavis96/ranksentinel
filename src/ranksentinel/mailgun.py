"""Mailgun email client with delivery logging."""

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Literal

import requests

from ranksentinel.config import Settings
from ranksentinel.db import execute

logger = logging.getLogger(__name__)

DeliveryStatus = Literal["sent", "skipped", "failed"]


class MailgunError(Exception):
    """Raised when Mailgun API returns an error."""
    pass


class MailgunClient:
    """Client for sending emails via Mailgun API."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.MAILGUN_API_KEY
        self.domain = settings.MAILGUN_DOMAIN
        self.from_address = settings.MAILGUN_FROM
        
        if not self.api_key or not self.domain:
            raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN must be configured")
    
    def send_email(
        self,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
        timeout: float = 30.0,
    ) -> tuple[bool, str | None, str | None]:
        """Send an email via Mailgun API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            text_body: Plain text email body
            html_body: HTML email body (optional)
            timeout: Request timeout in seconds
        
        Returns:
            Tuple of (success, provider_message_id, error_message)
        """
        url = f"https://api.mailgun.net/v3/{self.domain}/messages"
        
        data = {
            "from": self.from_address,
            "to": to,
            "subject": subject,
            "text": text_body,
        }
        
        if html_body:
            data["html"] = html_body
        
        try:
            response = requests.post(
                url,
                auth=("api", self.api_key),
                data=data,
                timeout=timeout,
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("id", "")
                logger.info(f"Email sent successfully to {to}, message_id={message_id}")
                return (True, message_id, None)
            else:
                error_msg = f"Mailgun API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return (False, None, error_msg)
        
        except requests.Timeout as e:
            error_msg = f"Mailgun request timeout: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        
        except requests.RequestException as e:
            error_msg = f"Mailgun request error: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error sending email: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)


def log_delivery(
    conn: sqlite3.Connection,
    customer_id: int,
    run_type: Literal["daily", "weekly"],
    recipient: str,
    subject: str,
    status: DeliveryStatus,
    provider_message_id: str | None = None,
    error: str | None = None,
) -> int:
    """Record an email delivery attempt in the deliveries table.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
        recipient: Email recipient address
        subject: Email subject line
        status: Delivery status ('sent', 'skipped', 'failed')
        provider_message_id: Mailgun message ID (if sent successfully)
        error: Error message (if failed)
    
    Returns:
        ID of the inserted delivery row
    """
    sent_at = datetime.now(timezone.utc).isoformat()
    
    return execute(
        conn,
        "INSERT INTO deliveries(customer_id, run_type, sent_at, recipient, subject, "
        "provider, provider_message_id, status, error) VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, run_type, sent_at, recipient, subject, "mailgun", 
         provider_message_id, status, error),
    )


def send_and_log(
    conn: sqlite3.Connection,
    client: MailgunClient,
    customer_id: int,
    run_type: Literal["daily", "weekly"],
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> bool:
    """Send an email and log the delivery attempt.
    
    This is a convenience function that combines send_email and log_delivery.
    
    Args:
        conn: Database connection
        client: MailgunClient instance
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
        recipient: Email recipient address
        subject: Email subject line
        text_body: Plain text email body
        html_body: HTML email body (optional)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    success, message_id, error = client.send_email(
        to=recipient,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
    
    status: DeliveryStatus = "sent" if success else "failed"
    
    log_delivery(
        conn=conn,
        customer_id=customer_id,
        run_type=run_type,
        recipient=recipient,
        subject=subject,
        status=status,
        provider_message_id=message_id,
        error=error,
    )
    
    return success
