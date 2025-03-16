from django.shortcuts import render
from tutorials.models.jobposting import JobPosting
from tutorials.models.accounts import CustomUser
from tutorials.matchmaking_helper import match_job_to_cv_together, is_location_match

def job_recommendation(request):
    user = request.user
    user_industry = user.user_industry
    user_locations = user.user_location

    if not user_industry:
        return render(request, 'job_postings.html', {'error_message': 'No industries specified for the user.'})

    job_postings = list(JobPosting.objects.all())
    job_lookup = {job.job_title: job for job in job_postings}
    job_titles = list(job_lookup.keys())

    # 🔍 Debugging before calling Together AI
    print(f"🔍 Sending to match_job_to_cv_together: {user_industry}, {job_titles}")

    sorted_matches = match_job_to_cv_together(user_industry, job_titles)
    unique_jobs = {}

    print("\n🔍 Job Matching Debug Info:\n")

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
    for job, score in matched_jobs:
        print(f"- {job.job_title} ({job.company.company_name}) | Location: {job.location} | Score: {score:.2f}")

    return render(request, 'job_postings.html', {'sorted_matches': matched_jobs})