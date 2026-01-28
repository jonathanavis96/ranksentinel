import re

from bs4 import BeautifulSoup


NOISE_CLASS_ID_SUBSTRINGS = ("cookie", "consent", "gdpr")


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
