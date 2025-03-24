import logging

from django.shortcuts import render
from django.http import JsonResponse

from tutorials.helpers.matchmaking_helper import match_job_to_cv_together, compute_final_scores
from tutorials.helpers.database_helper import get_random_job_postings, safe_json_list
from tutorials.helpers.base_helpers import extract_user_data

logger = logging.getLogger(__name__)

def format_job_posting(job):
    """Convert a job object into a dictionary for JSON response."""
    return {
        "id": job.id,
        "job_title": job.job_title,
        "company_name": job.company.company_name,
        "location": job.location,
        "salary_range": job.salary_range,
        "contract_type": job.contract_type,
        "job_overview": job.job_overview,
        "roles_responsibilities": job.roles_responsibilities,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "education_required": job.education_required,
        "perks": job.perks,
        "company_overview": job.company_overview,
        "why_join_us": job.why_join_us,
        "company_reviews": job.company_reviews,
        "company_id": job.company.id,
    }

def job_recommendation(request):
    """Handle job recommendations based on user profile and preferences."""
    user = request.user
    user_values, user_locations = extract_user_data(user)

    user_values = safe_json_list(user_values)
    user_locations = safe_json_list(user_locations)

    logger.info(f"User location: {user_locations}, User industry: {user_values}")

    job_postings = get_random_job_postings(100)

    if not user_values and not user_locations:
        sorted_matches = [(job, 0) for job in job_postings]
        return _return_response(request, sorted_matches)

    job_lookup = {job.job_title: job for job in job_postings}
    job_titles = list(job_lookup.keys())

    sorted_matches = match_job_to_cv_together(user_values, job_titles)
    
    matched_jobs = compute_final_scores(sorted_matches, job_lookup, user_locations)

    logger.info("\n📝 Final Recommended Jobs:")
    for job, score in matched_jobs[:3]:
        logger.info(f"- {job.job_title} ({job.company.company_name}) | Location: {job.location} | Score: {score:.2f}")

    return _return_response(request, matched_jobs)

def _return_response(request, matched_jobs):
    """Return the response in JSON or render HTML based on request type."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"recommended_jobs": [format_job_posting(job) for job, _ in matched_jobs[:3]]})
    return render(request, 'jobseeker/job_postings.html', {'sorted_matches': matched_jobs})
