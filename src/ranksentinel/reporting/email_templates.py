from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    text: str
    html: str


def render_weekly_digest(customer_name: str, findings_md: Iterable[str]) -> EmailMessage:
    subject = f"RankSentinel Weekly Digest — {customer_name}"

    body_md = "\n\n".join(findings_md) if findings_md else "No findings."

    text = (
        f"Weekly Digest for {customer_name}\n\n"
        "Sections: Critical / Warning / Info\n\n"
        f"{body_md}\n"
    )

    html = (
        f"<h1>Weekly Digest — {customer_name}</h1>"
        "<p><strong>Sections:</strong> Critical / Warning / Info</p>"
        f"<pre style='white-space:pre-wrap'>{body_md}</pre>"
    )
    return EmailMessage(subject=subject, text=text, html=html)


def render_daily_critical_alert(customer_name: str, critical_text: str, critical_html: str) -> EmailMessage:
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
