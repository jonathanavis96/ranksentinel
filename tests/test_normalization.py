"""Tests for normalization and diff functions."""

import pytest

from ranksentinel.runner.normalization import (
    diff_summary,
    extract_canonical,
    extract_meta_robots,
    extract_title,
    normalize_html_to_text,
    normalize_robots_txt,
)


class TestExtractTitle:
    def test_extract_title_basic(self):
        html = "<html><head><title>Test Page</title></head></html>"
        assert extract_title(html) == "Test Page"

    def test_extract_title_missing(self):
        html = "<html><head></head></html>"
        assert extract_title(html) == ""

    def test_extract_title_empty(self):
        html = "<html><head><title></title></head></html>"
        assert extract_title(html) == ""

    def test_extract_title_with_whitespace(self):
        html = "<html><head><title>  Test Page  </title></head></html>"
        assert extract_title(html) == "Test Page"


class TestNormalizeRobotsTxt:
    def test_normalize_removes_comments(self):
        content = """# This is a comment
User-agent: *
Disallow: /admin
# Another comment
Allow: /public"""
        normalized = normalize_robots_txt(content)
        assert "# This is a comment" not in normalized
        assert "User-agent: *" in normalized
        assert "Disallow: /admin" in normalized

    def test_normalize_removes_inline_comments(self):
        content = "Disallow: /admin # inline comment"
        normalized = normalize_robots_txt(content)
        assert normalized == "Disallow: /admin"
        assert "# inline comment" not in normalized

    def test_normalize_removes_empty_lines(self):
        content = """User-agent: *

Disallow: /admin

Allow: /public"""
        normalized = normalize_robots_txt(content)
        lines = normalized.splitlines()
        assert "" not in lines

    def test_normalize_preserves_order(self):
        content = """User-agent: *
Disallow: /admin
Allow: /public"""
        normalized = normalize_robots_txt(content)
        lines = normalized.splitlines()
        assert lines[0] == "User-agent: *"
        assert lines[1] == "Disallow: /admin"
        assert lines[2] == "Allow: /public"

    def test_normalize_empty_content(self):
        assert normalize_robots_txt("") == ""
        assert normalize_robots_txt(None) == ""

    def test_normalize_comment_only(self):
        content = """# Only comments
# Nothing else"""
        assert normalize_robots_txt(content) == ""


class TestDiffSummary:
    def test_diff_no_changes(self):
        before = "line1\nline2\nline3"
        after = "line1\nline2\nline3"
        assert diff_summary(before, after) == ""

    def test_diff_additions(self):
        before = "line1\nline2"
        after = "line1\nline2\nline3"
        result = diff_summary(before, after)
        assert "**Added:**" in result
        assert "line3" in result
        assert "**Removed:**" not in result

    def test_diff_removals(self):
        before = "line1\nline2\nline3"
        after = "line1\nline2"
        result = diff_summary(before, after)
        assert "**Removed:**" in result
        assert "line3" in result
        assert "**Added:**" not in result

    def test_diff_additions_and_removals(self):
        before = "line1\nline2"
        after = "line1\nline3"
        result = diff_summary(before, after)
        assert "**Added:**" in result
        assert "line3" in result
        assert "**Removed:**" in result
        assert "line2" in result

    def test_diff_empty_strings(self):
        assert diff_summary("", "") == ""
        assert diff_summary(None, None) == ""

    def test_diff_from_empty(self):
        before = ""
        after = "line1\nline2"
        result = diff_summary(before, after)
        assert "**Added:**" in result
        assert "line1" in result
        assert "line2" in result

    def test_diff_to_empty(self):
        before = "line1\nline2"
        after = ""
        result = diff_summary(before, after)
        assert "**Removed:**" in result
        assert "line1" in result
        assert "line2" in result


class TestRobotsTxtDiffIntegration:
    """Test robots.txt normalization + diff workflow."""

    def test_cosmetic_changes_ignored(self):
        before = """# Comment 1
User-agent: *
Disallow: /admin"""
        after = """# Comment 2 (different)
User-agent: *
Disallow: /admin"""
        normalized_before = normalize_robots_txt(before)
        normalized_after = normalize_robots_txt(after)
        assert diff_summary(normalized_before, normalized_after) == ""

    def test_meaningful_changes_detected(self):
        before = """User-agent: *
Disallow: /admin"""
        after = """User-agent: *
Disallow: /admin
Disallow: /"""
        normalized_before = normalize_robots_txt(before)
        normalized_after = normalize_robots_txt(after)
        result = diff_summary(normalized_before, normalized_after)
        assert "Disallow: /" in result
        assert "**Added:**" in result


class TestTitleDiffIntegration:
    """Test title extraction + diff workflow."""

    def test_title_change_detected(self):
        before = "Old Title"
        after = "New Title"
        result = diff_summary(before, after)
        assert "Old Title" in result
        assert "New Title" in result

    def test_title_unchanged(self):
        title = "Same Title"
        assert diff_summary(title, title) == ""


class TestCanonicalDiffIntegration:
    """Test canonical extraction + diff workflow."""

    def test_canonical_change_detected(self):
        before = "https://example.com/old"
        after = "https://example.com/new"
        result = diff_summary(before, after)
        assert "https://example.com/old" in result
        assert "https://example.com/new" in result

    def test_canonical_unchanged(self):
        url = "https://example.com/page"
        assert diff_summary(url, url) == ""


class TestExtractMetaRobots:
    """Test meta robots tag extraction."""

    def test_extract_meta_robots_basic(self):
        html = '<html><head><meta name="robots" content="noindex, nofollow"></head></html>'
        assert extract_meta_robots(html) == "noindex, nofollow"

    def test_extract_meta_robots_missing(self):
        html = "<html><head></head></html>"
        assert extract_meta_robots(html) == ""

    def test_extract_meta_robots_case_insensitive(self):
        html = '<html><head><meta name="ROBOTS" content="INDEX, FOLLOW"></head></html>'
        assert extract_meta_robots(html) == "INDEX, FOLLOW"

    def test_extract_meta_robots_empty_content(self):
        html = '<html><head><meta name="robots" content=""></head></html>'
        assert extract_meta_robots(html) == ""


class TestExtractCanonical:
    """Test canonical URL extraction."""

    def test_extract_canonical_basic(self):
        html = '<html><head><link rel="canonical" href="https://example.com/page"></head></html>'
        assert extract_canonical(html) == "https://example.com/page"

    def test_extract_canonical_missing(self):
        html = "<html><head></head></html>"
        assert extract_canonical(html) == ""

    def test_extract_canonical_empty_href(self):
        html = '<html><head><link rel="canonical" href=""></head></html>'
        assert extract_canonical(html) == ""

    def test_extract_canonical_with_whitespace(self):
        html = '<html><head><link rel="canonical" href="  https://example.com/page  "></head></html>'
        assert extract_canonical(html) == "https://example.com/page"
