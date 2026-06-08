"""
Planner Agent
-------------
Takes the student profile and decides which sources to check today.
Uses Gemini to reason about what's most likely to have changed.
"""

import google.generativeai as genai
import json
import os

# All sources the agent knows about
ALL_SOURCES = [
    {"name": "HEC Scholarships",       "url": "https://www.hec.gov.pk/english/scholarshipsDetail/Pages/Indigenous.aspx", "type": "scholarship"},
    {"name": "HEC Announcements",      "url": "https://www.hec.gov.pk/english/news/Pages/default.aspx",                  "type": "news"},
    {"name": "FAST NUCES Admissions",  "url": "https://admissions.nu.edu.pk/",                                            "type": "admission"},
    {"name": "NUST Admissions",        "url": "https://admission.nust.edu.pk/",                                           "type": "admission"},
    {"name": "LUMS Admissions",        "url": "https://admission.lums.edu.pk/",                                           "type": "admission"},
    {"name": "UET Lahore Admissions",  "url": "https://www.uet.edu.pk/admissions/",                                       "type": "admission"},
    {"name": "Dawn Education",         "url": "https://www.dawn.com/education",                                           "type": "news"},
]


class PlannerAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def plan(self, profile: dict, query: str = None) -> list[dict]:
        """
        Given the student profile, decide which sources to check.
        Returns a filtered list of sources relevant to this student.
        """

        prompt = f"""
You are a planner for a Pakistani student information agent.

Student profile:
{json.dumps(profile, indent=2)}

Available sources:
{json.dumps(ALL_SOURCES, indent=2)}

{"User query: " + query if query else "This is a scheduled daily check."}

Task: Decide which sources are worth checking for THIS student today.
Consider:
- Their target universities and programs
- Whether they care about scholarships, admissions, or both
- Which sources are most likely to have new info

Return ONLY a JSON array of source objects to check. No explanation.
Example: [{{"name": "...", "url": "...", "type": "..."}}]
        """

        response = self.model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: return all sources
            return ALL_SOURCES
