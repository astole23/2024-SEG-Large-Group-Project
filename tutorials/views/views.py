from django.shortcuts import render, get_object_or_404
from tutorials.models.accounts import Company
from tutorials.models.jobposting import JobPosting

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

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

def about_us(request):
    return render(request, 'about_us.html')

def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    job_postings = JobPosting.objects.filter(company_name=company.company_name)  # Match by name
    return render(request, "company_detail.html", {"company": company, "job_postings": job_postings})
