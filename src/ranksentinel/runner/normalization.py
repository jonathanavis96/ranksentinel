import re
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup


NOISE_CLASS_ID_SUBSTRINGS = ("cookie", "consent", "gdpr")


def normalize_url(base_url: str, url: str) -> str:
    """Normalize a URL to a canonical form.
    
    Handles:
    - Resolving relative URLs against base_url
    - Lowercasing scheme and hostname
    - Stripping fragments
    - Normalizing trailing slash (removes for paths, keeps for domain-only)
    - Preserving query strings
    
    Args:
        base_url: Base URL for resolving relative URLs
        url: URL to normalize (can be relative or absolute)
        
    Returns:
        Normalized absolute URL string
    """
    if not url:
        return ""
    
    # Resolve relative URLs to absolute
    absolute_url = urljoin(base_url, url.strip())
    
    # Parse the URL
    parsed = urlparse(absolute_url)
    
    # Only handle http/https schemes
    if parsed.scheme not in ("http", "https"):
        return ""
    
    # Normalize scheme and netloc to lowercase
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query
    
    # Strip fragment
    fragment = ""
    
    # Normalize trailing slash: remove from paths, keep for domain-only
    if path and path != "/":
        path = path.rstrip("/")
    elif not path:
        path = "/"
    
    # Reconstruct the URL
    normalized = urlunparse((scheme, netloc, path, "", query, fragment))
    
    return normalized


def normalize_html_to_text(html: str) -> str:
    """Normalize HTML to a stable text representation to reduce alert noise."""
    soup = BeautifulSoup(html or "", "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for tag_name in ["nav", "header", "footer"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for tag in soup.find_all(True):
        attrs = " ".join([str(tag.get("id", "")), " ".join(tag.get("class", []) or [])]).lower()
        if any(s in attrs for s in NOISE_CLASS_ID_SUBSTRINGS):
            tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\\s+", " ", text).strip()

    text = re.sub(r"\\b\\d{4}-\\d{2}-\\d{2}\\b", "<DATE>", text)
    text = re.sub(r"\\b\\d{2}:\\d{2}(:\\d{2})?\\b", "<TIME>", text)
    return text


def extract_meta_robots(html: str) -> str:
    """Extract meta robots tag content.

    Returns the content attribute value, or empty string if not present.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    meta_robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.IGNORECASE)})
    if meta_robots and meta_robots.get("content"):
        return str(meta_robots.get("content")).strip()
    return ""


def extract_canonical(html: str) -> str:
    """Extract canonical URL from link rel=canonical.

    Returns the href attribute value, or empty string if not present.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        return str(canonical.get("href")).strip()
    return ""


def extract_title(html: str) -> str:
    """Extract page title from <title> tag.

    Returns the title text content, or empty string if not present.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    title = soup.find("title")
    if title and title.string:
        return str(title.string).strip()
    return ""


def normalize_robots_txt(content: str) -> str:
    """Normalize robots.txt content to ignore cosmetic differences.

    - Strips whitespace
    - Removes comment-only lines
    - Preserves directive order (order matters in robots.txt)
    """
    lines = []
    for line in (content or "").splitlines():
        line = line.strip()
        # Skip empty lines and comment-only lines
        if not line or line.startswith("#"):
            continue
        # Remove inline comments (preserve directive, remove comment)
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if line:  # Only add if there's content after removing comments
            lines.append(line)
    return "\n".join(lines)


def diff_summary(before: str, after: str, label: str = "content") -> str:
    """Generate a human-readable diff summary.

    Returns a markdown-formatted diff showing additions and removals.
    """
    before_lines = set((before or "").splitlines())
    after_lines = set((after or "").splitlines())

    added = after_lines - before_lines
    removed = before_lines - after_lines

    if not added and not removed:
        return ""

    parts = []
    if removed:
        parts.append("**Removed:**\n```\n" + "\n".join(sorted(removed)) + "\n```")
    if added:
        parts.append("**Added:**\n```\n" + "\n".join(sorted(added)) + "\n```")

    return "\n\n".join(parts)
