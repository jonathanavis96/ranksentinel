"""Tests for sitemap URL count extraction and delta detection."""

from ranksentinel.runner.sitemap_parser import extract_url_count


class TestSitemapUrlCountExtraction:
    """Test URL count extraction from various sitemap formats."""

    def test_urlset_basic(self):
        """Test basic urlset sitemap."""
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
        result = extract_url_count(xml)
        assert result["url_count"] == 3
        assert result["sitemap_type"] == "urlset"
        assert "error" not in result

    def test_urlset_google_084_namespace(self):
        """Test urlset with Google 0.84 namespace."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.google.com/schemas/sitemap/0.84">
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
        result = extract_url_count(xml)
        assert result["url_count"] == 3
        assert result["sitemap_type"] == "urlset"
        assert "error" not in result

    def test_sitemapindex_basic(self):
        """Test sitemap index format."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap2.xml</loc>
  </sitemap>
</sitemapindex>"""
        result = extract_url_count(xml)
        assert result["url_count"] == 2
        assert result["sitemap_type"] == "index"
        assert "error" not in result

    def test_urlset_no_namespace(self):
        """Test urlset without namespace."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/page1</loc>
  </url>
</urlset>"""
        result = extract_url_count(xml)
        assert result["url_count"] == 1
        assert result["sitemap_type"] == "urlset"

    def test_empty_urlset(self):
        """Test empty urlset."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
        result = extract_url_count(xml)
        assert result["url_count"] == 0
        assert result["sitemap_type"] == "urlset"

    def test_empty_content(self):
        """Test empty content."""
        result = extract_url_count("")
        assert result["url_count"] == 0
        assert result["sitemap_type"] == "empty"
        assert "error" in result

    def test_invalid_xml(self):
        """Test malformed XML."""
        xml = "<urlset><url><loc>broken"
        result = extract_url_count(xml)
        assert result["url_count"] == 0
        assert result["sitemap_type"] == "parse_error"
        assert "error" in result

    def test_unknown_root_tag(self):
        """Test unknown root element."""
        xml = """<?xml version="1.0"?>
<unknown>
  <data>test</data>
</unknown>"""
        result = extract_url_count(xml)
        assert result["url_count"] == 0
        assert result["sitemap_type"] == "unknown"
        assert "error" in result

    def test_large_urlset(self):
        """Test large urlset."""
        urls = "\n".join(
            [f"  <url><loc>https://example.com/page{i}</loc></url>" for i in range(1000)]
        )
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
        result = extract_url_count(xml)
        assert result["url_count"] == 1000
        assert result["sitemap_type"] == "urlset"
