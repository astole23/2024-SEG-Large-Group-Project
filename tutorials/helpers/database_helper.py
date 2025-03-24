import random
import json
from tutorials.models.jobposting import JobPosting

def get_random_job_postings(limit=150):
    """Fetch a random subset of job postings."""
    total_jobs = JobPosting.objects.count()
    if total_jobs == 0:
        return []
    random_offset = max(0, random.randint(0, max(0, total_jobs - limit)))
    return list(JobPosting.objects.all()[random_offset:random_offset + limit])

def safe_json_list(data):
    """Safely parse JSON strings into a list."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return []
    return data if isinstance(data, list) else []
