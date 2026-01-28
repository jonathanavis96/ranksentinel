"""Tests for internal link extraction and broken link detection."""

import pytest

from ranksentinel.runner.link_checker import extract_internal_links, find_broken_links


def test_extract_internal_links_basic():
    """Test basic internal link extraction."""
    html = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="https://example.com/page3">Page 3</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    
    links = extract_internal_links(html, base_url)
    
    assert len(links) == 3
    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://example.com/page3" in links


def test_extract_internal_links_excludes_external():
    """Test that external links are excluded."""
    html = """
    <html>
        <body>
            <a href="/internal">Internal</a>
            <a href="https://external.com/page">External</a>
            <a href="https://example.com/also-internal">Also internal</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    
    links = extract_internal_links(html, base_url)
    
    assert len(links) == 2
    assert "https://example.com/internal" in links
    assert "https://example.com/also-internal" in links
    assert "https://external.com/page" not in links


def test_extract_internal_links_excludes_fragments_and_special():
    """Test that fragments, javascript, mailto, tel links are excluded."""
    html = """
    <html>
        <body>
            <a href="#section">Section</a>
            <a href="javascript:void(0)">JS</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="tel:+1234567890">Phone</a>
            <a href="/valid">Valid</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    
    links = extract_internal_links(html, base_url)
    
    assert len(links) == 1
    assert "https://example.com/valid" in links


def test_extract_internal_links_removes_fragments():
    """Test that URL fragments are removed."""
    html = """
    <html>
        <body>
            <a href="/page#section1">Page Section 1</a>
            <a href="/page#section2">Page Section 2</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    
    links = extract_internal_links(html, base_url)
    
    # Should dedupe to a single URL without fragments
    assert len(links) == 1
    assert "https://example.com/page" in links


def test_extract_internal_links_handles_query_params():
    """Test that query parameters are preserved."""
    html = """
    <html>
        <body>
            <a href="/page?foo=bar">Page with query</a>
            <a href="/page?baz=qux">Page with different query</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    
    links = extract_internal_links(html, base_url)
    
    assert len(links) == 2
    assert "https://example.com/page?foo=bar" in links
    assert "https://example.com/page?baz=qux" in links


def test_extract_internal_links_empty_html():
    """Test with empty HTML."""
    links = extract_internal_links("", "https://example.com")
    assert len(links) == 0


def test_extract_internal_links_no_links():
    """Test with HTML containing no links."""
    html = "<html><body><p>No links here</p></body></html>"
    links = extract_internal_links(html, "https://example.com")
    assert len(links) == 0


def test_extract_internal_links_relative_paths():
    """Test relative path resolution."""
    html = """
    <html>
        <body>
            <a href="page1">Page 1</a>
            <a href="./page2">Page 2</a>
            <a href="../page3">Page 3</a>
        </body>
    </html>
    """
    base_url = "https://example.com/subdir/"
    
    links = extract_internal_links(html, base_url)
    
    assert "https://example.com/subdir/page1" in links
    assert "https://example.com/subdir/page2" in links
    assert "https://example.com/page3" in links


def test_find_broken_links_integration():
    """Test broken link detection with mock scenario.
    
    Note: This is a minimal test. In a real scenario, you'd mock fetch_text
    or use a test server.
    """
    html = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body>
    </html>
    """
    base_url = "https://httpbin.org"
    
    # This will actually make network calls to httpbin.org/page1 and /page2
    # which should return 404s or connection errors
    broken = find_broken_links(base_url, html, max_links_to_check=2, timeout_s=5)
    
    # Expect 2 broken links (404s or errors)
    assert len(broken) == 2
    for target_url, status_code, error_msg in broken:
        # Status code should be either 404 or 0 (connection error)
        assert status_code in (0, 404)
        assert "/page" in target_url
