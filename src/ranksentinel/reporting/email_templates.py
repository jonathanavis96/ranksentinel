from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    text: str
    html: str


def render_weekly_digest(
    customer_name: str, findings_md: Iterable[str], schedule_token: str | None = None
) -> EmailMessage:
    subject = f"RankSentinel Weekly Digest — {customer_name}"

    body_md = "\n\n".join(findings_md) if findings_md else "No findings."

    # Add schedule link if token provided
    schedule_link = ""
    if schedule_token:
        schedule_link_text = f"\n\n→ Manage your weekly digest schedule: https://ranksentinel.com/schedule?token={schedule_token}\n"
        schedule_link_html = (
            f"<div style='background: #f5f5f5; border-left: 4px solid #1976d2; padding: 15px; margin: 20px 0; border-radius: 4px;'>"
            f"<strong>→ Manage Schedule:</strong> "
            f"<a href='https://ranksentinel.com/schedule?token={schedule_token}'>Change your weekly digest day/time</a>"
            f"</div>"
        )
    else:
        schedule_link_text = ""
        schedule_link_html = ""

    text = (
        f"Weekly Digest for {customer_name}\n\n"
        "Sections: Critical / Warning / Info\n\n"
        f"{body_md}\n"
        f"{schedule_link_text}"
    )

    html = (
        f"<h1>Weekly Digest — {customer_name}</h1>"
        "<p><strong>Sections:</strong> Critical / Warning / Info</p>"
        f"<pre style='white-space:pre-wrap'>{body_md}</pre>"
        f"{schedule_link_html}"
    )
    return EmailMessage(subject=subject, text=text, html=html)


def render_daily_critical_alert(
    customer_name: str, critical_text: str, critical_html: str
) -> EmailMessage:
    """Render a daily critical alert email with only critical findings.

    Args:
        customer_name: Customer name
        critical_text: Plain text version of critical findings section
        critical_html: HTML version of critical findings section

    Returns:
        EmailMessage with subject, text, and html
    """
    subject = f"🚨 RankSentinel Critical Alert — {customer_name}"

    text = (
        f"CRITICAL ALERT for {customer_name}\n\n"
        "High-severity SEO issues detected during daily monitoring.\n\n"
        f"{critical_text}\n\n"
        "→ Next Steps: Review the issues above and take corrective action immediately.\n"
    )

    html = (
        f"<html><head><style>"
        f"body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}"
        f"h1 {{ color: #d32f2f; border-bottom: 3px solid #d32f2f; padding-bottom: 10px; }}"
        f".alert-banner {{ background: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0; border-radius: 4px; }}"
        f".next-steps {{ background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0; border-radius: 4px; }}"
        f"</style></head><body>"
        f"<h1>🚨 Critical Alert — {customer_name}</h1>"
        f"<div class='alert-banner'>"
        f"<strong>High-severity SEO issues detected during daily monitoring.</strong>"
        f"</div>"
        f"{critical_html}"
        f"<div class='next-steps'>"
        f"<strong>→ Next Steps:</strong> Review the issues above and take corrective action immediately."
        f"</div>"
        f"</body></html>"
    )

    return EmailMessage(subject=subject, text=text, html=html)


def render_first_insight(
    customer_name: str, report_text: str, report_html: str, schedule_token: str | None = None
) -> EmailMessage:
    """Render a First Insight onboarding email.

    Args:
        customer_name: Customer name
        report_text: Plain text version of the report
        report_html: HTML version of the report
        schedule_token: Optional schedule token for passwordless schedule management

    Returns:
        EmailMessage with subject, text, and html
    """
    subject = f"🎉 Your First RankSentinel Insight — {customer_name}"

    # Add schedule link if token provided
    schedule_link_text = ""
    schedule_link_html = ""
    if schedule_token:
        schedule_link_text = f"\n→ Set your weekly digest schedule: https://ranksentinel.com/schedule?token={schedule_token}\n"
        schedule_link_html = (
            f"<div style='background: #f5f5f5; border-left: 4px solid #1976d2; padding: 15px; margin: 20px 0; border-radius: 4px;'>"
            f"<strong>→ Set Schedule:</strong> "
            f"<a href='https://ranksentinel.com/schedule?token={schedule_token}'>Choose your weekly digest day and time</a>"
            f"</div>"
        )

    text = (
        f"Welcome to RankSentinel, {customer_name}!\n\n"
        "We've completed your first site analysis. Here's what we found:\n\n"
        f"{report_text}\n\n"
        f"{schedule_link_text}"
        "→ Next Steps: We'll continue monitoring your site and send weekly digests with any changes or new issues.\n"
    )

    html = (
        f"<html><head><style>"
        f"body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}"
        f"h1 {{ color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px; }}"
        f".welcome-banner {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 15px; margin: 20px 0; border-radius: 4px; }}"
        f".next-steps {{ background: #e8f5e9; border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0; border-radius: 4px; }}"
        f"</style></head><body>"
        f"<h1>🎉 Your First Insight — {customer_name}</h1>"
        f"<div class='welcome-banner'>"
        f"<strong>Welcome to RankSentinel!</strong> We've completed your first site analysis."
        f"</div>"
        f"{report_html}"
        f"{schedule_link_html}"
        f"<div class='next-steps'>"
        f"<strong>→ Next Steps:</strong> We'll continue monitoring your site and send weekly digests with any changes or new issues."
        f"</div>"
        f"</body></html>"
    )

    return EmailMessage(subject=subject, text=text, html=html)


def render_sample_report(domain: str) -> EmailMessage:
    """Render a sample report email for lead capture.

    This is an educational/demo email showing what RankSentinel can detect,
    not an actual analysis of the lead's site.

    Args:
        domain: The domain the lead submitted (for personalization)

    Returns:
        EmailMessage with subject, text, and html
    """
    subject = f"Sample RankSentinel Report for {domain}"

    text = (
        f"Thank you for your interest in RankSentinel!\n\n"
        f"Here's a sample of what we monitor for {domain}:\n\n"
        "═══════════════════════════════════════════════\n"
        "CRITICAL ISSUES WE DETECT\n"
        "═══════════════════════════════════════════════\n\n"
        "• Homepage accidentally set to noindex\n"
        "  → Catches accidental staging flags pushed to production\n\n"
        "• Robots.txt blocking key sections\n"
        "  → Detects when crawlers are blocked from important pages\n\n"
        "• 404 spikes on previously indexed URLs\n"
        "  → Alerts when content disappears unexpectedly\n\n"
        "═══════════════════════════════════════════════\n"
        "WARNING ISSUES WE TRACK\n"
        "═══════════════════════════════════════════════\n\n"
        "• Sitemap URL count drops\n"
        "  → Signals potential crawlability or CMS issues\n\n"
        "• Title tag changes on key pages\n"
        "  → Monitors SEO-critical metadata drift\n\n"
        "• Canonical tag conflicts\n"
        "  → Detects duplicate content signals\n\n"
        "═══════════════════════════════════════════════\n"
        "WEEKLY DIGEST FORMAT\n"
        "═══════════════════════════════════════════════\n\n"
        "You'll receive a weekly summary organized by severity:\n"
        "  → Critical (immediate action needed)\n"
        "  → Warning (investigate soon)\n"
        "  → Info (awareness only)\n\n"
        "Plus daily alerts for critical issues only.\n\n"
        "═══════════════════════════════════════════════\n"
        "READY TO START MONITORING?\n"
        "═══════════════════════════════════════════════\n\n"
        f"→ Start monitoring {domain} now:\n"
        f"  https://ranksentinel.com/schedule\n\n"
        "We'll send your first real insight within 24 hours.\n\n"
        "Questions? Reply to this email.\n"
    )

    html = (
        f"<html><head><style>"
        f"body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}"
        f"h1 {{ color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px; }}"
        f"h2 {{ color: #424242; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; margin-top: 30px; }}"
        f".intro {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 15px; margin: 20px 0; border-radius: 4px; }}"
        f".example-box {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 4px; border-left: 3px solid #757575; }}"
        f".critical {{ border-left-color: #d32f2f; }}"
        f".warning {{ border-left-color: #f57c00; }}"
        f".cta {{ background: #1976d2; color: white; padding: 15px 30px; text-align: center; border-radius: 6px; margin: 30px 0; }}"
        f".cta a {{ color: white; text-decoration: none; font-weight: bold; font-size: 18px; }}"
        f"ul {{ padding-left: 20px; }}"
        f"li {{ margin: 10px 0; }}"
        f"</style></head><body>"
        f"<h1>Sample RankSentinel Report</h1>"
        f"<div class='intro'>"
        f"<strong>Thank you for your interest!</strong> Here's what we monitor for <strong>{domain}</strong>."
        f"</div>"
        f"<h2>Critical Issues We Detect</h2>"
        f"<div class='example-box critical'>"
        f"<ul>"
        f"<li><strong>Homepage accidentally set to noindex</strong><br>"
        f"Catches staging flags pushed to production</li>"
        f"<li><strong>Robots.txt blocking key sections</strong><br>"
        f"Detects when crawlers are blocked from important pages</li>"
        f"<li><strong>404 spikes on indexed URLs</strong><br>"
        f"Alerts when content disappears unexpectedly</li>"
        f"</ul>"
        f"</div>"
        f"<h2>Warning Issues We Track</h2>"
        f"<div class='example-box warning'>"
        f"<ul>"
        f"<li><strong>Sitemap URL count drops</strong><br>"
        f"Signals potential crawlability issues</li>"
        f"<li><strong>Title tag changes on key pages</strong><br>"
        f"Monitors SEO-critical metadata drift</li>"
        f"<li><strong>Canonical tag conflicts</strong><br>"
        f"Detects duplicate content signals</li>"
        f"</ul>"
        f"</div>"
        f"<h2>Weekly Digest Format</h2>"
        f"<div class='example-box'>"
        f"<p>You'll receive a weekly summary organized by severity:</p>"
        f"<ul>"
        f"<li><strong>Critical</strong> — immediate action needed</li>"
        f"<li><strong>Warning</strong> — investigate soon</li>"
        f"<li><strong>Info</strong> — awareness only</li>"
        f"</ul>"
        f"<p>Plus daily alerts for critical issues only.</p>"
        f"</div>"
        f"<div class='cta'>"
        f"<a href='https://ranksentinel.com/schedule'>Start Monitoring {domain} Now →</a>"
        f"</div>"
        f"<p style='text-align: center; color: #757575;'>"
        f"We'll send your first real insight within 24 hours.<br>"
        f"Questions? Reply to this email."
        f"</p>"
        f"</body></html>"
    )

    return EmailMessage(subject=subject, text=text, html=html)
