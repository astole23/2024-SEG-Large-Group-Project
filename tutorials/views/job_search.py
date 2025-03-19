import random
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from tutorials.models.jobposting import JobPosting
from tutorials.models.accounts import CustomUser
from tutorials.matchmaking_helper import match_job_to_cv_together, is_location_match
from tutorials.models.standard_cv import CVApplication

def get_random_job_postings(limit=100):
    """Fetch a limited number of random job postings using offset."""
    total_jobs = JobPosting.objects.count()  # Get total number of job postings

    if total_jobs == 0:
        return []  # No jobs available

    random_offset = max(0, random.randint(0, max(0, total_jobs - limit)))  # Choose random start index

    return list(JobPosting.objects.all()[random_offset:random_offset + limit])  # Fetch random slice of jobs


def job_recommendation(request):
    user = request.user
    user_industry = user.user_industry or []
    user_locations = user.user_location

    print(f"user location is {user_locations}")
    print(f"user industry is {user_industry}")

    # ✅ Fetch only 100 random job postings instead of all of them
    job_postings = get_random_job_postings(100)

    # ✅ If no user industry or location is specified, return jobs as is
    if not user_industry and not user_locations:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            recommended_jobs = [
                {
                    "id": job.id,
                    "job_title": job.job_title,
                    "company_name": job.company.company_name,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "contract_type": job.contract_type
                }
                for job in job_postings
            ]
            return JsonResponse({"recommended_jobs": recommended_jobs})

        return render(request, 'job_postings.html', {'sorted_matches': [(job, 0) for job in job_postings]})  # Score = 0 since no matching

    job_lookup = {job.job_title: job for job in job_postings}
    job_titles = list(job_lookup.keys())

    try:
        user_cv = CVApplication.objects.get(user=user)
        field_of_study = [user_cv.education[0]["field_of_study"]] if user_cv.education else []
        previous_jobs = [exp["jobTitle"] for exp in user_cv.job_title] if user_cv.job_title else []
    except CVApplication.DoesNotExist:
        field_of_study = []
        previous_jobs = []

    user_values = user_industry + field_of_study + previous_jobs

    # ✅ Perform matching
    sorted_matches = match_job_to_cv_together(user_values, job_titles)
    unique_jobs = {}  # Prevent duplicates

    for job_title, base_score in sorted_matches:
        job = job_lookup.get(job_title)
        if not job or job_title in unique_jobs:
            continue

        location_bonus = is_location_match(user_locations, job.location)
        final_score = base_score + location_bonus

        unique_jobs[job_title] = (job, final_score)

    # ✅ Sort the jobs based on final score
    matched_jobs = sorted(unique_jobs.values(), key=lambda x: x[1], reverse=True)

    # ✅ Debugging: Print out the matched job names
    print("\n📝 Final Recommended Jobs:")
    for job, score in matched_jobs[:3]:  # Only show top 3 for logging
        print(f"- {job.job_title} ({job.company.company_name}) | Location: {job.location} | Score: {score:.2f}")

    # ✅ Handle API vs. Page Rendering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        recommended_jobs = [
            {
                "id": job.id,
                "job_title": job.job_title,
                "company_name": job.company.company_name,
                "location": job.location,
                "salary_range": job.salary_range,
                "contract_type": job.contract_type
            }
            for job, score in matched_jobs[:3]  # Return top 3 jobs
        ]
        return JsonResponse({"recommended_jobs": recommended_jobs})

    return render(request, 'job_postings.html', {'sorted_matches': matched_jobs})
