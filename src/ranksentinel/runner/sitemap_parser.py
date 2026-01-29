"""Sitemap parsing utilities for URL count extraction."""

import xml.etree.ElementTree as ET
from typing import Any


def list_sitemap_urls(sitemap_xml: str) -> list[str]:
    """Extract list of URLs from sitemap XML.
    
    Supports both sitemap index and urlset formats.
    - For urlset: returns list of <loc> URLs from <url> entries
    - For sitemapindex: returns list of <loc> URLs from <sitemap> entries
    
    Args:
        sitemap_xml: Raw XML content of sitemap
        
    Returns:
        List of URL strings. Empty list on parse failure or empty sitemap.
    """
    if not sitemap_xml or not sitemap_xml.strip():
        return []
    
    try:
        root = ET.fromstring(sitemap_xml)
        
        # Remove namespace from tag for easier matching
        tag = root.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = []
        
        if tag == "sitemapindex":
            # Sitemap index - extract <loc> from <sitemap> entries
            sitemaps = root.findall(".//sm:sitemap/sm:loc", ns)
            if not sitemaps:
                # Try without namespace
                sitemaps = root.findall(".//sitemap/loc")
            
            urls = [sitemap.text.strip() for sitemap in sitemaps if sitemap.text]
            
        elif tag == "urlset":
            # Standard sitemap - extract <loc> from <url> entries
            url_locs = root.findall(".//sm:url/sm:loc", ns)
            if not url_locs:
                # Try without namespace
                url_locs = root.findall(".//url/loc")
            
            urls = [loc.text.strip() for loc in url_locs if loc.text]
        
        return urls
        
    except ET.ParseError:
        return []
    except Exception:
        return []


def extract_url_count(sitemap_xml: str) -> dict[str, Any]:
    """Extract URL count from sitemap XML.
    
    Supports both sitemap index and urlset formats.
    
    Args:
        sitemap_xml: Raw XML content of sitemap
        
    Returns:
        Dict with 'url_count' (int) and 'sitemap_type' (str: 'index' or 'urlset')
        Returns {'url_count': 0, 'sitemap_type': 'unknown', 'error': str} on parse failure
    """
    if not sitemap_xml or not sitemap_xml.strip():
        return {"url_count": 0, "sitemap_type": "empty", "error": "Empty sitemap content"}
    
    try:
        root = ET.fromstring(sitemap_xml)
        
        # Remove namespace from tag for easier matching
        tag = root.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        
        if tag == "sitemapindex":
            # Sitemap index - count <sitemap> entries
            # Namespace-aware search
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemaps = root.findall(".//sm:sitemap", ns)
            if not sitemaps:
                # Try without namespace
                sitemaps = root.findall(".//sitemap")
            
            return {
                "url_count": len(sitemaps),
                "sitemap_type": "index",
            }
        elif tag == "urlset":
            # Standard sitemap - count <url> entries
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = root.findall(".//sm:url", ns)
            if not urls:
                # Try without namespace
                urls = root.findall(".//url")
            
            return {
                "url_count": len(urls),
                "sitemap_type": "urlset",
            }
        else:
            return {
                "url_count": 0,
                "sitemap_type": "unknown",
                "error": f"Unknown root tag: {root.tag}",
            }
    except ET.ParseError as e:
        return {
            "url_count": 0,
            "sitemap_type": "parse_error",
            "error": f"XML parse error: {e}",
        }
    except Exception as e:
        return {
            "url_count": 0,
            "sitemap_type": "unknown",
            "error": f"Unexpected error: {e}",
        }
