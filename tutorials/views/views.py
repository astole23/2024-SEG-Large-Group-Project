
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from tutorials.models.accounts import Company
from tutorials.models.jobposting import JobPosting
from tutorials.forms import CompanyForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from tutorials.models.company_review import Review
from tutorials.forms import CompanyEditForm
from datetime import datetime
from django.core.paginator import Paginator
from tutorials.forms import JobPostingForm
from tutorials.models.jobposting import JobPosting

from tutorials.forms import CompanyRegistrationForm, UserRegistrationForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

def employer_dashboard(request):

    # Query the database for all job postings
    job_postings = JobPosting.objects.all().order_by('-created_at')
    # Pass the query results to the template in a context dictionary
    context = {'job_postings': job_postings}
    return render(request, 'employer_dashboard.html', context)



def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            company = Company.objects.get(email=email)
        except Company.DoesNotExist:
            company = None

        if company and check_password(password, company.password):
            request.session['company_id'] = company.id

            return redirect('edit_company', company_id=company.id)
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

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

    job_types = ["Apprenticeship", "Full-time", "Internship", "Part-time"]

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



def about_us(request):
    return render(request, 'about_us.html')

def profile_settings(request):
    return render(request, 'settings.html')



def signup_view(request):
    company_form = CompanyRegistrationForm()
    user_form = UserRegistrationForm()
    if request.method == "POST":

        user_type = request.POST.get("user_type")
     
        if user_type == "company":
            company_form = CompanyRegistrationForm(request.POST)
            if company_form.is_valid():
                company_form.save()
                messages.success(request, "Company registered successfully!")
                return redirect("employer_dashboard")
            else:
                messages.error(request, "Error in company signup form.")

        elif user_type == "user":
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "User registered successfully!")
                return redirect("user_dashboard")
            else:
                messages.error(request, "Error in user signup form.")

    return render(request, "signup.html", {"company_form": company_form, "user_form": user_form})
 

def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
    else:
        form = CompanyForm(instance=company)

    return render(request, 'company_detail.html', {'company': company, 'form': form})

def leave_review(request, company_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        # Create and save the review
        review = Review(text=text, rating=rating)
        review.save()

        return JsonResponse({'message': 'Review submitted successfully!'}, status=200)
    
    return render(request, 'company_detail.html', {'company_id': company_id})


def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        company.description = request.POST.get('description')
        company.logo = request.FILES.get('logo')  # If uploading logo
        company.save()
        
        # Optionally, provide feedback to the user
        return render(request, 'edit_company.html', {'company': company, 'message': 'Company details updated!'})

    return render(request, 'edit_company.html', {'company': company})



@require_POST
@csrf_exempt  # Remove if you send a valid CSRF token.
def create_job_posting(request, company_id):
    try:
        # Parse JSON data from the request body.
        data = json.loads(request.body)
        print("Received data:", data)  # Debug: log the incoming data
        
        # Convert application_deadline from string to a date object.
        deadline_str = data.get('application_deadline')
        if not deadline_str:
            raise ValueError("Application deadline is required.")
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError(f"Invalid date format for application_deadline: {deadline_str}. Expected YYYY-MM-DD.")
        print("Parsed deadline:", deadline)
        
        # Convert company_reviews to float if provided.
        reviews = data.get('company_reviews')
        if reviews:
            try:
                reviews = float(reviews)
            except ValueError:
                reviews = None
        else:
            reviews = None

        # Check required fields manually (for debugging)
        required_fields = ['job_title', 'company_name', 'location', 'contract_type', 
                           'job_overview', 'roles_responsibilities', 'required_skills', 
                           'education_required', 'perks']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required but missing or empty.")

        # Create a new JobPosting instance.
        job_posting = JobPosting.objects.create(
            job_title=data.get('job_title'),
            company_name=data.get('company_name'),
            child_company_name=data.get('child_company_name'),
            location=data.get('location'),
            work_type=data.get('work_type'),
            salary_range=data.get('salary_range'),
            contract_type=data.get('contract_type'),
            job_overview=data.get('job_overview'),
            # Use the key 'roles_responsibilities' from the form
            roles_responsibilities=data.get('roles_responsibilities'),
            required_skills=data.get('required_skills'),
            preferred_skills=data.get('preferred_skills'),
            education_required=data.get('education_required'),
            perks=data.get('perks'),
            application_deadline=deadline,
            required_documents=data.get('required_documents'),
            company_overview=data.get('company_overview'),
            why_join_us=data.get('why_join_us'),
            company_reviews=reviews
        )
        
        print("Job posting created with ID:", job_posting.id)
        # Return a success JSON response.
        return JsonResponse({'status': 'success', 'job_id': job_posting.id})
    
    except Exception as e:
        # Log the error for debugging
        print("Error in create_job_posting:", str(e))
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)