"""HTTP client wrapper with retry, timeout, and error classification.

This module provides a consistent HTTP fetch layer for all network operations.
Features:
- Configurable timeouts and retries with exponential backoff
- Error classification (timeout, dns, connection, http_4xx, http_5xx)
- User-Agent header
- Redirect handling
- Gzip support (automatic via requests)
"""

import time
from enum import Enum
from typing import Any

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    RequestException,
    Timeout,
)


class ErrorType(str, Enum):
    """HTTP error classification."""

    TIMEOUT = "timeout"
    DNS = "dns"
    CONNECTION = "connection"
    HTTP_4XX = "http_4xx"
    HTTP_5XX = "http_5xx"
    UNKNOWN = "unknown"


class FetchResult:
    """Result of an HTTP fetch operation."""

    def __init__(
        self,
        status_code: int | None = None,
        final_url: str | None = None,
        body: str | bytes | None = None,
        redirect_chain: list[str] | None = None,
        error: str | None = None,
        error_type: ErrorType | None = None,
    ):
        self.status_code = status_code
        self.final_url = final_url
        self.body = body
        self.redirect_chain = redirect_chain or []
        self.error = error
        self.error_type = error_type

    @property
    def ok(self) -> bool:
        """Returns True if the request was successful (2xx status)."""
        return self.status_code is not None and 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Returns True if an error occurred."""
        return self.error is not None


def classify_error(exc: Exception) -> ErrorType:
    """Classify a requests exception into an error type."""
    if isinstance(exc, Timeout):
        return ErrorType.TIMEOUT
    if isinstance(exc, ConnectionError):
        # Check for DNS-specific errors
        if "Name or service not known" in str(exc) or "getaddrinfo failed" in str(exc):
            return ErrorType.DNS
        return ErrorType.CONNECTION
    if isinstance(exc, HTTPError):
        if hasattr(exc, "response") and exc.response is not None:
            if 400 <= exc.response.status_code < 500:
                return ErrorType.HTTP_4XX
            if 500 <= exc.response.status_code < 600:
                return ErrorType.HTTP_5XX
    return ErrorType.UNKNOWN


def fetch_with_retry(
    url: str,
    timeout: int = 20,
    attempts: int = 3,
    base_delay: float = 1.0,
    user_agent: str = "RankSentinel/0.1",
    allow_redirects: bool = True,
    return_bytes: bool = False,
) -> FetchResult:
    """Fetch a URL with retry logic and error classification.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        attempts: Number of retry attempts
        base_delay: Base delay for exponential backoff (seconds)
        user_agent: User-Agent header value
        allow_redirects: Whether to follow redirects
        return_bytes: If True, return body as bytes; otherwise as string

    Returns:
        FetchResult with status, final URL, body, redirect chain, and error info
    """
    last_error = None
    last_error_type = None

    for attempt in range(attempts):
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                allow_redirects=allow_redirects,
                headers={"User-Agent": user_agent},
            )

            # Build redirect chain
            redirect_chain = [r.url for r in resp.history] + [resp.url]

            # Check for HTTP errors (4xx, 5xx)
            if resp.status_code >= 400:
                error_type = (
                    ErrorType.HTTP_4XX if resp.status_code < 500 else ErrorType.HTTP_5XX
                )
                return FetchResult(
                    status_code=resp.status_code,
                    final_url=resp.url,
                    body=resp.content if return_bytes else resp.text,
                    redirect_chain=redirect_chain,
                    error=f"HTTP {resp.status_code}",
                    error_type=error_type,
                )

            # Success case
            body = resp.content if return_bytes else resp.text
            return FetchResult(
                status_code=resp.status_code,
                final_url=resp.url,
                body=body,
                redirect_chain=redirect_chain,
            )

        except RequestException as e:
            last_error = str(e)
            last_error_type = classify_error(e)

            # Don't retry on 4xx errors (client errors)
            if last_error_type == ErrorType.HTTP_4XX:
                return FetchResult(
                    error=last_error,
                    error_type=last_error_type,
                )

            # Log retry attempt
            if attempt < attempts - 1:
                delay = base_delay * (2**attempt)
                time.sleep(delay)

    # All retries exhausted
    return FetchResult(
        error=last_error or "Unknown error",
        error_type=last_error_type or ErrorType.UNKNOWN,
    )


def fetch_text(
    url: str,
    timeout: int = 20,
    attempts: int = 3,
    base_delay: float = 1.0,
) -> FetchResult:
    """Fetch a URL and return text content.

    Convenience wrapper around fetch_with_retry for text responses.
    """
    return fetch_with_retry(
        url=url,
        timeout=timeout,
        attempts=attempts,
        base_delay=base_delay,
        return_bytes=False,
    )


def fetch_bytes(
    url: str,
    timeout: int = 20,
    attempts: int = 3,
    base_delay: float = 1.0,
) -> FetchResult:
    """Fetch a URL and return binary content.

    Convenience wrapper around fetch_with_retry for binary responses.
    """
    return fetch_with_retry(
        url=url,
        timeout=timeout,
        attempts=attempts,
        base_delay=base_delay,
        return_bytes=True,
    )
