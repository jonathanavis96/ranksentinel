"""Weekly report composer for RankSentinel.

Generates formatted weekly digest text/HTML from findings with prioritized recommendations.
"""

from dataclasses import dataclass
from typing import Any

from ranksentinel.reporting.recommendations import (
    FindingWithRecommendation,
    get_recommendation_for_finding,
    get_recommendation_priority,
    sort_findings_with_recommendations,
)
from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING, Severity


@dataclass
class CoverageStats:
    """Coverage statistics for a run."""

    sitemap_url: str | None
    total_urls: int | None
    sampled_urls: int | None
    success_count: int | None
    error_count: int | None
    http_429_count: int | None
    http_404_count: int | None


@dataclass
class WeeklyReport:
    """A composed weekly report with sections by severity."""

    customer_name: str
    critical_findings: list[FindingWithRecommendation]
    warning_findings: list[FindingWithRecommendation]
    info_findings: list[FindingWithRecommendation]
    coverage: CoverageStats | None = None
    customer_status: str = "active"  # active, trial, paywalled, previously_interested

    @property
    def critical_count(self) -> int:
        return len(self.critical_findings)

    @property
    def warning_count(self) -> int:
        return len(self.warning_findings)

    @property
    def info_count(self) -> int:
        return len(self.info_findings)

    @property
    def total_count(self) -> int:
        return self.critical_count + self.warning_count + self.info_count

    def to_text(self) -> str:
        """Generate plain text version of the report."""
        lines = []
        lines.append(f"RankSentinel Weekly Digest — {self.customer_name}")
        lines.append("=" * 60)
        lines.append("")

        # Check if this is a paywalled customer
        is_paywalled = self.customer_status in ("paywalled", "previously_interested")

        # Add "All clear" header if no critical or warnings
        if self.critical_count == 0 and self.warning_count == 0:
            lines.append("✓ ALL CLEAR")
            lines.append("")
            lines.append("Great news! No critical issues or warnings detected this week.")
            lines.append("")

        lines.append("Executive Summary")
        lines.append("")
        lines.append(f"- {self.critical_count} Critical")
        lines.append(f"- {self.warning_count} Warnings")
        lines.append(f"- {self.info_count} Info")
        lines.append("")
        lines.append(
            "This report focuses on SEO regressions and high-signal site health issues. "
            "It avoids alert noise by normalizing page content and only escalating high-severity issues."
        )
        lines.append("")

        # Add coverage section
        if self.coverage:
            lines.append("-" * 60)
            lines.append("COVERAGE")
            lines.append("-" * 60)
            lines.append("")
            if self.coverage.sitemap_url:
                lines.append(f"Sitemap: {self.coverage.sitemap_url}")
            if self.coverage.total_urls is not None:
                lines.append(f"Total URLs in sitemap: {self.coverage.total_urls}")
            if self.coverage.sampled_urls is not None:
                lines.append(f"URLs sampled (crawl limit): {self.coverage.sampled_urls}")
            if self.coverage.success_count is not None:
                lines.append(f"Successful fetches: {self.coverage.success_count}")
            if self.coverage.error_count is not None:
                lines.append(f"Failed fetches: {self.coverage.error_count}")
            if self.coverage.http_429_count is not None and self.coverage.http_429_count > 0:
                lines.append(f"Rate limit (429) responses: {self.coverage.http_429_count}")
            if self.coverage.http_404_count is not None and self.coverage.http_404_count > 0:
                lines.append(f"404 responses: {self.coverage.http_404_count}")
            lines.append("")

        if self.critical_findings or (is_paywalled and self.critical_count == 0):
            lines.append("-" * 60)
            lines.append("CRITICAL")
            lines.append("-" * 60)
            lines.append("")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("🔒 LOCKED — Upgrade to see your site's critical issues")
                lines.append("")
                lines.append("Example critical issues we detect:")
                lines.append("• Important page became non-indexable")
                lines.append("• Robots.txt blocking key sections")
                lines.append("• Homepage accidentally set to noindex")
                lines.append("")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.critical_findings, 1):
                    lines.append(f"{idx}) {finding.title}")
                    lines.append("")
                    if finding.url:
                        lines.append(f"   URL: {finding.url}")
                    lines.append(f"   Detected: {finding.created_at}")
                    lines.append("")
                    lines.append(f"   {finding.details_md}")
                    lines.append("")
                    lines.append(f"   → Recommended Action: {finding.recommendation}")
                    lines.append("")

        if self.warning_findings or (is_paywalled and self.warning_count == 0):
            lines.append("-" * 60)
            lines.append("WARNINGS")
            lines.append("-" * 60)
            lines.append("")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("🔒 LOCKED — Upgrade to see your site's warnings")
                lines.append("")
                lines.append("Example warnings we track:")
                lines.append("• Title or canonical changed on a key page")
                lines.append("• Sitemap URL count dropped significantly")
                lines.append("• Page speed score degraded")
                lines.append("")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.warning_findings, 1):
                    lines.append(f"{idx}) {finding.title}")
                    lines.append("")
                    if finding.url:
                        lines.append(f"   URL: {finding.url}")
                    lines.append(f"   Detected: {finding.created_at}")
                    lines.append("")
                    lines.append(f"   {finding.details_md}")
                    lines.append("")
                    lines.append(f"   → Recommended Action: {finding.recommendation}")
                    lines.append("")

        if self.info_findings or (is_paywalled and self.info_count == 0):
            lines.append("-" * 60)
            lines.append("INFO")
            lines.append("-" * 60)
            lines.append("")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("🔒 LOCKED — Upgrade to see informational updates")
                lines.append("")
                lines.append("Example info updates we monitor:")
                lines.append("• Content changed since last snapshot")
                lines.append("• New pages added to sitemap")
                lines.append("• Minor metadata updates")
                lines.append("")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.info_findings, 1):
                    lines.append(f"{idx}) {finding.title}")
                    lines.append("")
                    if finding.url:
                        lines.append(f"   URL: {finding.url}")
                    lines.append(f"   Detected: {finding.created_at}")
                    lines.append("")
                    lines.append(f"   {finding.details_md}")
                    lines.append("")
                    lines.append(f"   → Recommended Action: {finding.recommendation}")
                    lines.append("")

        return "\n".join(lines)

    def to_html(self) -> str:
        """Generate HTML version of the report."""
        is_paywalled = self.customer_status in ("paywalled", "previously_interested")
        
        lines = []
        lines.append("<html><head><style>")
        lines.append(
            "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }"
        )
        lines.append(
            "h1 { color: #1a1a1a; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }"
        )
        lines.append("h2 { color: #333; margin-top: 40px; }")
        lines.append(
            ".all-clear { background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 8px; }"
        )
        lines.append(".all-clear h2 { margin-top: 0; color: #2e7d32; }")
        lines.append(
            ".summary { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }"
        )
        lines.append(".summary ul { margin: 10px 0; }")
        lines.append(
            ".finding { background: #fff; border-left: 4px solid #ddd; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }"
        )
        lines.append(".finding.critical { border-left-color: #d32f2f; }")
        lines.append(".finding.warning { border-left-color: #f57c00; }")
        lines.append(".finding.info { border-left-color: #1976d2; }")
        lines.append(".finding h3 { margin-top: 0; color: #1a1a1a; }")
        lines.append(".meta { color: #666; font-size: 0.9em; margin: 10px 0; }")
        lines.append(".details { margin: 15px 0; line-height: 1.6; }")
        lines.append(
            ".recommendation { background: #e8f5e9; border-radius: 4px; padding: 12px; margin-top: 15px; }"
        )
        lines.append(".recommendation strong { color: #2e7d32; }")
        lines.append(
            ".locked { background: #fff3cd; border-left: 4px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 8px; filter: blur(3px); }"
        )
        lines.append(
            ".locked-label { background: #fff3cd; border-left: 4px solid #ff9800; padding: 15px; margin: 10px 0 20px 0; border-radius: 8px; font-weight: bold; }"
        )
        lines.append("</style></head><body>")

        lines.append(f"<h1>RankSentinel Weekly Digest — {self.customer_name}</h1>")

        # Add "All clear" banner if no critical or warnings
        if self.critical_count == 0 and self.warning_count == 0:
            lines.append("<div class='all-clear'>")
            lines.append("<h2>✓ All Clear</h2>")
            lines.append("<p>Great news! No critical issues or warnings detected this week.</p>")
            lines.append("</div>")

        lines.append("<div class='summary'>")
        lines.append("<strong>Executive Summary</strong>")
        lines.append("<ul>")
        lines.append(f"<li><strong>{self.critical_count}</strong> Critical</li>")
        lines.append(f"<li><strong>{self.warning_count}</strong> Warnings</li>")
        lines.append(f"<li><strong>{self.info_count}</strong> Info</li>")
        lines.append("</ul>")
        lines.append(
            "<p>This report focuses on SEO regressions and high-signal site health issues. "
            "It avoids alert noise by normalizing page content and only escalating high-severity issues.</p>"
        )
        lines.append("</div>")

        # Add coverage section
        if self.coverage:
            lines.append("<div class='summary'>")
            lines.append("<strong>Coverage</strong>")
            lines.append("<ul>")
            if self.coverage.sitemap_url:
                lines.append(
                    f"<li><strong>Sitemap:</strong> <code>{self.coverage.sitemap_url}</code></li>"
                )
            if self.coverage.total_urls is not None:
                lines.append(
                    f"<li><strong>Total URLs in sitemap:</strong> {self.coverage.total_urls}</li>"
                )
            if self.coverage.sampled_urls is not None:
                lines.append(
                    f"<li><strong>URLs sampled (crawl limit):</strong> {self.coverage.sampled_urls}</li>"
                )
            if self.coverage.success_count is not None:
                lines.append(
                    f"<li><strong>Successful fetches:</strong> {self.coverage.success_count}</li>"
                )
            if self.coverage.error_count is not None:
                lines.append(
                    f"<li><strong>Failed fetches:</strong> {self.coverage.error_count}</li>"
                )
            if self.coverage.http_429_count is not None and self.coverage.http_429_count > 0:
                lines.append(
                    f"<li><strong>Rate limit (429) responses:</strong> {self.coverage.http_429_count}</li>"
                )
            if self.coverage.http_404_count is not None and self.coverage.http_404_count > 0:
                lines.append(
                    f"<li><strong>404 responses:</strong> {self.coverage.http_404_count}</li>"
                )
            lines.append("</ul>")
            lines.append("</div>")

        if self.critical_findings or (is_paywalled and self.critical_count == 0):
            lines.append("<h2>Critical</h2>")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("<div class='locked-label'>🔒 LOCKED — Upgrade to see your site's critical issues</div>")
                lines.append("<div class='locked'>")
                lines.append("<h3>Example: Important page became non-indexable</h3>")
                lines.append("<div class='meta'>")
                lines.append("<div><strong>URL:</strong> <code>https://example.com/important-page</code></div>")
                lines.append("<div><strong>Detected:</strong> 2024-01-15 08:30:00</div>")
                lines.append("</div>")
                lines.append("<div class='details'>Meta robots tag changed from 'index,follow' to 'noindex'. This will remove the page from search results.</div>")
                lines.append("<div class='recommendation'><strong>→ Recommended Action:</strong> Review robots/noindex/canonical settings</div>")
                lines.append("</div>")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.critical_findings, 1):
                    lines.append("<div class='finding critical'>")
                    lines.append(f"<h3>{idx}) {finding.title}</h3>")
                    lines.append("<div class='meta'>")
                    if finding.url:
                        lines.append(f"<div><strong>URL:</strong> <code>{finding.url}</code></div>")
                    lines.append(f"<div><strong>Detected:</strong> {finding.created_at}</div>")
                    lines.append("</div>")
                    lines.append(f"<div class='details'>{finding.details_md}</div>")
                    lines.append(
                        f"<div class='recommendation'><strong>→ Recommended Action:</strong> {finding.recommendation}</div>"
                    )
                    lines.append("</div>")

        if self.warning_findings or (is_paywalled and self.warning_count == 0):
            lines.append("<h2>Warnings</h2>")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("<div class='locked-label'>🔒 LOCKED — Upgrade to see your site's warnings</div>")
                lines.append("<div class='locked'>")
                lines.append("<h3>Example: Title or canonical changed on a key page</h3>")
                lines.append("<div class='meta'>")
                lines.append("<div><strong>URL:</strong> <code>https://example.com/product-page</code></div>")
                lines.append("<div><strong>Detected:</strong> 2024-01-15 08:30:00</div>")
                lines.append("</div>")
                lines.append("<div class='details'>Page title changed from 'Best Product 2024' to 'Product - Site'. Canonical URL also updated.</div>")
                lines.append("<div class='recommendation'><strong>→ Recommended Action:</strong> Review metadata changes for SEO impact</div>")
                lines.append("</div>")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.warning_findings, 1):
                    lines.append("<div class='finding warning'>")
                    lines.append(f"<h3>{idx}) {finding.title}</h3>")
                    lines.append("<div class='meta'>")
                    if finding.url:
                        lines.append(f"<div><strong>URL:</strong> <code>{finding.url}</code></div>")
                    lines.append(f"<div><strong>Detected:</strong> {finding.created_at}</div>")
                    lines.append("</div>")
                    lines.append(f"<div class='details'>{finding.details_md}</div>")
                    lines.append(
                        f"<div class='recommendation'><strong>→ Recommended Action:</strong> {finding.recommendation}</div>"
                    )
                    lines.append("</div>")

        if self.info_findings or (is_paywalled and self.info_count == 0):
            lines.append("<h2>Info</h2>")
            if is_paywalled:
                # Show locked examples for paywalled customers
                lines.append("<div class='locked-label'>🔒 LOCKED — Upgrade to see informational updates</div>")
                lines.append("<div class='locked'>")
                lines.append("<h3>Example: Content changed since last snapshot</h3>")
                lines.append("<div class='meta'>")
                lines.append("<div><strong>URL:</strong> <code>https://example.com/blog-post</code></div>")
                lines.append("<div><strong>Detected:</strong> 2024-01-15 08:30:00</div>")
                lines.append("</div>")
                lines.append("<div class='details'>Page content updated. Word count changed by 15%. H1 tag unchanged.</div>")
                lines.append("<div class='recommendation'><strong>→ Recommended Action:</strong> Review content for consistency</div>")
                lines.append("</div>")
            else:
                # Show real findings for active/trial customers
                for idx, finding in enumerate(self.info_findings, 1):
                    lines.append("<div class='finding info'>")
                    lines.append(f"<h3>{idx}) {finding.title}</h3>")
                    lines.append("<div class='meta'>")
                    if finding.url:
                        lines.append(f"<div><strong>URL:</strong> <code>{finding.url}</code></div>")
                    lines.append(f"<div><strong>Detected:</strong> {finding.created_at}</div>")
                    lines.append("</div>")
                    lines.append(f"<div class='details'>{finding.details_md}</div>")
                    lines.append(
                        f"<div class='recommendation'><strong>→ Recommended Action:</strong> {finding.recommendation}</div>"
                    )
                    lines.append("</div>")

        lines.append("</body></html>")
        return "\n".join(lines)


def parse_severity(severity_str: str) -> Severity:
    """Parse severity string to Severity object."""
    if severity_str == "critical":
        return CRITICAL
    elif severity_str == "warning":
        return WARNING
    elif severity_str == "info":
        return INFO
    else:
        return INFO  # Default to INFO for unknown severities


def compose_daily_critical_report(customer_name: str, findings_rows: list[Any]) -> WeeklyReport:
    """Compose a daily critical report from database findings rows.

    Similar to compose_weekly_report but intended for daily critical alerts.
    Uses the same WeeklyReport structure for consistency.

    Args:
        customer_name: Customer name for the report
        findings_rows: List of sqlite3.Row objects from findings table (critical severity only)

    Returns:
        WeeklyReport with only critical findings populated
    """
    # Convert rows to FindingWithRecommendation objects
    findings_with_recs: list[FindingWithRecommendation] = []

    for row in findings_rows:
        severity = parse_severity(row["severity"])
        category = row["category"]
        title = row["title"]

        # Get recommendation and priority
        recommendation = get_recommendation_for_finding(category, title, severity)
        priority = get_recommendation_priority(category, title, severity)

        findings_with_recs.append(
            FindingWithRecommendation(
                finding_id=row["id"],
                customer_id=row["customer_id"],
                severity=severity,
                category=category,
                title=title,
                details_md=row["details_md"],
                url=row["url"] if row["url"] else None,
                created_at=row["created_at"],
                recommendation=recommendation,
                priority=priority,
            )
        )

    # Sort findings by priority
    sorted_findings = sort_findings_with_recommendations(findings_with_recs)

    # Only critical findings for daily alerts
    critical_findings = [f for f in sorted_findings if f.severity == CRITICAL]

    return WeeklyReport(
        customer_name=customer_name,
        critical_findings=critical_findings,
        warning_findings=[],
        info_findings=[],
    )


def compose_weekly_report(
    customer_name: str, findings_rows: list[Any], coverage: CoverageStats | None = None,
    customer_status: str = "active"
) -> WeeklyReport:
    """Compose a weekly report from database findings rows.

    Args:
        customer_name: Customer name for the report
        findings_rows: List of sqlite3.Row objects from findings table
        coverage: Optional coverage statistics for this run
        customer_status: Customer status (active, trial, paywalled, previously_interested)

    Returns:
        WeeklyReport with sorted findings by severity and priority
    """
    # Convert rows to FindingWithRecommendation objects
    findings_with_recs: list[FindingWithRecommendation] = []

    for row in findings_rows:
        severity = parse_severity(row["severity"])
        category = row["category"]
        title = row["title"]

        # Get recommendation and priority
        recommendation = get_recommendation_for_finding(category, title, severity)
        priority = get_recommendation_priority(category, title, severity)

        findings_with_recs.append(
            FindingWithRecommendation(
                finding_id=row["id"],
                customer_id=row["customer_id"],
                severity=severity,
                category=category,
                title=title,
                details_md=row["details_md"],
                url=row["url"] if row["url"] else None,
                created_at=row["created_at"],
                recommendation=recommendation,
                priority=priority,
            )
        )

    # Sort findings by severity and priority
    sorted_findings = sort_findings_with_recommendations(findings_with_recs)

    # Split into severity sections
    critical_findings = [f for f in sorted_findings if f.severity == CRITICAL]
    warning_findings = [f for f in sorted_findings if f.severity == WARNING]
    info_findings = [f for f in sorted_findings if f.severity == INFO]

    return WeeklyReport(
        customer_name=customer_name,
        critical_findings=critical_findings,
        warning_findings=warning_findings,
        info_findings=info_findings,
        coverage=coverage,
        customer_status=customer_status,
    )
