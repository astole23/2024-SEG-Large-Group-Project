from django.shortcuts import render
from tutorials.models.jobposting import JobPosting

# Create your views here.
def employer_dashboard(request):
    # Query the database for all job postings
    job_postings = JobPosting.objects.all()
    # Pass the query results to the template in a context dictionary
    context = {'job_postings': job_postings}
    return render(request, 'employer_dashboard.html', context)

def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

def guest(request):
    return render(request, 'guest.html')

def user_dashboard(request):
    return render(request, 'user_dashboard.html')