"""
Alert Agent
-----------
The final agentic step — takes action without being asked.

Checks Firebase to see what's already been sent.
Sends new items via WhatsApp (Twilio) or email (Gmail API).
This is what makes the whole system an agent, not a chatbot.
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
        """Format items into a readable WhatsApp/email message."""
        lines = [
            f"📚 PakStudentAlert — {datetime.now().strftime('%d %b %Y')}",
            f"Hey {profile.get('name', 'Student')}! Here's what's new:\n"
        ]

        for item in items:
            urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item.get("urgency", "low"), "📌")
            lines.append(f"{urgency_emoji} *{item['title']}*")
            if item.get("date"):
                lines.append(f"   📅 {item['date']}")
            lines.append(f"   {item.get('details', '')}")
            if item.get("conflict_flagged"):
                lines.append(f"   ⚠️ Note: {item.get('conflict_note', 'Conflicting info found — verify manually')}")
            lines.append("")

        lines.append("— Your PakStudentAlert Agent 🤖")
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
        print(f"  📧 Email sent to {to_email}")

    async def notify(self, items: list[dict], profile: dict):
        """Send alert if there are new items not previously seen."""
        if not items:
            print("  💤 No new relevant items — no alert sent.")
            return

        # Check which items are genuinely new (not sent before)
        new_items = []
        for item in items:
            item_id = item["title"].lower().replace(" ", "_")[:50]
            if not self.db.already_seen(item_id):
                new_items.append(item)
                self.db.mark_seen(item_id)

        if not new_items:
            print("  💤 All items already sent before — no alert sent.")
            return

        print(f"  🔔 {len(new_items)} new items to alert about!")
        message = self._make_message(new_items, profile)

        # Print to console always (useful for development)
        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")

        # Send email if configured
        if self.email_enabled and profile.get("email"):
            self._send_email(message, profile["email"])
