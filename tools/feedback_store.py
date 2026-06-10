"""
Feedback Store
--------------
Stores user feedback (thumbs up/down) on alert items.
Uses local JSON in dev mode, Firebase in production.
The Relevance agent reads this history to improve scoring over time.
"""

import json
import os
from pathlib import Path
from datetime import datetime


class FeedbackStore:
    def __init__(self):
        self.use_firebase = bool(os.getenv("FIREBASE_PROJECT_ID"))

        if self.use_firebase:
            import firebase_admin
            from firebase_admin import credentials, firestore
            if not firebase_admin._apps:
                cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        else:
            self.local_path = Path("data/feedback.json")
            self.local_path.parent.mkdir(exist_ok=True)
            if not self.local_path.exists():
                self.local_path.write_text("[]")

    def _load(self) -> list:
        return json.loads(self.local_path.read_text())

    def _save(self, data: list):
        self.local_path.write_text(json.dumps(data, indent=2))

    def record(self, item_title: str, item_source: str, item_type: str,
               vote: str, profile_discipline: str):
        """
        Record a thumbs up or down on an item.
        vote: "up" or "down"
        """
        entry = {
            "title": item_title,
            "source": item_source,
            "type": item_type,
            "vote": vote,
            "discipline": profile_discipline,
            "timestamp": datetime.now().isoformat(),
        }

        if self.use_firebase:
            self.db.collection("feedback").add(entry)
        else:
            data = self._load()
            data.append(entry)
            self._save(data)

    def get_summary(self, discipline: str, limit: int = 30) -> dict:
        """
        Return a summary of recent feedback for the Relevance agent to use.
        Returns: {liked_types: [...], disliked_types: [...], liked_sources: [...]}
        """
        if self.use_firebase:
            docs = (self.db.collection("feedback")
                    .where("discipline", "==", discipline)
                    .order_by("timestamp", direction="DESCENDING")
                    .limit(limit).stream())
            entries = [d.to_dict() for d in docs]
        else:
            all_entries = self._load()
            entries = [e for e in all_entries if e.get("discipline") == discipline][-limit:]

        if not entries:
            return {}

        liked   = [e for e in entries if e["vote"] == "up"]
        disliked = [e for e in entries if e["vote"] == "down"]

        def top(items, key, n=3):
            from collections import Counter
            return [k for k, _ in Counter(i[key] for i in items).most_common(n)]

        return {
            "liked_types":    top(liked, "type"),
            "disliked_types": top(disliked, "type"),
            "liked_sources":  top(liked, "source"),
            "disliked_sources": top(disliked, "source"),
            "total_feedback": len(entries),
        }

    def get_all(self) -> list:
        if self.use_firebase:
            return [d.to_dict() for d in self.db.collection("feedback").stream()]
        return self._load()