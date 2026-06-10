"""
Alert Agent
-----------
Formats and displays new items to the user.
Tracks what's been shown before so you don't see duplicates.
"""

import json
from datetime import datetime
from pathlib import Path


class AlertAgent:
    def __init__(self):
        self.seen_path = Path("data/seen_alerts.json")
        self.seen_path.parent.mkdir(exist_ok=True)
        if not self.seen_path.exists():
            self.seen_path.write_text("{}")

    def _load_seen(self) -> dict:
        return json.loads(self.seen_path.read_text())

    def _save_seen(self, data: dict):
        self.seen_path.write_text(json.dumps(data, indent=2))

    def _already_seen(self, item_id: str) -> bool:
        return item_id in self._load_seen()

    def _mark_seen(self, item_id: str):
        data = self._load_seen()
        data[item_id] = datetime.now().isoformat()
        self._save_seen(data)

    def _format(self, items: list[dict], profile: dict) -> str:
        aggregate = profile.get("aggregate_pct")
        lines = [
            f"PakStudentAlert — {datetime.now().strftime('%d %b %Y')}",
            f"Hey {profile.get('name', 'Student')}! Here's what's new:\n",
        ]
        if aggregate:
            lines.append(f"Your aggregate: {aggregate}% ({profile.get('discipline','CS')} applicant)\n")

        for item in items:
            urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                item.get("urgency", "low").split(" ")[0].lower(), "📌"
            )
            lines.append(f"{urgency_emoji} {item['title']}")
            if item.get("date"):
                lines.append(f"   📅 {item['date']}")
            lines.append(f"   {item.get('details', '')}")
            if item.get("eligibility_note"):
                elig_emoji = {"strong": "✅", "eligible": "✅", "borderline": "⚠️", "below": "❌"}.get(
                    item.get("eligibility_status", ""), "ℹ️"
                )
                lines.append(f"   {elig_emoji} {item['eligibility_note']}")
            if item.get("conflict_flagged"):
                lines.append(f"   ⚠️ {item.get('conflict_note', 'Conflicting sources — verify manually')}")
            lines.append("")

        return "\n".join(lines)

    async def notify(self, items: list[dict], profile: dict):
        if not items:
            print("  💤 No relevant items found.")
            return

        new_items = []
        for item in items:
            item_id = item["title"].lower().replace(" ", "_")[:50]
            if not self._already_seen(item_id):
                new_items.append(item)
                self._mark_seen(item_id)

        if not new_items:
            print("  💤 Nothing new since last run.")
            return

        print(f"  🔔 {len(new_items)} new items!")
        print("\n" + "="*50)
        print(self._format(new_items, profile))
        print("="*50 + "\n")