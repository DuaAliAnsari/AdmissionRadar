"""
Firebase Client
---------------
Tracks which alerts have already been sent so we don't spam the student.
In development mode (no Firebase credentials), uses a local JSON file instead.
"""

import json
import os
from pathlib import Path


class FirebaseClient:
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
            # Dev mode: use local JSON file
            self.local_path = Path("data/seen_alerts.json")
            self.local_path.parent.mkdir(exist_ok=True)
            if not self.local_path.exists():
                self.local_path.write_text("{}")
            print("  ℹ️  Firebase not configured — using local storage (dev mode)")

    def _load_local(self) -> dict:
        return json.loads(self.local_path.read_text())

    def _save_local(self, data: dict):
        self.local_path.write_text(json.dumps(data, indent=2))

    def already_seen(self, item_id: str) -> bool:
        """Check if this alert was already sent."""
        if self.use_firebase:
            doc = self.db.collection("seen_alerts").document(item_id).get()
            return doc.exists
        else:
            return item_id in self._load_local()

    def mark_seen(self, item_id: str):
        """Mark this alert as sent."""
        from datetime import datetime
        if self.use_firebase:
            self.db.collection("seen_alerts").document(item_id).set(
                {"seen_at": datetime.now().isoformat()}
            )
        else:
            data = self._load_local()
            data[item_id] = datetime.now().isoformat()
            self._save_local(data)
