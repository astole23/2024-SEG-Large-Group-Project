from django.shortcuts import render
from tutorials.models.jobposting import JobPosting
from tutorials.models.accounts import CustomUser
from tutorials.matchmaking_helper import match_job_to_cv_bert

def job_recommendation(request):
    # Get the current user
    user = request.user
    
    # Get the user's declared industries
    user_industry = user.user_industry  # List of industries user is interested in

    # Print the user industry to the console for debugging purposes
    print(f"User Industry: {user_industry}")

    # Check if user_industry is empty
    if not user_industry:
        return render(request, 'job_postings.html', {'error_message': 'No industries specified for the user.'})

    # Filter job postings based on the user's industries
    job_postings = JobPosting.objects.all()

    # Print the job postings to the console for debugging purposes
    print(f"Job Postings: {job_postings}")

    # Get the job titles from the filtered job postings
    job_titles = [job.job_title for job in job_postings]

    # Print job titles for debugging
    print(f"Job Titles: {job_titles}")

    # Perform matchmaking (you might want to match the user’s declared job titles with the job postings)
    sorted_matches = match_job_to_cv_bert(user_industry, job_titles)

    # You can now return these sorted matches in your context
    return render(request, 'job_postings.html', {'sorted_matches': sorted_matches})