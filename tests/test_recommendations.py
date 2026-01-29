"""Tests for recommendation rules engine."""

import pytest

from ranksentinel.reporting.recommendations import (
    FindingWithRecommendation,
    get_recommendation_for_finding,
    get_recommendation_priority,
    sort_findings_with_recommendations,
)
from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING


class TestRecommendationRules:
    """Test recommendation mapping for different finding types."""

    def test_noindex_critical_recommendation(self):
        """Noindex findings get specific removal recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Key page noindex detected",
            severity=CRITICAL,
        )
        assert "Remove the noindex directive" in action
        assert "restore search engine visibility" in action

    def test_sitemap_zero_recommendation(self):
        """Sitemap URL count zero gets urgent recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Sitemap URL count dropped to zero",
            severity=CRITICAL,
        )
        assert "Check your sitemap generation process" in action
        assert "immediately" in action

    def test_sitemap_drop_significant_recommendation(self):
        """Significant sitemap drops get review recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Sitemap URL count dropped significantly",
            severity=CRITICAL,
        )
        assert "Review your sitemap configuration" in action

    def test_404_recommendation(self):
        """404 findings get fix/restore recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Page not found (404): https://example.com/page",
            severity=CRITICAL,
        )
        assert "Fix broken links" in action or "restore the missing page" in action

    def test_canonical_disappeared_recommendation(self):
        """Canonical disappearance gets restoration recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Canonical URL disappeared",
            severity=CRITICAL,
        )
        assert "Restore the canonical tag" in action
        assert "duplicate content" in action

    def test_canonical_change_recommendation(self):
        """Canonical changes get review recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Canonical URL changed",
            severity=WARNING,
        )
        assert "Review canonical tag changes" in action

    def test_robots_change_recommendation(self):
        """Robots.txt changes get review recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Robots.txt changed",
            severity=WARNING,
        )
        assert "Review robots.txt changes" in action
        assert "crawlers" in action

    def test_psi_performance_regression_recommendation(self):
        """PSI performance regression gets investigation recommendation."""
        action = get_recommendation_for_finding(
            category="performance",
            title="PSI performance regression (confirmed)",
            severity=CRITICAL,
        )
        assert "Investigate recent code" in action
        assert "performance" in action.lower()

    def test_psi_lcp_regression_recommendation(self):
        """PSI LCP regression gets specific LCP optimization recommendation."""
        action = get_recommendation_for_finding(
            category="performance",
            title="PSI LCP regression (confirmed)",
            severity=CRITICAL,
        )
        assert "largest contentful paint" in action.lower()
        assert "image" in action.lower() or "server response" in action.lower()

    def test_title_disappeared_recommendation(self):
        """Title disappearance gets add title recommendation."""
        action = get_recommendation_for_finding(
            category="content",
            title="Page title disappeared from key page",
            severity=WARNING,
        )
        assert "Add a descriptive title tag" in action

    def test_title_change_recommendation(self):
        """Title changes get review recommendation."""
        action = get_recommendation_for_finding(
            category="content",
            title="Page title changed",
            severity=INFO,
        )
        assert "Review title tag changes" in action

    def test_system_error_recommendation(self):
        """System errors get support contact recommendation."""
        action = get_recommendation_for_finding(
            category="system",
            title="Daily run processing error",
            severity=CRITICAL,
        )
        assert "Contact support" in action

    def test_fallback_recommendation_indexability(self):
        """Unknown indexability findings get generic indexability recommendation."""
        action = get_recommendation_for_finding(
            category="indexability",
            title="Some unknown indexability issue",
            severity=WARNING,
        )
        assert "indexability" in action.lower()
        assert "search engines" in action.lower()

    def test_fallback_recommendation_performance(self):
        """Unknown performance findings get generic performance recommendation."""
        action = get_recommendation_for_finding(
            category="performance",
            title="Some unknown performance issue",
            severity=WARNING,
        )
        assert "performance" in action.lower()

    def test_fallback_recommendation_unknown_category(self):
        """Unknown categories get generic recommendation."""
        action = get_recommendation_for_finding(
            category="unknown_category",
            title="Some issue",
            severity=INFO,
        )
        assert "Review this finding" in action


class TestRecommendationPriority:
    """Test priority assignment for sorting."""

    def test_noindex_high_priority(self):
        """Noindex gets priority 1 (highest impact)."""
        priority = get_recommendation_priority(
            category="indexability",
            title="Key page noindex detected",
            severity=CRITICAL,
        )
        assert priority == 1

    def test_sitemap_zero_high_priority(self):
        """Sitemap zero gets priority 1."""
        priority = get_recommendation_priority(
            category="indexability",
            title="Sitemap URL count dropped to zero",
            severity=CRITICAL,
        )
        assert priority == 1

    def test_404_lower_priority(self):
        """404s get priority 3 (less impact than noindex)."""
        priority = get_recommendation_priority(
            category="indexability",
            title="Page not found (404)",
            severity=CRITICAL,
        )
        assert priority == 3

    def test_unknown_finding_default_priority(self):
        """Unknown findings get default priority 999."""
        priority = get_recommendation_priority(
            category="unknown",
            title="Unknown issue",
            severity=INFO,
        )
        assert priority == 999


class TestSortingStability:
    """Test sorting by severity first, then priority (impact)."""

    def test_sort_by_severity_first(self):
        """Critical findings come before warnings, warnings before info."""
        findings = [
            FindingWithRecommendation(
                finding_id=1,
                customer_id=1,
                severity=INFO,
                category="content",
                title="Page title changed",
                details_md="Details",
                url="https://example.com",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Review title",
                priority=1,
            ),
            FindingWithRecommendation(
                finding_id=2,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Key page noindex detected",
                details_md="Details",
                url="https://example.com",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Remove noindex",
                priority=1,
            ),
            FindingWithRecommendation(
                finding_id=3,
                customer_id=1,
                severity=WARNING,
                category="indexability",
                title="Canonical URL changed",
                details_md="Details",
                url="https://example.com",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Review canonical",
                priority=2,
            ),
        ]

        sorted_findings = sort_findings_with_recommendations(findings)

        assert sorted_findings[0].severity == CRITICAL
        assert sorted_findings[1].severity == WARNING
        assert sorted_findings[2].severity == INFO

    def test_sort_by_priority_within_severity(self):
        """Within same severity, lower priority (higher impact) comes first."""
        findings = [
            FindingWithRecommendation(
                finding_id=1,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Page not found (404)",
                details_md="Details",
                url="https://example.com/page1",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Fix broken links",
                priority=3,  # Lower impact
            ),
            FindingWithRecommendation(
                finding_id=2,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Key page noindex detected",
                details_md="Details",
                url="https://example.com/page2",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Remove noindex",
                priority=1,  # Higher impact
            ),
            FindingWithRecommendation(
                finding_id=3,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Sitemap URL count dropped significantly",
                details_md="Details",
                url=None,
                created_at="2026-01-29T10:00:00Z",
                recommendation="Review sitemap",
                priority=2,  # Medium impact
            ),
        ]

        sorted_findings = sort_findings_with_recommendations(findings)

        # All are CRITICAL, so should be sorted by priority
        assert sorted_findings[0].priority == 1  # noindex (highest impact)
        assert sorted_findings[1].priority == 2  # sitemap drop
        assert sorted_findings[2].priority == 3  # 404

    def test_stable_sort_complex_case(self):
        """Test realistic mixed severity and priority sorting."""
        findings = [
            FindingWithRecommendation(
                finding_id=1,
                customer_id=1,
                severity=INFO,
                category="content",
                title="Page title changed",
                details_md="Details",
                url="https://example.com/1",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Review",
                priority=2,
            ),
            FindingWithRecommendation(
                finding_id=2,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Page not found (404)",
                details_md="Details",
                url="https://example.com/2",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Fix",
                priority=3,
            ),
            FindingWithRecommendation(
                finding_id=3,
                customer_id=1,
                severity=WARNING,
                category="indexability",
                title="Canonical URL disappeared",
                details_md="Details",
                url="https://example.com/3",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Restore",
                priority=1,
            ),
            FindingWithRecommendation(
                finding_id=4,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title="Key page noindex detected",
                details_md="Details",
                url="https://example.com/4",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Remove",
                priority=1,
            ),
            FindingWithRecommendation(
                finding_id=5,
                customer_id=1,
                severity=WARNING,
                category="content",
                title="Page title disappeared",
                details_md="Details",
                url="https://example.com/5",
                created_at="2026-01-29T10:00:00Z",
                recommendation="Add",
                priority=1,
            ),
        ]

        sorted_findings = sort_findings_with_recommendations(findings)

        # Expected order:
        # 1. CRITICAL priority 1 (noindex)
        # 2. CRITICAL priority 3 (404)
        # 3. WARNING priority 1 (canonical disappeared)
        # 4. WARNING priority 1 (title disappeared)
        # 5. INFO priority 2 (title changed)

        assert sorted_findings[0].finding_id == 4  # CRITICAL p1
        assert sorted_findings[1].finding_id == 2  # CRITICAL p3
        assert sorted_findings[2].finding_id in [3, 5]  # WARNING p1 (both)
        assert sorted_findings[3].finding_id in [3, 5]  # WARNING p1 (both)
        assert sorted_findings[4].finding_id == 1  # INFO p2


class TestRecommendationListGeneration:
    """Test generating prioritized recommendation lists from findings."""

    def test_recommendation_list_includes_all_findings(self):
        """Each finding gets a recommendation."""
        findings = [
            FindingWithRecommendation(
                finding_id=i,
                customer_id=1,
                severity=CRITICAL,
                category="indexability",
                title=f"Issue {i}",
                details_md="Details",
                url=f"https://example.com/{i}",
                created_at="2026-01-29T10:00:00Z",
                recommendation=f"Action {i}",
                priority=i,
            )
            for i in range(1, 6)
        ]

        sorted_findings = sort_findings_with_recommendations(findings)

        assert len(sorted_findings) == 5
        # Each finding should have a recommendation
        for finding in sorted_findings:
            assert finding.recommendation
            assert len(finding.recommendation) > 0
