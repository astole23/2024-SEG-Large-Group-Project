from django.shortcuts import render
from django.db.models import Q
from tutorials.models.jobposting import JobPosting
from django.core.paginator import Paginator

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
    query = request.GET.get('q','')
    if query:
        job_postings = JobPosting.objects.filter(job_title__icontains=query)
    else:
        job_postings = JobPosting.objects.all()
    context = {'job_postings': job_postings}
    return render(request, 'guest.html', context)

def user_dashboard(request):
    return render(request, 'user_dashboard.html')

def search(request):
    query = request.GET.get('q', '')

    industries = [
        "business", "management", "sales", "marketing", "technology", "internship",
        "software-development", "engineering", "design", "industry", "finance",
        "accounting", "healthcare", "education", "legal", "customer-service",
        "retail", "hospitality", "construction", "media", "logistics",
        "human-resources", "writing", "consulting", "ngo", "data-science"
    ]

    job_types = ["contract", "freelance", "full_time", "internship", "part_time", "temporary"]

    perks_list = [
        "Flexible working hours", "Health insurance", "Remote work opportunities",
        "On-site gym", "Free lunch/snacks", "Childcare facilities", "Pet-friendly office",
        "Stock options", "Paid time off (PTO)", "Annual performance bonus",
        "Professional development budget", "Free training and certifications",
        "Travel opportunities", "Company laptop", "Work-from-home stipend",
        "Retirement savings plan", "Parental leave", "Diversity and inclusion initiatives",
        "Team-building retreats", "Mental health support", "Referral bonus program",
        "Discounted gym memberships", "Free parking", "Office game room",
        "Tuition reimbursement", "Equity in the company", "Employee discount programs",
        "Unlimited vacation days", "Free access to learning platforms",
        "Relocation assistance", "Commuter benefits", "Wellness programs",
        "Corporate social responsibility opportunities", "Paid volunteering days",
        "Flexible dress id", "Monthly social events", "Annual health check-ups",
        "Employee recognition programs", "Innovation budget", "Quarterly team dinners",
        "Company-sponsored sports teams", "On-site library", "Study leave benefits",
        "Hybrid work environment", "Leadership training", "Sabbatical leave options",
        "Annual company trips", "Pet insurance", "Life insurance",
        "Health savings account (HSA)", "Dedicated workspace reimbursement",
        "Subscription to industry journals", "Discounts on company products/services"
    ]
    # Extract selected filters from request
    selected_education = request.GET.getlist('education_required')
    selected_job_types = request.GET.getlist('job_type')
    selected_industries = request.GET.getlist('industry')
    selected_locations = request.GET.getlist('location_filter')
    selected_perks = request.GET.getlist('benefits')
    selected_work_flexibility = request.GET.getlist('work_flexibility')
    selected_salary = request.GET.get('salary_range', '')
    

    # Get distinct locations from database
    cities = JobPosting.objects.values_list('location', flat=True).distinct()

    # Apply filtering logic to job postings
    job_postings = JobPosting.objects.all()

    

    if query:
        job_postings = job_postings.filter(job_title__icontains=query)

    if selected_education:
        job_postings = job_postings.filter(education_required__in=selected_education)

    if selected_job_types:
        job_postings = job_postings.filter(contract_type__in=selected_job_types)

    if selected_industries:
        job_postings = job_postings.filter(job_title__in=selected_industries)

    if selected_locations:
        job_postings = job_postings.filter(location__in=selected_locations)

    if selected_perks:
        job_postings = job_postings.filter(perks__icontains="|".join(selected_perks))

    if selected_work_flexibility:
        job_postings = job_postings.filter(work_type__in=selected_work_flexibility)

    if selected_salary:
        job_postings = job_postings.filter(salary_range__gte=selected_salary)

    #paginator = Paginator(job_postings, 10)
    #page_number = request.GET.get('page')  # Get current page from URL
    #page_obj = paginator.get_page(page_number)  # Get the specific page

    context = {
        'query': query,
        'selected_education': selected_education,
        'selected_job_types': selected_job_types,
        'selected_industries': selected_industries,
        'selected_locations': selected_locations,
        'selected_perks': selected_perks,
        'selected_work_flexibility': selected_work_flexibility,
        'selected_salary': selected_salary,
        'cities': cities,
        'job_postings': job_postings,
        'perks_list': perks_list,
        'industries': industries,
        'job_types': job_types,
        #'page_obj': page_obj
    }

    return render(request, 'search.html', context)


