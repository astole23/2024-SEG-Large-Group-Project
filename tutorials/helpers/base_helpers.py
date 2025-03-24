from tutorials.models.standard_cv import UserCV
from .database_helper import safe_json_list

def normalize_to_string_list(value):
    if isinstance(value, list):
        return ", ".join(v.strip() for v in value)
    elif isinstance(value, str):
        return value.strip()
    return ""

def normalize_edu(e):
    return (
        e.get("university", "").strip().lower(),
        e.get("degree_type", "").strip().lower(),
        e.get("field_of_study", "").strip().lower(),
        e.get("grade", "").strip().lower(),
        e.get("dates", "").strip().lower(),
        e.get("modules", "").strip().lower(),
    )

def normalize_exp(e):
    return (
        e.get("company", "").strip().lower(),
        e.get("job_title", "").strip().lower(),
        e.get("responsibilities", "").strip().lower(),
        e.get("dates", "").strip().lower(),
    )

def normalize_str(s):
    return str(s or '').strip().lower().replace('–', '-').replace('—', '-').replace('’', "'")
    
def remove_duplicate_education(entries):
    seen = set()
    cleaned = []
    for edu in entries:
        key = f"{normalize_str(edu.get('university'))}|{normalize_str(edu.get('degreeType'))}|{normalize_str(edu.get('fieldOfStudy'))}|{normalize_str(edu.get('dates'))}"
        if key not in seen:
            seen.add(key)
            cleaned.append(edu)
    return cleaned

def remove_duplicate_experience(entries):
    seen = set()
    cleaned = []
    for exp in entries:
        key = f"{normalize_str(exp.get('employer'))}|{normalize_str(exp.get('jobTitle'))}|{normalize_str(exp.get('dates'))}"
        if key not in seen:
            seen.add(key)
            cleaned.append(exp)
    return cleaned

def extract_user_data(user):
    """Extract industry, location, and CV data for the user."""
    user_industry = user.user_industry or []
    user_locations = user.user_location

    try:
        user_cv = UserCV.objects.get(user=user)
        education_data = safe_json_list(user_cv.education)
        work_data = safe_json_list(user_cv.work_experience or user_cv.job_title)

        field_of_study = [edu.get("fieldOfStudy") for edu in education_data if "fieldOfStudy" in edu]
        previous_jobs = [exp.get("job_title") for exp in user_cv.work_experience or []]
    except UserCV.DoesNotExist:
        field_of_study = []
        previous_jobs = []

    user_values = user_industry + field_of_study + previous_jobs
    return user_values, user_locations

