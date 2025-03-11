from django.shortcuts import render
from tutorials.models.jobposting import JobPosting
from django.contrib.auth.decorators import login_required

@login_required
def job_search(request):
    # Fetch the logged-in user's profile
    user = request.user

    # Get the user's location and industry
    user_location = user.user_location
    user_industry = user.user_industry

    # Print the location and industry for debugging purposes
    print(f"User Location: {user_location}")
    print(f"User Industry: {user_industry}")

    # Filter job postings based on location and industry
    job_postings = JobPosting.objects.all()

    # Filter by location if available
    if user_location:
        job_postings = job_postings.filter(company__user_location__icontains=user_location)

    # Filter by industry if available
    if user_industry:
        job_postings = job_postings.filter(company__user_industry__icontains=user_industry)

    return render(request, 'job_search.html', {'job_postings': job_postings})
