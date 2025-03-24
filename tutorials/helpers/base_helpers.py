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