"""
Validator Agent
---------------
This is what makes the project NOT just RAG.

When two sources report different merit scores or deadlines for the same
thing, this agent uses Gemini to reason about which one to trust,
and flags the conflict clearly to the student.
"""

import google.generativeai as genai
import json
import os


class ValidatorAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _find_conflicts(self, all_items: list[dict]) -> list[tuple]:
        """Find pairs of items that seem to be about the same thing."""
        conflicts = []
        seen_titles = {}

        for item in all_items:
            key = item["title"].lower()[:40]
            if key in seen_titles:
                conflicts.append((seen_titles[key], item))
            else:
                seen_titles[key] = item

        return conflicts

    async def resolve_conflict(self, item_a: dict, item_b: dict) -> dict:
        """Use Gemini to decide which of two conflicting items to trust."""
        prompt = f"""
Two sources report different information about the same topic.
Your job: decide which is more trustworthy and return the resolved item.

Item A (from {item_a.get("_source", "unknown")}):
{json.dumps(item_a, indent=2)}

Item B (from {item_b.get("_source", "unknown")}):
{json.dumps(item_b, indent=2)}

Rules:
- Prefer official sources (HEC, university portals) over news sites
- Prefer more recent dates
- If genuinely uncertain, merge both and flag the conflict

Return ONLY a JSON object:
{{
  "title": "...",
  "type": "...",
  "date": "...",
  "details": "...",
  "urgency": "...",
  "conflict_flagged": true/false,
  "conflict_note": "optional explanation if conflict was flagged"
}}
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception:
            # Fallback: keep item_a
            item_a["conflict_flagged"] = True
            item_a["conflict_note"] = "Could not auto-resolve, showing first source"
            return item_a

    async def validate(self, raw_results: list[dict]) -> list[dict]:
        """Flatten, deduplicate, and resolve conflicts."""

        # Flatten all items, tagging each with its source
        all_items = []
        for result in raw_results:
            for item in result.get("items", []):
                item["_source"] = result["source"]
                all_items.append(item)

        print(f"  Validating {len(all_items)} items across sources...")

        conflicts = self._find_conflicts(all_items)
        if conflicts:
            print(f"  ⚠️  Found {len(conflicts)} potential conflicts — resolving with Gemini...")

        # For each conflict, let Gemini resolve it
        resolved_titles = set()
        final_items = []

        for item_a, item_b in conflicts:
            resolved = await self.resolve_conflict(item_a, item_b)
            final_items.append(resolved)
            resolved_titles.add(item_a["title"].lower()[:40])
            resolved_titles.add(item_b["title"].lower()[:40])

        # Add non-conflicting items
        for item in all_items:
            key = item["title"].lower()[:40]
            if key not in resolved_titles:
                final_items.append(item)

        return final_items
