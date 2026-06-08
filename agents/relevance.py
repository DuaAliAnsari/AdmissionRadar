"""
Relevance Agent
---------------
Filters validated items against the student's profile.
Only surfaces what actually matters to THIS student.
"""

import google.generativeai as genai
import json
import os


class RelevanceAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def filter(self, items: list[dict], profile: dict) -> list[dict]:
        """Score each item against the student profile. Return only relevant ones."""
        if not items:
            return []

        prompt = f"""
You are filtering university news/deadlines for a Pakistani student.

Student profile:
{json.dumps(profile, indent=2)}

Items to evaluate:
{json.dumps(items, indent=2)}

For each item, decide if it's relevant to this student.
Score relevance: 0 (irrelevant) to 10 (must see immediately).

Return ONLY a JSON array of items with relevance >= 5, each with a "relevance_score" field added.
Sort by relevance_score descending.
No explanation, just the JSON array.
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
            # Fallback: return all items
            return items
