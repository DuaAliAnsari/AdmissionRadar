import json, re, os
from google import genai

def _strip_fences(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text

class ValidatorAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def _find_conflicts(self, all_items):
        conflicts, seen = [], {}
        for item in all_items:
            key = item["title"].lower()[:40]
            if key in seen:
                conflicts.append((seen[key], item))
            else:
                seen[key] = item
        return conflicts

    async def resolve_conflict(self, item_a, item_b):
        prompt = f"""
Two sources report info about the same topic. Pick the more trustworthy one.
Prefer official university sources over news. Prefer more recent dates.

Item A (from {item_a.get("_source", "?")}): {json.dumps(item_a)}
Item B (from {item_b.get("_source", "?")}): {json.dumps(item_b)}

Return ONLY a single JSON item (the resolved one). No conflict_note unless genuinely ambiguous.
"""
        try:
            response = self.client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
            return json.loads(_strip_fences(response.text))
        except Exception:
            return item_a

    async def validate(self, raw_results):
        all_items = []
        for result in raw_results:
            for item in result.get("items", []):
                item["_source"] = result["source"]
                all_items.append(item)

        print(f"  Validating {len(all_items)} items across sources...")
        conflicts = self._find_conflicts(all_items)
        if conflicts:
            print(f"  ⚠️  Found {len(conflicts)} conflict(s) — resolving...")

        resolved_keys, final_items = set(), []
        for item_a, item_b in conflicts:
            resolved = await self.resolve_conflict(item_a, item_b)
            # Strip internal fields
            resolved.pop("_source", None)
            resolved.pop("conflict_flagged", None)
            resolved.pop("conflict_note", None)
            final_items.append(resolved)
            resolved_keys.add(item_a["title"].lower()[:40])
            resolved_keys.add(item_b["title"].lower()[:40])

        for item in all_items:
            if item["title"].lower()[:40] not in resolved_keys:
                item.pop("_source", None)
                final_items.append(item)

        return final_items