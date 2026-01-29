"""Recommendation rules engine for RankSentinel findings.

Maps finding types to actionable recommendations based on category and title patterns.
Provides stable sorting by severity and impact.
"""

from dataclasses import dataclass

from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING, Severity


@dataclass(frozen=True)
class Recommendation:
    """A recommended action for a finding."""

    finding_category: str
    finding_title_pattern: str
    action: str
    priority: int  # Lower number = higher priority within same severity


# Recommendation rules mapping
# Order matters: first match wins for each finding
RECOMMENDATION_RULES: list[Recommendation] = [
    # Indexability - Critical
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="noindex",
        action="Remove the noindex directive from key pages to restore search engine visibility.",
        priority=1,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Sitemap URL count dropped to zero",
        action="Check your sitemap generation process immediately - all URLs have disappeared.",
        priority=1,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Sitemap URL count dropped significantly",
        action="Review your sitemap configuration to ensure pages are not being accidentally excluded.",
        priority=2,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Sitemap unreachable",
        action="Verify your sitemap URL is accessible and properly configured.",
        priority=2,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="404",
        action="Fix broken links or restore the missing page to prevent SEO impact.",
        priority=3,
    ),
    # Indexability - Warning/Info
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Canonical URL disappeared",
        action="Restore the canonical tag to prevent duplicate content issues.",
        priority=1,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Canonical URL",
        action="Review canonical tag changes to ensure they align with your SEO strategy.",
        priority=2,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Sitemap URL count decreased",
        action="Monitor sitemap URL count changes and investigate if unexpected.",
        priority=3,
    ),
    Recommendation(
        finding_category="indexability",
        finding_title_pattern="Robots.txt changed",
        action="Review robots.txt changes to ensure crawlers can access important pages.",
        priority=2,
    ),
    # Performance - Critical
    Recommendation(
        finding_category="performance",
        finding_title_pattern="PSI performance regression",
        action="Investigate recent code or asset changes that may have degraded page performance.",
        priority=1,
    ),
    Recommendation(
        finding_category="performance",
        finding_title_pattern="PSI LCP regression",
        action="Optimize largest contentful paint - check image sizes, server response times, and render-blocking resources.",
        priority=1,
    ),
    # Content - Warning/Info
    Recommendation(
        finding_category="content",
        finding_title_pattern="Page title disappeared",
        action="Add a descriptive title tag to improve SEO and click-through rates.",
        priority=1,
    ),
    Recommendation(
        finding_category="content",
        finding_title_pattern="Page title",
        action="Review title tag changes to ensure they remain optimized for search.",
        priority=2,
    ),
    # System errors - Critical
    Recommendation(
        finding_category="system",
        finding_title_pattern="processing error",
        action="Contact support - the monitoring system encountered an error.",
        priority=1,
    ),
]


def get_recommendation_for_finding(
    category: str, title: str, severity: Severity
) -> str:
    """Get actionable recommendation for a finding.

    Args:
        category: Finding category (e.g., "indexability", "performance")
        title: Finding title
        severity: Severity object (CRITICAL, WARNING, INFO)

    Returns:
        Recommendation action text
    """
    # Find first matching rule
    title_lower = title.lower()
    for rule in RECOMMENDATION_RULES:
        if rule.finding_category == category and rule.finding_title_pattern.lower() in title_lower:
            return rule.action

    # Default fallback by category
    if category == "indexability":
        return "Review this indexability issue to ensure search engines can discover and crawl your content."
    elif category == "performance":
        return "Investigate performance changes and optimize as needed."
    elif category == "content":
        return "Review content changes to ensure they align with your SEO strategy."
    else:
        return "Review this finding and take appropriate action."


def get_recommendation_priority(category: str, title: str, severity: Severity) -> int:
    """Get priority for a finding (used for sorting within same severity).

    Args:
        category: Finding category
        title: Finding title
        severity: Severity object

    Returns:
        Priority integer (lower = higher priority)
    """
    title_lower = title.lower()
    for rule in RECOMMENDATION_RULES:
        if rule.finding_category == category and rule.finding_title_pattern.lower() in title_lower:
            return rule.priority

    # Default priority
    return 999


@dataclass
class FindingWithRecommendation:
    """Finding with its recommendation and sort keys."""

    finding_id: int
    customer_id: int
    severity: Severity
    category: str
    title: str
    details_md: str
    url: str | None
    created_at: str
    recommendation: str
    priority: int

    @property
    def severity_rank(self) -> int:
        """Severity rank for sorting (lower = more severe)."""
        if self.severity == CRITICAL:
            return 1
        elif self.severity == WARNING:
            return 2
        elif self.severity == INFO:
            return 3
        else:
            return 999


def sort_findings_with_recommendations(
    findings: list[FindingWithRecommendation],
) -> list[FindingWithRecommendation]:
    """Sort findings by severity first, then priority (impact).

    Args:
        findings: List of findings with recommendations

    Returns:
        Sorted list (most severe and highest impact first)
    """
    return sorted(findings, key=lambda f: (f.severity_rank, f.priority))
