"""
Alert Agent
-----------
Sends email digest. Now shows eligibility status per item.
"""

import os
import json
from datetime import datetime
from tools.firebase_client import FirebaseClient


class AlertAgent:
    def __init__(self, db: FirebaseClient):
        self.db = db
        self.email_enabled = bool(os.getenv("GMAIL_ADDRESS"))

    def _make_message(self, items: list[dict], profile: dict) -> str:
        """Format items into a readable email message."""
        aggregate = None
        matric = profile.get("matric_pct")
        fsc = profile.get("fsc_pct")
        test = profile.get("test_score")
        if matric and fsc and test:
            test_pct = (test / 200) * 100
            aggregate = round((matric * 0.10) + (fsc * 0.40) + (test_pct * 0.50), 2)

        lines = [
            f"PakStudentAlert — {datetime.now().strftime('%d %b %Y')}",
            f"Hey {profile.get('name', 'Student')}! Here's what's new:\n",
        ]

        if aggregate:
            lines.append(f"Your aggregate: {aggregate}% ({profile.get('discipline','CS')} applicant)\n")

        for item in items:
            urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.get("urgency", "low"), "📌")
            lines.append(f"{urgency_emoji} {item['title']}")
            if item.get("date"):
                lines.append(f"   Date: {item['date']}")
            lines.append(f"   {item.get('details', '')}")

            # Show eligibility if available
            elig_status = item.get("eligibility_status", "")
            elig_note = item.get("eligibility_note", "")
            if elig_note:
                elig_emoji = {"strong": "✅", "eligible": "✅", "borderline": "⚠️", "below": "❌"}.get(elig_status, "ℹ️")
                lines.append(f"   {elig_emoji} Eligibility: {elig_note}")

            if item.get("conflict_flagged"):
                lines.append(f"   ⚠️ Note: {item.get('conflict_note', 'Conflicting info found — verify manually')}")
            lines.append("")

        lines.append("— Your PakStudentAlert Agent")
        return "\n".join(lines)

    def _send_email(self, message: str, to_email: str):
        """Send via Gmail SMTP."""
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(message)
        msg["Subject"] = f"PakStudentAlert — {datetime.now().strftime('%d %b %Y')}"
        msg["From"] = os.getenv("GMAIL_ADDRESS")
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"))
            server.send_message(msg)
        print(f"  Email sent to {to_email}")

    async def notify(self, items: list[dict], profile: dict):
        """Send alert if there are new items not previously seen."""
        if not items:
            print("  No new relevant items — no alert sent.")
            return

        new_items = []
        for item in items:
            item_id = item["title"].lower().replace(" ", "_")[:50]
            if not self.db.already_seen(item_id):
                new_items.append(item)
                self.db.mark_seen(item_id)

        if not new_items:
            print("  All items already sent before — no alert sent.")
            return

        print(f"  {len(new_items)} new items to alert about!")
        message = self._make_message(new_items, profile)

        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")

        if self.email_enabled and profile.get("email"):
            self._send_email(message, profile["email"])