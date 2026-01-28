"""Internal link extraction and broken link detection."""

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ranksentinel.http_client import fetch_text


def extract_internal_links(html: str, base_url: str) -> list[str]:
    """Extract internal links from HTML content.
    
    Args:
        html: HTML content to parse
        base_url: Base URL of the page for resolving relative links
        
    Returns:
        List of absolute internal URLs (same domain as base_url)
    """
    if not html or not base_url:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    internal_links = set()
    
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        
        # Skip empty, anchor-only, javascript, mailto, tel links
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        
        # Resolve relative URLs to absolute
        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        
        # Only include same-domain links (internal)
        if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
            # Remove fragment
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            internal_links.add(clean_url)
    
    return sorted(internal_links)


def check_link_status(url: str, timeout_s: int = 10) -> tuple[int, str]:
    """Check the HTTP status of a link.
    
    Args:
        url: URL to check
        timeout_s: Timeout in seconds
        
    Returns:
        Tuple of (status_code, error_message). 
        Status code is 0 if request failed completely.
    """
    result = fetch_text(url, timeout=timeout_s, attempts=2, base_delay=1.0)
    
    if result.is_error:
        return (0, f"{result.error_type}: {result.error}")
    
    return (result.status_code or 0, "")


def find_broken_links(
    source_url: str,
    html: str,
    max_links_to_check: int = 50,
    timeout_s: int = 10,
) -> list[tuple[str, int, str]]:
    """Find broken internal links in HTML content.
    
    Args:
        source_url: The URL of the page being analyzed
        html: HTML content of the page
        max_links_to_check: Maximum number of links to check (to avoid blowups)
        timeout_s: Timeout per link check
        
    Returns:
        List of tuples: (target_url, status_code, error_message)
        Only includes links with 4xx/5xx status or connection errors.
    """
    internal_links = extract_internal_links(html, source_url)
    
    # Cap the number of links to check
    links_to_check = internal_links[:max_links_to_check]
    
    broken = []
    for link in links_to_check:
        status_code, error_msg = check_link_status(link, timeout_s)
        
        # Consider broken if: 4xx, 5xx, or connection error (status_code=0)
        if status_code == 0 or status_code >= 400:
            broken.append((link, status_code, error_msg))
    
    return broken
