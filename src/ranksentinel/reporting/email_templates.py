from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EmailMessage:
    subject: str
    text: str
    html: str


def render_weekly_digest(customer_name: str, findings_md: Iterable[str]) -> EmailMessage:
    subject = f"RankSentinel Weekly Digest — {customer_name}"

    body_md = "

".join(findings_md) if findings_md else "No findings."

    text = (
        f"Weekly Digest for {customer_name}

"
        "Sections: Critical / Warning / Info

"
        f"{body_md}
"
    )

    html = (
        f"<h1>Weekly Digest — {customer_name}</h1>"
        "<p><strong>Sections:</strong> Critical / Warning / Info</p>"
        f"<pre style='white-space:pre-wrap'>{body_md}</pre>"
    )
    return EmailMessage(subject=subject, text=text, html=html)
