"""Robots.txt parser and crawl gate for polite crawling.

This module provides functionality to:
- Parse robots.txt files into allow/deny rules
- Check if URLs can be crawled based on robots.txt rules
- Provide a crawl gate for filtering URL lists

Uses Python's standard urllib.robotparser.RobotFileParser for RFC-compliant parsing.
"""
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


class RobotsCrawlGate:
    """Robots.txt-based crawl gate for filtering URLs before fetch.
    
    This class wraps urllib.robotparser.RobotFileParser to provide a simple
    interface for checking if URLs are allowed to be crawled.
    
    Attributes:
        base_url: Base URL (scheme + netloc) for the robots.txt file
        user_agent: User agent string to match against robots.txt rules
        parser: RobotFileParser instance for rule checking
        is_loaded: Whether robots.txt content has been loaded
    """
    
    def __init__(self, base_url: str, user_agent: str = "*"):
        """Initialize the crawl gate.
        
        Args:
            base_url: Base URL (e.g., "https://example.com")
            user_agent: User agent to match against robots.txt rules (default: "*")
        """
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.parser = RobotFileParser()
        self.is_loaded = False
    
    def load_robots_txt(self, robots_content: str) -> None:
        """Load and parse robots.txt content.
        
        Args:
            robots_content: Raw robots.txt file content
        """
        # RobotFileParser expects to parse from a URL or file-like object
        # We'll parse line-by-line manually
        lines = (robots_content or "").splitlines()
        self.parser.parse(lines)
        self.is_loaded = True
    
    def can_fetch(self, url: str) -> bool:
        """Check if a URL can be fetched according to robots.txt rules.
        
        If robots.txt hasn't been loaded, returns True (allow by default).
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL can be fetched, False otherwise
        """
        if not self.is_loaded:
            # If robots.txt not loaded, allow by default (conservative approach)
            return True
        
        # Ensure URL is from the same base domain
        parsed = urlparse(url)
        url_base = f"{parsed.scheme}://{parsed.netloc}"
        if url_base != self.base_url:
            # Different domain, allow (not our concern)
            return True
        
        return self.parser.can_fetch(self.user_agent, url)
    
    def filter_urls(self, urls: list[str]) -> list[str]:
        """Filter a list of URLs, keeping only those allowed by robots.txt.
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            List of URLs that are allowed to be crawled
        """
        return [url for url in urls if self.can_fetch(url)]


def create_crawl_gate(base_url: str, robots_content: str | None, user_agent: str = "*") -> RobotsCrawlGate:
    """Factory function to create and initialize a crawl gate.
    
    Args:
        base_url: Base URL (e.g., "https://example.com")
        robots_content: Robots.txt content, or None if not available
        user_agent: User agent string (default: "*")
        
    Returns:
        Initialized RobotsCrawlGate instance
    """
    gate = RobotsCrawlGate(base_url, user_agent)
    if robots_content:
        gate.load_robots_txt(robots_content)
    return gate
