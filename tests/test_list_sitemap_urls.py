"""Tests for list_sitemap_urls function."""

import pytest

from ranksentinel.runner.sitemap_parser import list_sitemap_urls


class TestListSitemapUrls:
    """Test URL list extraction from various sitemap formats."""

    def test_urlset_basic(self):
        """Test basic urlset sitemap returns URLs."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
  <url>
    <loc>https://example.com/page3</loc>
  </url>
</urlset>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 3
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result
        assert "https://example.com/page3" in result

    def test_sitemapindex_basic(self):
        """Test sitemap index returns sitemap URLs."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap2.xml</loc>
  </sitemap>
</sitemapindex>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 2
        assert "https://example.com/sitemap1.xml" in result
        assert "https://example.com/sitemap2.xml" in result

    def test_urlset_no_namespace(self):
        """Test urlset without namespace."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/page1</loc>
  </url>
</urlset>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 1
        assert result[0] == "https://example.com/page1"

    def test_sitemapindex_no_namespace(self):
        """Test sitemap index without namespace."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex>
  <sitemap>
    <loc>https://example.com/sitemap1.xml</loc>
  </sitemap>
</sitemapindex>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 1
        assert result[0] == "https://example.com/sitemap1.xml"

    def test_empty_urlset(self):
        """Test empty urlset returns empty list."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
        result = list_sitemap_urls(xml)
        assert result == []

    def test_empty_content(self):
        """Test empty content returns empty list."""
        result = list_sitemap_urls("")
        assert result == []

    def test_invalid_xml(self):
        """Test malformed XML returns empty list."""
        xml = "<urlset><url><loc>broken"
        result = list_sitemap_urls(xml)
        assert result == []

    def test_unknown_root_tag(self):
        """Test unknown root element returns empty list."""
        xml = """<?xml version="1.0"?>
<unknown>
  <data>test</data>
</unknown>"""
        result = list_sitemap_urls(xml)
        assert result == []

    def test_urlset_with_whitespace(self):
        """Test URLs with whitespace are stripped."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>  https://example.com/page1  </loc>
  </url>
</urlset>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 1
        assert result[0] == "https://example.com/page1"

    def test_urlset_with_empty_loc(self):
        """Test URL entries with empty or missing loc are skipped."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
  </url>
  <url>
    <loc></loc>
  </url>
  <url>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
</urlset>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 2
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result

    def test_large_urlset(self):
        """Test large urlset returns all URLs."""
        urls_xml = "\n".join(
            [
                f'  <url><loc>https://example.com/page{i}</loc></url>'
                for i in range(100)
            ]
        )
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>"""
        result = list_sitemap_urls(xml)
        assert len(result) == 100
        assert "https://example.com/page0" in result
        assert "https://example.com/page99" in result
