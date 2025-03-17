from django.shortcuts import render
from django.http import JsonResponse
from tutorials.models.jobposting import JobPosting
from tutorials.models.accounts import CustomUser
from tutorials.matchmaking_helper import match_job_to_cv_together, is_location_match
from tutorials.models.standard_cv import CVApplication

def job_recommendation(request):
    user = request.user
    user_industry = user.user_industry or []
    user_locations = user.user_location

    print(f"user location is {user_locations}")
    print(f"user location is {user_industry}")


    if not user_industry:
        return JsonResponse({"error": "No industries specified for the user."}, status=400) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'job_postings.html', {'error_message': 'No industries specified for the user.'})

    job_postings = list(JobPosting.objects.all())
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


    sorted_matches = match_job_to_cv_together(user_values, job_titles)
    unique_jobs = {} 

    for job_title, base_score in sorted_matches:
        job = job_lookup.get(job_title)
        if not job or job_title in unique_jobs:
            continue

        location_bonus = is_location_match(user_locations, job.location)
        final_score = base_score + location_bonus

        unique_jobs[job_title] = (job, final_score)

    # ✅ Convert to sorted list
    matched_jobs = sorted(unique_jobs.values(), key=lambda x: x[1], reverse=True)

    # ✅ Print out the matched job names
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
