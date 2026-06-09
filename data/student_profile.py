"""
Student Profile
---------------
Edit this file to match your own details.
The Planner and Relevance agents use this to personalize everything.
Now includes academic scores for real eligibility filtering.
"""

STUDENT_PROFILE = {
    "name": "Ali",

    # Your target universities (leave empty to check all)
"universities": ["FAST NUCES", "NUST", "LUMS", "COMSATS", "GIKI", "ITU", "Habib University", "NED Karachi"],
    # Your discipline — drives which universities the Planner checks
    # Options: "CS", "Engineering", "Medical", "Business", "Data Science"
    "discipline": "CS",

    # Your degree level
    "degree": "BS",
    "year": "applying",   # or "1st year", "2nd year", etc.

    # Academic scores (used for eligibility filtering)
    "matric_pct": 91.0,     # your matric percentage
    "fsc_pct": 88.0,        # your FSc/A-Level percentage (or equivalent)
    "test_score": 145,      # your entry test score (NET/ECAT/MDCAT raw score)
    "test_type": "NET",     # which test: "NET", "ECAT", "MDCAT", "SAT", etc.

    # Aggregate % (if already calculated, else leave null and agent computes it)
    "aggregate_pct": None,

    # What you care about
    "interests": ["admissions", "scholarships", "merit lists", "fee structure"],

    # Notification channel
    "email": "youremail@gmail.com",

    # Urgency threshold: only alert for items this urgent or higher
    "min_urgency": "medium",       # "low", "medium", or "high"
}


def load_profile() -> dict:
    return STUDENT_PROFILE