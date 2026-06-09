"""
Relevance Agent
---------------
Filters validated items against the student's profile.
Now does REAL eligibility filtering:
- Computes student aggregate
- Compares against historical merit ranges
- Flags "you're eligible", "borderline", or "below cutoff"
"""

import google.generativeai as genai
import json
import os
from data.universities import get_university


def compute_aggregate(profile: dict) -> float | None:
    """
    Compute student aggregate % from their scores.
    Different universities use different formulas — we use the most common one.
    Standard formula (used by FAST, COMSATS, etc.):
        Aggregate = (Matric% * 0.10) + (FSc% * 0.40) + (TestScore/200 * 100 * 0.50)
    """
    if profile.get("aggregate_pct"):
        return profile["aggregate_pct"]

    matric = profile.get("matric_pct")
    fsc = profile.get("fsc_pct")
    test = profile.get("test_score")

    if not all([matric, fsc, test]):
        return None

    test_type = profile.get("test_type", "NET")

    # Normalize test score to percentage based on test type
    test_max = {"NET": 200, "ECAT": 400, "MDCAT": 200, "SAT": 1600}.get(test_type, 200)
    test_pct = (test / test_max) * 100

    aggregate = (matric * 0.10) + (fsc * 0.40) + (test_pct * 0.50)
    return round(aggregate, 2)


def check_eligibility(aggregate: float, uni_name: str, program: str) -> dict:
    """Check if student is eligible for a specific program at a university."""
    uni = get_university(uni_name)
    if not uni:
        return {"status": "unknown", "note": "University not in knowledge base"}

    programs = uni.get("programs", {})
    prog_info = programs.get(program)
    if not prog_info:
        # Try to find closest program
        for p_key, p_info in programs.items():
            prog_info = p_info
            program = p_key
            break

    if not prog_info:
        return {"status": "unknown", "note": "Program info not available"}

    low, high = prog_info["merit_range"]

    if aggregate >= high - 2:
        return {"status": "strong", "note": f"Well above typical cutoff ({low}-{high}%)"}
    elif aggregate >= low:
        return {"status": "eligible", "note": f"Within merit range ({low}-{high}%)"}
    elif aggregate >= low - 3:
        return {"status": "borderline", "note": f"Slightly below typical cutoff ({low}-{high}%) — borderline"}
    else:
        return {"status": "below", "note": f"Below typical cutoff ({low}-{high}%)"}


class RelevanceAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def filter(self, items: list[dict], profile: dict) -> list[dict]:
        """Score each item against the student profile. Return only relevant ones."""
        if not items:
            return []

        # Compute student aggregate for eligibility checks
        aggregate = compute_aggregate(profile)
        eligibility_context = ""
        if aggregate:
            eligibility_context = f"\nStudent aggregate: {aggregate}% (computed from their scores)"

        prompt = f"""
You are filtering Pakistani university news/deadlines for a specific student.

Student profile:
{json.dumps(profile, indent=2)}
{eligibility_context}

Items to evaluate:
{json.dumps(items, indent=2)}

For each item:
1. Decide if it's relevant to this student (their discipline, target unis, interests)
2. If the item mentions a merit cutoff or percentage, compare it against the student's aggregate ({aggregate}%)
   and add an "eligibility_note" like:
   - "Your aggregate ({aggregate}%) is above this cutoff — you're eligible"
   - "Your aggregate ({aggregate}%) is borderline for this cutoff"
   - "Your aggregate ({aggregate}%) is below this cutoff"
3. Score relevance 0-10

Return ONLY a JSON array of items with relevance >= 3, each with:- "relevance_score" field added
- "eligibility_note" field added (if merit info found)

Sort by relevance_score descending. No explanation, just JSON array.
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            filtered = json.loads(text.strip())

            # Add local eligibility check for known universities
            if aggregate:
                for item in filtered:
                    source = item.get("_source", "")
                    for uni_name in profile.get("universities", []):
                        if uni_name.lower() in source.lower():
                            discipline = profile.get("discipline", "CS")
                            elig = check_eligibility(aggregate, uni_name, discipline)
                            if not item.get("eligibility_note"):
                                item["eligibility_note"] = elig["note"]
                            item["eligibility_status"] = elig["status"]

            return filtered
        except Exception:
            return items