"""Tests for robots.txt parser and crawl gate."""

from ranksentinel.runner.robots import RobotsCrawlGate, create_crawl_gate


def test_robots_gate_allows_all_when_empty():
    """Empty robots.txt should allow all URLs."""
    gate = create_crawl_gate("https://example.com", "")

    assert gate.can_fetch("https://example.com/")
    assert gate.can_fetch("https://example.com/page1")
    assert gate.can_fetch("https://example.com/admin/")


def test_robots_gate_respects_disallow_rules(robots_simple):
    """Crawl gate should respect Disallow directives."""
    gate = create_crawl_gate("https://example.com", robots_simple)

    # /admin/ should be blocked
    assert not gate.can_fetch("https://example.com/admin/")
    assert not gate.can_fetch("https://example.com/admin/settings")

    # Other paths should be allowed
    assert gate.can_fetch("https://example.com/")
    assert gate.can_fetch("https://example.com/page1")
    assert gate.can_fetch("https://example.com/public/")


def test_robots_gate_blocks_site_wide_disallow(robots_restrictive):
    """Disallow: / should block entire site."""
    gate = create_crawl_gate("https://example.com", robots_restrictive)

    assert not gate.can_fetch("https://example.com/")
    assert not gate.can_fetch("https://example.com/page1")
    assert not gate.can_fetch("https://example.com/admin/")


def test_robots_gate_allows_when_not_loaded():
    """Gate should allow all URLs when robots.txt not loaded."""
    gate = RobotsCrawlGate("https://example.com")

    # No robots.txt loaded yet
    assert not gate.is_loaded
    assert gate.can_fetch("https://example.com/")
    assert gate.can_fetch("https://example.com/admin/")


def test_robots_gate_ignores_different_domain():
    """Gate should allow URLs from different domains."""
    gate = create_crawl_gate("https://example.com", "User-agent: *\nDisallow: /")

    # Different domain should be allowed (not our concern)
    assert gate.can_fetch("https://other-domain.com/")
    assert gate.can_fetch("https://other-domain.com/admin/")


def test_robots_gate_filters_url_list():
    """filter_urls should return only allowed URLs."""
    robots_content = """User-agent: *
Disallow: /private/
Disallow: /admin/
"""
    gate = create_crawl_gate("https://example.com", robots_content)

    urls = [
        "https://example.com/",
        "https://example.com/page1",
        "https://example.com/private/data",
        "https://example.com/admin/settings",
        "https://example.com/public/info",
    ]

    allowed = gate.filter_urls(urls)

    assert "https://example.com/" in allowed
    assert "https://example.com/page1" in allowed
    assert "https://example.com/public/info" in allowed
    assert "https://example.com/private/data" not in allowed
    assert "https://example.com/admin/settings" not in allowed


def test_robots_gate_with_comments_and_whitespace(robots_with_comments):
    """Parser should handle comments and whitespace correctly."""
    gate = create_crawl_gate("https://example.com", robots_with_comments)

    # Should parse actual directives, ignoring comments
    assert not gate.can_fetch("https://example.com/admin/")
    assert gate.can_fetch("https://example.com/public/")


def test_robots_gate_mixed_case_user_agent():
    """Parser should handle mixed case in User-agent."""
    robots_content = """User-Agent: Googlebot
Disallow: /private/

User-agent: *
Disallow: /admin/
"""
    gate = create_crawl_gate("https://example.com", robots_content)

    # Default user-agent should match *
    assert not gate.can_fetch("https://example.com/admin/")
    assert gate.can_fetch("https://example.com/private/")


def test_robots_gate_fixture_requirement():
    """Test AC requirement: /private should be blocked by fixture robots rules."""
    # This is the specific test case from the AC
    robots_content = """User-agent: *
Disallow: /private
"""
    gate = create_crawl_gate("https://example.com", robots_content)

    # URLs under /private should be blocked
    assert not gate.can_fetch("https://example.com/private")
    assert not gate.can_fetch("https://example.com/private/")
    assert not gate.can_fetch("https://example.com/private/data")

    # Other URLs should be allowed
    assert gate.can_fetch("https://example.com/")
    assert gate.can_fetch("https://example.com/public")


def test_create_crawl_gate_factory():
    """Test factory function creates properly initialized gate."""
    robots_content = "User-agent: *\nDisallow: /admin/"

    gate = create_crawl_gate("https://example.com", robots_content, user_agent="TestBot")

    assert gate.base_url == "https://example.com"
    assert gate.user_agent == "TestBot"
    assert gate.is_loaded is True
    assert not gate.can_fetch("https://example.com/admin/")


def test_create_crawl_gate_with_none_content():
    """Factory function should handle None robots content gracefully."""
    gate = create_crawl_gate("https://example.com", None)

    assert not gate.is_loaded
    # Should allow all when not loaded
    assert gate.can_fetch("https://example.com/admin/")
