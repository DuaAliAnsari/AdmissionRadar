"""
Student Profile
---------------
Edit this file to match your own details.
The Planner and Relevance agents use this to personalize everything.
"""

STUDENT_PROFILE = {
    "name": "Ali",

    # Your target universities
    "universities": ["FAST NUCES", "NUST", "LUMS"],

    # Your program
    "program": "Computer Science",
    "degree": "BS",
    "year": "applying",   # or "1st year", "2nd year", etc.

    # What you care about
    "interests": ["admissions", "scholarships", "merit lists", "fee structure"],

    # Notification channel
    "email": "dua.ansari@gmail.com",

    # Urgency threshold: only alert for items this urgent or higher
    "min_urgency": "medium",       # "low", "medium", or "high"
}


def load_profile() -> dict:
    return STUDENT_PROFILE
