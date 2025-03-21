import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from tutorials.models.jobposting import JobPosting
from tutorials.models.standard_cv import CVApplication
from tutorials.helpers.matchmaking_helper import match_job_to_cv_together, is_location_match
from tutorials.models.standard_cv import UserCV

def get_random_job_postings(limit=150):
    total_jobs = JobPosting.objects.count()
    if total_jobs == 0:
        return []
    random_offset = max(0, random.randint(0, max(0, total_jobs - limit)))
    return list(JobPosting.objects.all()[random_offset:random_offset + limit])

def safe_json_list(data):
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return []
    return data if isinstance(data, list) else []

def job_recommendation(request):
    user = request.user
    user_industry = user.user_industry or []
    user_locations = user.user_location

    print(f"user location is {user_locations}")
    print(f"user industry is {user_industry}")

    job_postings = get_random_job_postings(100)

    if not user_industry and not user_locations:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            recommended_jobs = [
                {
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
                }
                for job in job_postings
            ]
            return JsonResponse({"recommended_jobs": recommended_jobs})
        return render(request, 'jobseeker/job_postings.html', {'sorted_matches': [(job, 0) for job in job_postings]})

    job_lookup = {job.job_title: job for job in job_postings}
    job_titles = list(job_lookup.keys())

    try:
        user_cv = UserCV.objects.get(user=user)

        # ✅ Safely decode education and work experience
        education_data = safe_json_list(user_cv.education)
        work_data = safe_json_list(user_cv.work_experience or user_cv.job_title)

        education_data = user_cv.education if isinstance(user_cv.education, list) else []
        field_of_study = [edu.get("fieldOfStudy") for edu in education_data if "fieldOfStudy" in edu]

        previous_jobs = [exp.get("job_title") for exp in user_cv.work_experience or []]


    except UserCV.DoesNotExist:
        field_of_study = []
        previous_jobs = []

    user_values = user_industry + field_of_study + previous_jobs

    sorted_matches = match_job_to_cv_together(user_values, job_titles)
    unique_jobs = {}

    for job_title, base_score in sorted_matches:
        job = job_lookup.get(job_title)
        if not job or job_title in unique_jobs:
            continue

        location_bonus = is_location_match(user_locations, job.location)
        final_score = base_score + location_bonus
        unique_jobs[job_title] = (job, final_score)

    matched_jobs = sorted(unique_jobs.values(), key=lambda x: x[1], reverse=True)

    print("\n📝 Final Recommended Jobs:")
    for job, score in matched_jobs[:3]:
        print(f"- {job.job_title} ({job.company.company_name}) | Location: {job.location} | Score: {score:.2f}")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        recommended_jobs = [
            {
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
            }
            for job, score in matched_jobs[:3]
        ]
        return JsonResponse({"recommended_jobs": recommended_jobs})

    return render(request, 'jobseeker/job_postings.html', {'sorted_matches': matched_jobs})
