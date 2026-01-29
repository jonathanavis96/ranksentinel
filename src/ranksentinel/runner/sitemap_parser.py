"""Sitemap parsing utilities for URL count extraction."""

import xml.etree.ElementTree as ET
from typing import Any


def list_sitemap_urls(sitemap_xml: str) -> list[str]:
    """Extract list of URLs from sitemap XML.
    
    Supports both sitemap index and urlset formats.
    - For urlset: returns list of <loc> URLs from <url> entries
    - For sitemapindex: returns list of <loc> URLs from <sitemap> entries
    
    Namespace-agnostic: works with sitemaps.org, Google 0.84, or no namespace.
    
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
        
        urls = []
        
        if tag == "sitemapindex":
            # Sitemap index - extract <loc> from <sitemap> entries
            # Use namespace-agnostic search by matching local-name
            for sitemap_elem in root.iter():
                local_name = sitemap_elem.tag.split("}", 1)[1] if "}" in sitemap_elem.tag else sitemap_elem.tag
                if local_name == "sitemap":
                    for loc_elem in sitemap_elem:
                        loc_local = loc_elem.tag.split("}", 1)[1] if "}" in loc_elem.tag else loc_elem.tag
                        if loc_local == "loc" and loc_elem.text:
                            urls.append(loc_elem.text.strip())
            
        elif tag == "urlset":
            # Standard sitemap - extract <loc> from <url> entries
            # Use namespace-agnostic search by matching local-name
            for url_elem in root.iter():
                local_name = url_elem.tag.split("}", 1)[1] if "}" in url_elem.tag else url_elem.tag
                if local_name == "url":
                    for loc_elem in url_elem:
                        loc_local = loc_elem.tag.split("}", 1)[1] if "}" in loc_elem.tag else loc_elem.tag
                        if loc_local == "loc" and loc_elem.text:
                            urls.append(loc_elem.text.strip())
        
        return urls
        
    except ET.ParseError:
        return []
    except Exception:
        return []


def extract_url_count(sitemap_xml: str) -> dict[str, Any]:
    """Extract URL count from sitemap XML.
    
    Supports both sitemap index and urlset formats.
    Namespace-agnostic: works with sitemaps.org, Google 0.84, or no namespace.
    
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
            # Use namespace-agnostic counting by matching local-name
            count = 0
            for elem in root.iter():
                local_name = elem.tag.split("}", 1)[1] if "}" in elem.tag else elem.tag
                if local_name == "sitemap":
                    count += 1
            
            return {
                "url_count": count,
                "sitemap_type": "index",
            }
        elif tag == "urlset":
            # Standard sitemap - count <url> entries
            # Use namespace-agnostic counting by matching local-name
            count = 0
            for elem in root.iter():
                local_name = elem.tag.split("}", 1)[1] if "}" in elem.tag else elem.tag
                if local_name == "url":
                    count += 1
            
            return {
                "url_count": count,
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
