from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from tutorials.models.jobposting import JobPosting
from tutorials.models.company_review import Review
from django.contrib.auth import get_user_model
from tutorials.forms import (
    UserLoginForm, CompanyLoginForm,
    UserSignUpForm, CompanySignUpForm,
    CompanyProfileForm
)

CustomUser = get_user_model()

@login_required
def employer_dashboard(request):
    # If user is not a company, block access
    if not request.user.is_company:
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login')  
    
    # Otherwise, proceed as normal
    job_postings = JobPosting.objects.all().order_by('-created_at')
    return render(request, 'employer_dashboard.html', {'job_postings': job_postings})


def contact_us(request):
    return render(request, 'contact_us.html')

def guest(request):
    query = request.GET.get('q', '')
    if query:
        job_postings = JobPosting.objects.filter(job_title__icontains=query)
    else:
        job_postings = JobPosting.objects.all()
    return render(request, 'guest.html', {'job_postings': job_postings})

@login_required
def user_dashboard(request):
    # If user is a company, block access
    if request.user.is_company:
        messages.error(request, "Access restricted to normal users only.")
        return redirect('login')  

    # Otherwise, show the user dashboard
    user_info = {}
    if request.user.is_authenticated:
        user_info = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'full_name': f"{request.user.first_name} {request.user.last_name}"
        }
    # Convert to JSON
    user_info_json = json.dumps(user_info)
    return render(request, 'user_dashboard.html', {'user_info_json': user_info_json})


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
    selected_education = request.GET.getlist('education_required')
    selected_job_types = request.GET.getlist('job_type')
    selected_industries = request.GET.getlist('industry')
    selected_locations = request.GET.getlist('location_filter')
    selected_perks = request.GET.getlist('benefits')
    selected_work_flexibility = request.GET.getlist('work_flexibility')
    selected_salary = request.GET.get('salary_range', '')
    
    cities = JobPosting.objects.values_list('location', flat=True).distinct()
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
    }

    print("Query:", query)
    print("Selected job types:", selected_job_types)
    print("Job postings count before filtering:", JobPosting.objects.count())

    if query:
        job_postings = job_postings.filter(job_title__icontains=query)
        print("Count after query filter:", job_postings.count())
    return render(request, 'search.html', context)

def about_us(request):
    return render(request, 'about_us.html')

def profile_settings(request):
    return render(request, 'settings.html')

def login_view(request):
    # Since this view only needs to display the forms (the POST is handled in process_login),
    # we just pass prefixed forms to the template.
    user_form = UserLoginForm(prefix='user')
    company_form = CompanyLoginForm(prefix='company')

    return render(request, 'login.html', {
        'user_form': user_form,
        'company_form': company_form
    })

def signup_view(request):
    # This view just displays the empty forms for a GET request;
    # the actual POST is handled in process_signup.
    user_form = UserSignUpForm(prefix='user')
    company_form = CompanySignUpForm(prefix='company')

    return render(request, 'signup.html', {
        'user_form': user_form,
        'company_form': company_form
    })


def company_detail(request, company_id):
    """
    Display and update a company's profile.
    """
    company = get_object_or_404(CustomUser, id=company_id, is_company=True)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
    else:
        form = CompanyProfileForm(instance=company)
    return render(request, 'company_detail.html', {'company': company, 'form': form})

def leave_review(request, company_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        review = Review(text=text, rating=rating)
        review.save()
        return JsonResponse({'message': 'Review submitted successfully!'}, status=200)
    return render(request, 'company_detail.html', {'company_id': company_id})

def edit_company(request, company_id):
    """
    Allow a company to update its profile details.
    """
    company = get_object_or_404(CustomUser, id=company_id, is_company=True)
    if request.method == 'POST':
        company.description = request.POST.get('description')
        company.logo = request.FILES.get('logo')
        company.save()
        return render(request, 'edit_company.html', {
            'company': company,
            'message': 'Company details updated!'
        })
    return render(request, 'edit_company.html', {'company': company})

@require_POST
@csrf_exempt
def create_job_posting(request, company_id):
    try:
        data = json.loads(request.body)
        deadline_str = data.get('application_deadline')
        if not deadline_str:
            raise ValueError("Application deadline is required.")
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError(f"Invalid date format for application_deadline: {deadline_str}. Expected YYYY-MM-DD.")
        reviews = data.get('company_reviews')
        if reviews:
            try:
                reviews = float(reviews)
            except ValueError:
                reviews = None
        else:
            reviews = None

        required_fields = [
            'job_title', 'company_name', 'location', 'contract_type', 
            'job_overview', 'roles_responsibilities', 'required_skills', 
            'education_required', 'perks'
        ]
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required but missing or empty.")

        job_posting = JobPosting.objects.create(
            job_title=data.get('job_title'),
            company_name=data.get('company_name'),
            child_company_name=data.get('child_company_name'),
            location=data.get('location'),
            work_type=data.get('work_type'),
            salary_range=data.get('salary_range'),
            contract_type=data.get('contract_type'),
            job_overview=data.get('job_overview'),
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
        return JsonResponse({'status': 'success', 'job_id': job_posting.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)

def apply_step1(request):
    return render(request, 'step1.html')

def apply_step2(request):
    return render(request, 'step2.html')

def apply_step3(request):
    return render(request, 'step3.html')

def apply_step4(request):
    return render(request, 'step4.html')

def application_success(request):
    return render(request, 'success.html')
