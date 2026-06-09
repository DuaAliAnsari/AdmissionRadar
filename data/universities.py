"""
University Knowledge Base
--------------------------
Structured info on 20+ Pakistani universities.
Agents reference this instead of relying purely on scraped content.
Includes: entry tests, fee ranges, historical merit ranges, programs.
"""

UNIVERSITIES = {
    "FAST NUCES": {
        "full_name": "FAST National University of Computer and Emerging Sciences",
        "campuses": ["Karachi", "Lahore", "Islamabad", "Peshawar", "Chiniot-Faisalabad"],
        "disciplines": ["CS", "Engineering", "Business"],
        "entry_test": "NU Entry Test (NET)",
        "admission_url": "https://admissions.nu.edu.pk/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [82, 92], "fee_per_semester": 85000},
            "SE": {"degree": "BS SE", "duration": 4, "merit_range": [80, 90], "fee_per_semester": 85000},
            "AI": {"degree": "BS AI", "duration": 4, "merit_range": [83, 93], "fee_per_semester": 85000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "NUST": {
        "full_name": "National University of Sciences and Technology",
        "campuses": ["Islamabad"],
        "disciplines": ["Engineering", "CS", "Business", "Medical"],
        "entry_test": "NET (NUST Entrance Test)",
        "admission_url": "https://admission.nust.edu.pk/",
        "programs": {
            "CS": {"degree": "BE CS", "duration": 4, "merit_range": [85, 95], "fee_per_semester": 95000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [83, 93], "fee_per_semester": 95000},
            "ME": {"degree": "BE ME", "duration": 4, "merit_range": [82, 92], "fee_per_semester": 95000},
            "AI": {"degree": "BE AI", "duration": 4, "merit_range": [86, 95], "fee_per_semester": 95000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "LUMS": {
        "full_name": "Lahore University of Management Sciences",
        "campuses": ["Lahore"],
        "disciplines": ["Business", "CS", "Law", "Social Sciences"],
        "entry_test": "SAT or LUMS own test",
        "admission_url": "https://admission.lums.edu.pk/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [88, 97], "fee_per_semester": 200000},
            "BSc": {"degree": "BSc Economics & Math", "duration": 4, "merit_range": [85, 95], "fee_per_semester": 200000},
            "BA": {"degree": "BA Social Sciences", "duration": 4, "merit_range": [80, 92], "fee_per_semester": 200000},
        },
        "financial_aid": True,  # National Outreach Programme (NOP)
        "hostel": True,
    },
    "UET Lahore": {
        "full_name": "University of Engineering and Technology Lahore",
        "campuses": ["Lahore", "Faisalabad", "Narowal", "Kala Shah Kaku"],
        "disciplines": ["Engineering", "CS"],
        "entry_test": "ECAT",
        "admission_url": "https://www.uet.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [80, 90], "fee_per_semester": 45000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [78, 88], "fee_per_semester": 45000},
            "ME": {"degree": "BE ME", "duration": 4, "merit_range": [76, 86], "fee_per_semester": 45000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "COMSATS": {
        "full_name": "COMSATS University Islamabad",
        "campuses": ["Islamabad", "Lahore", "Karachi", "Abbottabad", "Attock", "Sahiwal", "Vehari", "Wah"],
        "disciplines": ["CS", "Engineering", "Business", "Pharmacy"],
        "entry_test": "Aggregate (Matric + FSc + NTS/SAT)",
        "admission_url": "https://admission.comsats.edu.pk/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [70, 85], "fee_per_semester": 55000},
            "SE": {"degree": "BS SE", "duration": 4, "merit_range": [68, 83], "fee_per_semester": 55000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [67, 82], "fee_per_semester": 55000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "IBA Karachi": {
        "full_name": "Institute of Business Administration Karachi",
        "campuses": ["Karachi"],
        "disciplines": ["Business", "CS", "Economics"],
        "entry_test": "IBA Admission Test",
        "admission_url": "https://admission.iba.edu.pk/",
        "programs": {
            "BBA": {"degree": "BBA", "duration": 4, "merit_range": [80, 92], "fee_per_semester": 120000},
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [78, 90], "fee_per_semester": 120000},
            "Econ": {"degree": "BS Economics", "duration": 4, "merit_range": [75, 88], "fee_per_semester": 120000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "NED Karachi": {
        "full_name": "NED University of Engineering and Technology",
        "campuses": ["Karachi"],
        "disciplines": ["Engineering", "CS"],
        "entry_test": "ECAT",
        "admission_url": "https://www.neduet.edu.pk/admission",
        "programs": {
            "CS": {"degree": "BE CS", "duration": 4, "merit_range": [78, 90], "fee_per_semester": 30000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [76, 88], "fee_per_semester": 30000},
            "ME": {"degree": "BE ME", "duration": 4, "merit_range": [74, 86], "fee_per_semester": 30000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "Aga Khan University": {
        "full_name": "Aga Khan University",
        "campuses": ["Karachi"],
        "disciplines": ["Medical", "Nursing", "Education"],
        "entry_test": "AKU-EB / MCAT",
        "admission_url": "https://www.aku.edu/admissions/",
        "programs": {
            "MBBS": {"degree": "MBBS", "duration": 5, "merit_range": [90, 99], "fee_per_semester": 400000},
            "BScN": {"degree": "BScN Nursing", "duration": 4, "merit_range": [75, 88], "fee_per_semester": 150000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "DOW University": {
        "full_name": "Dow University of Health Sciences",
        "campuses": ["Karachi"],
        "disciplines": ["Medical", "Pharmacy", "Allied Health"],
        "entry_test": "MDCAT",
        "admission_url": "https://www.duhs.edu.pk/admissions/",
        "programs": {
            "MBBS": {"degree": "MBBS", "duration": 5, "merit_range": [85, 96], "fee_per_semester": 80000},
            "BDS": {"degree": "BDS", "duration": 4, "merit_range": [80, 92], "fee_per_semester": 75000},
            "Pharm": {"degree": "Pharm-D", "duration": 5, "merit_range": [75, 88], "fee_per_semester": 60000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "KEMU": {
        "full_name": "King Edward Medical University",
        "campuses": ["Lahore"],
        "disciplines": ["Medical"],
        "entry_test": "MDCAT",
        "admission_url": "https://www.kemu.edu.pk/admissions/",
        "programs": {
            "MBBS": {"degree": "MBBS", "duration": 5, "merit_range": [88, 97], "fee_per_semester": 50000},
            "BDS": {"degree": "BDS", "duration": 4, "merit_range": [83, 93], "fee_per_semester": 45000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "QAU": {
        "full_name": "Quaid-i-Azam University",
        "campuses": ["Islamabad"],
        "disciplines": ["Sciences", "Social Sciences", "Business"],
        "entry_test": "Aggregate (Matric + FSc)",
        "admission_url": "https://qau.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [72, 85], "fee_per_semester": 15000},
            "Physics": {"degree": "BS Physics", "duration": 4, "merit_range": [65, 80], "fee_per_semester": 12000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "PU Lahore": {
        "full_name": "University of the Punjab",
        "campuses": ["Lahore"],
        "disciplines": ["Sciences", "Arts", "Business", "Law", "Engineering"],
        "entry_test": "Aggregate (Matric + FSc)",
        "admission_url": "https://admission.pu.edu.pk/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [70, 84], "fee_per_semester": 20000},
            "Commerce": {"degree": "BCom", "duration": 2, "merit_range": [60, 78], "fee_per_semester": 10000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "Habib University": {
        "full_name": "Habib University",
        "campuses": ["Karachi"],
        "disciplines": ["Engineering", "CS", "Social Sciences"],
        "entry_test": "Habib Admission Test (HAT)",
        "admission_url": "https://habib.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [80, 92], "fee_per_semester": 160000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [78, 90], "fee_per_semester": 160000},
        },
        "financial_aid": True,
        "hostel": False,
    },
    "GIKI": {
        "full_name": "Ghulam Ishaq Khan Institute of Engineering Sciences and Technology",
        "campuses": ["Topi, KPK"],
        "disciplines": ["Engineering", "CS"],
        "entry_test": "SAT II or ECAT",
        "admission_url": "https://www.giki.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [82, 93], "fee_per_semester": 100000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [80, 91], "fee_per_semester": 100000},
            "ME": {"degree": "BE ME", "duration": 4, "merit_range": [78, 89], "fee_per_semester": 100000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "ITU": {
        "full_name": "Information Technology University",
        "campuses": ["Lahore"],
        "disciplines": ["CS", "Engineering"],
        "entry_test": "ITU Entry Test",
        "admission_url": "https://itu.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [75, 88], "fee_per_semester": 70000},
            "DS": {"degree": "BS Data Science", "duration": 4, "merit_range": [76, 89], "fee_per_semester": 70000},
        },
        "financial_aid": True,
        "hostel": False,
    },
    "Sukkur IBA": {
        "full_name": "Sukkur IBA University",
        "campuses": ["Sukkur"],
        "disciplines": ["CS", "Business", "Engineering"],
        "entry_test": "Sukkur IBA Entry Test",
        "admission_url": "https://www.iba-suk.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [68, 82], "fee_per_semester": 35000},
            "BBA": {"degree": "BBA", "duration": 4, "merit_range": [65, 80], "fee_per_semester": 30000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "Air University": {
        "full_name": "Air University",
        "campuses": ["Islamabad", "Multan", "Kamra"],
        "disciplines": ["CS", "Engineering", "Business"],
        "entry_test": "AU Entry Test",
        "admission_url": "https://www.au.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [72, 85], "fee_per_semester": 60000},
            "SE": {"degree": "BS SE", "duration": 4, "merit_range": [70, 83], "fee_per_semester": 60000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "SZABIST": {
        "full_name": "Shaheed Zulfikar Ali Bhutto Institute of Science and Technology",
        "campuses": ["Karachi", "Islamabad", "Larkana", "Hyderabad", "Dubai"],
        "disciplines": ["CS", "Business", "Media"],
        "entry_test": "SZABIST Entry Test",
        "admission_url": "https://www.szabist.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [68, 82], "fee_per_semester": 65000},
            "BBA": {"degree": "BBA", "duration": 4, "merit_range": [65, 80], "fee_per_semester": 65000},
        },
        "financial_aid": True,
        "hostel": False,
    },
    "MUET": {
        "full_name": "Mehran University of Engineering and Technology",
        "campuses": ["Jamshoro"],
        "disciplines": ["Engineering", "CS"],
        "entry_test": "ECAT",
        "admission_url": "https://www.muet.edu.pk/admissions/",
        "programs": {
            "CS": {"degree": "BE CS", "duration": 4, "merit_range": [70, 84], "fee_per_semester": 25000},
            "EE": {"degree": "BE EE", "duration": 4, "merit_range": [68, 82], "fee_per_semester": 25000},
        },
        "financial_aid": True,
        "hostel": True,
    },
    "UCP": {
        "full_name": "University of Central Punjab",
        "campuses": ["Lahore"],
        "disciplines": ["CS", "Business", "Engineering", "Law", "Medical"],
        "entry_test": "UCP Entry Test",
        "admission_url": "https://admission.ucp.edu.pk/",
        "programs": {
            "CS": {"degree": "BS CS", "duration": 4, "merit_range": [65, 80], "fee_per_semester": 55000},
            "BBA": {"degree": "BBA", "duration": 4, "merit_range": [62, 78], "fee_per_semester": 55000},
        },
        "financial_aid": True,
        "hostel": True,
    },
}

# Discipline-to-university mapping for the Planner agent
DISCIPLINE_UNIVERSITIES = {
    "CS": ["FAST NUCES", "NUST", "LUMS", "COMSATS", "IBA Karachi", "NED Karachi", "Habib University", "GIKI", "ITU", "Air University", "SZABIST"],
    "Engineering": ["NUST", "UET Lahore", "NED Karachi", "GIKI", "COMSATS", "MUET", "Habib University", "Air University"],
    "Medical": ["Aga Khan University", "DOW University", "KEMU"],
    "Business": ["LUMS", "IBA Karachi", "Sukkur IBA", "SZABIST", "UCP", "ITU"],
    "Data Science": ["ITU", "FAST NUCES", "NUST", "LUMS"],
}

# Entry tests by discipline
ENTRY_TESTS = {
    "CS": ["NET (FAST)", "NET (NUST)", "ECAT", "IBA Test", "HAT (Habib)", "SAT"],
    "Engineering": ["ECAT", "NET (NUST)", "SAT II", "AU Entry Test"],
    "Medical": ["MDCAT", "MCAT", "AKU-EB"],
    "Business": ["IBA Test", "LUMS Test", "SAT"],
}


def get_unis_for_discipline(discipline: str) -> list[str]:
    """Return list of university names relevant to a discipline."""
    return DISCIPLINE_UNIVERSITIES.get(discipline, list(UNIVERSITIES.keys()))


def get_university(name: str) -> dict:
    """Get full university info by name."""
    return UNIVERSITIES.get(name, {})


def get_all_admission_urls() -> list[dict]:
    """Return all admission URLs as source list for crawler."""
    sources = []
    for name, info in UNIVERSITIES.items():
        sources.append({
            "name": f"{name} Admissions",
            "url": info["admission_url"],
            "type": "admission",
            "university": name,
        })
    return sources