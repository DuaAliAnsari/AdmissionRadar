"""
Planner Agent
-------------
Takes the student profile and decides which sources to check today.
Now discipline-aware: CS student gets CS university URLs,
medical student gets medical university URLs, etc.
"""

import google.generativeai as genai
import json
import os
from data.universities import get_unis_for_discipline, UNIVERSITIES, get_all_admission_urls

# Static sources always checked regardless of discipline
ALWAYS_CHECK = [
    {"name": "HEC Announcements",  "url": "https://www.hec.gov.pk/english/news/Pages/default.aspx",  "type": "news"},
    {"name": "Dawn Education",     "url": "https://www.dawn.com/education",                           "type": "news"},
]


class PlannerAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _build_sources_for_profile(self, profile: dict) -> list[dict]:
        """Build source list based on discipline and target universities."""
        discipline = profile.get("discipline", "CS")
        target_unis = profile.get("universities", [])

        # Get relevant universities for this discipline
        relevant_unis = get_unis_for_discipline(discipline)

        # If student has specific target unis, prioritize those
        if target_unis:
            priority = [u for u in target_unis if u in UNIVERSITIES]
            others = [u for u in relevant_unis if u not in priority]
            ordered = priority + others
        else:
            ordered = relevant_unis

        # Build source list from university knowledge base
        sources = list(ALWAYS_CHECK)
        for uni_name in ordered:
            uni = UNIVERSITIES.get(uni_name)
            if uni:
                sources.append({
                    "name": f"{uni_name} Admissions",
                    "url": uni["admission_url"],
                    "type": "admission",
                    "university": uni_name,
                })

        return sources

    async def plan(self, profile: dict, query: str = None) -> list[dict]:
        """
        Given the student profile, decide which sources to check.
        Returns a filtered list of sources relevant to this student.
        """
        all_sources = self._build_sources_for_profile(profile)

        # If it's a one-off query, let Gemini decide which subset matters
        if query:
            prompt = f"""
You are a planner for a Pakistani student information agent.

Student profile:
{json.dumps(profile, indent=2)}

Available sources:
{json.dumps(all_sources, indent=2)}

User query: {query}

Pick only the sources most relevant to answering this query.
Return ONLY a JSON array of source objects. No explanation.
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
                pass

        # For scheduled runs, return all relevant sources (cap at 15)
        return all_sources[:15]