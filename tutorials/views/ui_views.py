from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
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
from django.utils.dateparse import parse_date
import traceback
from django.db import transaction
from django.utils.timezone import localtime
from tutorials.forms import (
    UserLoginForm, CompanyLoginForm,
    UserSignUpForm, CompanySignUpForm,
    CompanyProfileForm, UserUpdateForm, MyPasswordChangeForm
)

from django.utils.timesince import timesince
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from tutorials.models.accounts import CustomUser

from tutorials.models.applications import JobApplication
from tutorials.models.applications import Notification
from tutorials.forms import CVApplicationForm
from tutorials.models.standard_cv import CVApplication, UserCV
import logging
from tutorials.auto_fill import extract_text_from_pdf, classify_resume_with_together
import tempfile
from tutorials.views.function_views import remove_duplicates_by_keys , split_skills
import os
from tutorials.models.user_dashboard import UploadedCV, UserDocument
CustomUser = get_user_model()

from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator

@login_required
def employer_dashboard(request):
    # Only allow company users
    
    if not request.user.is_company:
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login')  
    
    job_list = JobPosting.objects.filter(company=request.user).order_by('-created_at')

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    job_postings = paginator.get_page(page_number)

    return render(request, 'company/employer_dashboard.html', {'job_postings': job_postings})

def user_logout(request):
    # Log the user out
    logout(request)
    # Redirect them to the homepage or login page
    return redirect('/')


def contact_us(request):
    return render(request, 'pages/contact_us.html')

def normalize_to_string_list(value):
    if isinstance(value, list):
        return ", ".join(v.strip() for v in value)
    elif isinstance(value, str):
        return value.strip()
    return ""

def guest(request):
    query = request.GET.get('q', '')
    if query:
        job_postings = JobPosting.objects.filter(job_title__icontains=query)
    else:
        job_postings = JobPosting.objects.all()
    return render(request, 'pages/guest.html', {'job_postings': job_postings,'is_guest': True})

@login_required
def user_dashboard(request):
    if request.user.is_company:
        messages.error(request, "Access restricted to normal users only.")
        return redirect('login')

    # 1. User Info (for frontend)
    user_info = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'location': request.user.user_location[0] if isinstance(request.user.user_location, list) and request.user.user_location else 'Unknown',
        'profile_photo': request.user.user_profile_photo.url if request.user.user_profile_photo else None
    }

    # 2. CV Structured Data (AI parsed)
    try:
        cv = UserCV.objects.get(user=request.user)
        structured = {
            "skills": cv.key_skills,
            "technical_skills": cv.technical_skills,
            "languages": cv.languages
        }
        cv_data = {
            'personalInfo': cv.personal_info or {},
            'education': cv.education or [],
            'workExperience': cv.work_experience or [],
            'skills': {
                'key_skills': normalize_to_string_list(structured.get("skills", "")),
                'technical_skills': normalize_to_string_list(structured.get("technical_skills", "")),
                'languages': normalize_to_string_list(structured.get("languages", ""))
            },
        }
    except UserCV.DoesNotExist:
        cv_data = {}
    except Exception as e:
        print("⚠️ Error loading UserCV:", e)
        cv_data = {}

    # 3. Raw PDF CV Upload Info
    try:
        uploaded_cv = UploadedCV.objects.get(user=request.user)
        raw_cv_info = {
            'filename': uploaded_cv.file.name.split('/')[-1],
            'file_url': uploaded_cv.file.url,
            'uploaded_at': localtime(uploaded_cv.uploaded_at).strftime("%b %d, %Y %I:%M %p")
        }
    except UploadedCV.DoesNotExist:
        raw_cv_info = {}
    except Exception as e:
        print("⚠️ Error loading UploadedCV:", e)
        raw_cv_info = {}

    # 4. Up to 5 Supporting Documents
    try:
        uploaded_documents = UserDocument.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
        documents_list = []
        for doc in uploaded_documents:
            documents_list.append({
                'filename': doc.file.name.split('/')[-1],
                'file_url': doc.file.url,
                'uploaded_at': doc.uploaded_at.strftime("%b %d, %Y %I:%M %p"),
                'uploaded_at_human': timesince(doc.uploaded_at) + " ago",
            })

    except Exception as e:
        print("⚠️ Error loading UserDocuments:", e)
        uploaded_documents = []

    print("🧾 raw_cv_info_json:", raw_cv_info)

    return render(request, 'jobseeker/user_dashboard.html', {
        'user_info_json': json.dumps(user_info),
        'cv_data_json': json.dumps(cv_data, cls=DjangoJSONEncoder),
        'raw_cv_info_json': json.dumps(raw_cv_info),
        'documents_json': json.dumps(documents_list),  # ✅ ADD THIS
    })



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

    paginator = Paginator(job_postings, 12)  # 10 job postings per page
    page_number = request.GET.get('page')
    job_postings = paginator.get_page(page_number)

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

    return render(request, 'pages/search.html', context)

def about_us(request):
    return render(request, 'pages/about_us.html')

def terms_conditions(request):
    return render(request, 'pages/terms_conditions.html')

def status(request):
    return render(request, 'jobseeker/status.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def user_agreement(request):
    return render(request, 'pages/user_agreement.html')

def faq(request):
    return render(request, 'pages/faq.html')

def my_jobs(request):
    return render(request, 'jobseeker/my_jobs.html')



def login_view(request):
    # Since this view only needs to display the forms (the POST is handled in process_login),
    # we just pass prefixed forms to the template.
    user_form = UserLoginForm(prefix='user')
    company_form = CompanyLoginForm(prefix='company')

    return render(request, 'auth/login.html', {
        'user_form': user_form,
        'company_form': company_form
    })

def signup_view(request):
    print("🚀 Signup process started")  # Confirm that view is running

    if request.method == 'POST':
        print(f"🔍 Received POST request: {request.POST}")  # Debugging input data

        is_company = 'is_company' in request.POST  # Check if user is a company
        print(f"🏢 Is company? {is_company}")  # Check if we're processing a company

        if is_company:
            company_form = CompanySignUpForm(request.POST, prefix='company')
            print(f"📋 Company form valid? {company_form.is_valid()}")  # Check if form is valid

            if company_form.is_valid():
                print("✅ Company form passed validation")
                company = company_form.save(commit=False)

                # Hash the password before saving
                company.set_password(company_form.cleaned_data['password1'])
                company.is_company = True
                company.save()

                print(f"🔑 Saved company user: {company.username}, ID: {company.id}")

                # Authenticate AFTER saving
                authenticated_user = authenticate(username=company.username, password=company_form.cleaned_data['password1'])

                print(f"🔍 Authenticate returned: {authenticated_user}")  # See what authenticate() returns

                if authenticated_user:
                    print(f"✅ Company User authenticated: {authenticated_user.username}")
                    login(request, authenticated_user)
                    return redirect('employer_dashboard')
                else:
                    print(f"❌ Authentication failed for {company.username}")
                    print(f"🔍 Saved Password Hash: {company.password}")  # Check if it's hashed correctly

        else:
            user_form = UserSignUpForm(request.POST, prefix='user')

            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.user_industry = user_form.cleaned_data['user_industry'].split(',')
                user.user_location = user_form.cleaned_data['user_location'].split(',')

                # Hash the password before saving
                user.set_password(user_form.cleaned_data['password1'])
                user.is_company = False  # Ensure this is set
                user.save()


                # Authenticate AFTER saving
                authenticated_user = authenticate(username=user.username, password=user_form.cleaned_data['password1'])


                if authenticated_user:
                    login(request, authenticated_user)
                    return redirect('user_dashboard')
                
    else:
        user_form = UserSignUpForm(prefix='user')
        company_form = CompanySignUpForm(prefix='company')

    return render(request, 'auth/signup.html', {'user_form': user_form, 'company_form': company_form})

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
    return render(request, 'company/company_detail.html', {'company': company, 'form': form})

def company_profile(request):
    """
    Display and update the logged-in company's profile.
    """
    if not request.user.is_company:  
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login') 
    
    company = get_object_or_404(CustomUser, id=request.user.id, is_company=True)
    
    job_postings = JobPosting.objects.filter(company=company)

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
    else:
        form = CompanyProfileForm(instance=company)

    return render(request, 'company/company_profile.html', {'company': company, 'form': form, 'job_postings': job_postings,})

@login_required
@require_POST
def leave_review(request, company_id):
    text = request.POST.get('text')
    rating = request.POST.get('rating')

    if not text or not rating:
        messages.error(request, "Both fields are required.")
        return redirect('company_profile')

    company = get_object_or_404(CustomUser, id=company_id, is_company=True)
    Review.objects.create(company=company, text=text, rating=rating)

    messages.success(request, "Review submitted successfully!")
    return redirect('company_profile')


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
    return render(request, 'company/edit_company.html', {'company': company})





logger = logging.getLogger(__name__)

@login_required
@require_POST
@csrf_exempt
def create_job_posting(request):
    logger.debug(f"create_job_posting called by user: {request.user} (is_company={request.user.is_company})")
    
    # Only company accounts can create job postings.
    if not request.user.is_company:
        logger.warning("Non-company user attempted to create a job posting.")
        return JsonResponse({'status': 'error', 'error': 'Not authorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        logger.debug(f"Received data: {data}")

        # Validate and parse the application_deadline
        deadline_str = data.get('application_deadline')
        logger.debug(f"Application deadline received: {deadline_str}")
        if not deadline_str:
            raise ValueError("Application deadline is required.")
        deadline = parse_date(deadline_str)
        logger.debug(f"Parsed deadline: {deadline}")
        if not deadline:
            raise ValueError(f"Invalid date format for application_deadline: {deadline_str}. Expected YYYY-MM-DD.")
        
        # Convert company_reviews to a float if provided
        reviews = data.get('company_reviews')
        logger.debug(f"Company reviews received: {reviews}")
        try:
            reviews = float(reviews) if reviews else None
        except ValueError:
            logger.warning("Failed to convert company_reviews to float. Setting reviews to None.")
            reviews = None

        # Validate required fields
        required_fields = [
            'job_title', 'location', 'contract_type', 
            'job_overview', 'roles_responsibilities', 'required_skills', 
            'perks'
        ]
        for field in required_fields:
            if not data.get(field):
                error_msg = f"Field '{field}' is required but missing or empty."
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                logger.debug(f"Field '{field}' value: {data.get(field)}")

        # Log additional fields (optional)
        logger.debug(f"Optional fields - child_company_name: {data.get('child_company_name')}, work_type: {data.get('work_type')}, "
                     f"salary_range: {data.get('salary_range')}, preferred_skills: {data.get('preferred_skills')}, "
                     f"education_required: {data.get('education_required')}, required_documents: {data.get('required_documents')}, "
                     f"company_overview: {data.get('company_overview')}, why_join_us: {data.get('why_join_us')}")
        
        job_posting = JobPosting.objects.create(
            job_title=data.get('job_title'),
            # Set the company using the logged-in user
            company=request.user,
            # Automatically set company_name from the logged-in user
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
            # Store the deadline as a string 
            application_deadline=deadline_str,
            required_documents=data.get('required_documents'),
            company_overview=data.get('company_overview'),
            why_join_us=data.get('why_join_us'),
            company_reviews=reviews
        )
        logger.info(f"Job posting created successfully with ID: {job_posting.id}")
        return JsonResponse({'status': 'success', 'job_id': job_posting.id})
    except Exception as e:
        logger.exception("Error creating job posting:")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)



@login_required
def start_application(request, job_posting_id):
    """
    Set the job_posting_id in the session and start the multi-step application.
    """
    # Save the job posting ID in the session
    request.session['job_posting_id'] = job_posting_id
    return redirect('apply_step1')


# Step 1: Application Method & Cover Letter
@login_required
def apply_step1(request):
    if request.method == 'POST':
        # Retrieve any existing application data or initialize a new dict
        application_data = request.session.get('application_data', {})
        application_data['application_type'] = request.POST.get('application_type')
        application_data['cover_letter'] = request.POST.get('cover_letter')
        request.session['application_data'] = application_data
        return redirect('apply_step2')
    return render(request, 'application/step1.html')

# Step 2: Personal Information
@login_required
def apply_step2(request):
    application_data = request.session.get('application_data', {})
    application_type = application_data.get('application_type')

    if request.method == 'POST':
        # Basic contact and address
        application_data.update({
            'title': request.POST.get('title'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'preferred_name': request.POST.get('preferred_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'country': request.POST.get('country'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'address_line3': request.POST.get('address_line3'),
            'city': request.POST.get('city'),
            'county': request.POST.get('county'),
            'postcode': request.POST.get('postcode'),
            'skills': request.POST.getlist('skill'),
        })

        # ✅ Handle multiple education entries
        institutions = request.POST.getlist('institution')
        degrees = request.POST.getlist('degree')
        edu_starts = request.POST.getlist('edu_start')
        edu_ends = request.POST.getlist('edu_end')
        education_list = []

        for i in range(len(institutions)):
            if institutions[i] or degrees[i] or edu_starts[i] or edu_ends[i]:
                education_list.append({
                    'university': institutions[i],
                    'degreeType': degrees[i],
                    'dates': f"{edu_starts[i]} - {edu_ends[i]}"
                })

        application_data['education_list'] = education_list

        # ✅ Handle multiple work experience entries
        companies = request.POST.getlist('company_name')
        positions = request.POST.getlist('position')
        work_starts = request.POST.getlist('work_start')
        work_ends = request.POST.getlist('work_end')
        work_experience_list = []

        for i in range(len(companies)):
            if companies[i] or positions[i] or work_starts[i] or work_ends[i]:
                work_experience_list.append({
                    'employer_name': companies[i],
                    'job_title': positions[i],
                    'dates': f"{work_starts[i]} - {work_ends[i]}"
                })

        application_data['work_experience_list'] = work_experience_list

        request.session['application_data'] = application_data
        return redirect('apply_step3')

    # On GET — preload data if using CV
    initial_data = {}
    if application_type == 'cv':
        try:
            user_cv = UserCV.objects.get(user=request.user)
            personal = user_cv.personal_info or {}

            initial_data = {
                'title': personal.get('title', ''),
                'first_name': personal.get('first_name', ''),
                'last_name': personal.get('last_name', ''),
                'preferred_name': personal.get('preferred_name', ''),
                'email': personal.get('email', request.user.email),
                'phone': personal.get('phone', ''),
                'country': personal.get('country', ''),
                'address_line1': personal.get('address_line1', ''),
                'address_line2': personal.get('address_line2', ''),
                'address_line3': personal.get('address_line3', ''),
                'city': personal.get('city', ''),
                'county': personal.get('county', ''),
                'postcode': personal.get('postcode', ''),
                'skills': [s.strip() for s in user_cv.key_skills.split(',')] if user_cv.key_skills else [],
                'education_list': user_cv.education or [],
                'work_experience_list': user_cv.work_experience or [],
            }
        except UserCV.DoesNotExist:
            initial_data = {}

    return render(request, 'application/step2.html', {'initial_data': initial_data})


# Step 3: Job-Specific Questions
@login_required
def apply_step3(request):
    if request.method == 'POST':
        application_data = request.session.get('application_data', {})
        application_data['eligible_to_work'] = request.POST.get('eligible_to_work')
        application_data['previously_employed'] = request.POST.get('previously_employed')
        application_data['require_sponsorship'] = request.POST.get('require_sponsorship')
        application_data['how_did_you_hear'] = request.POST.get('how_did_you_hear')
        application_data['why_good_fit'] = request.POST.get('why_good_fit')
        application_data['salary_expectations'] = request.POST.get('salary_expectations')
        application_data['background_check'] = request.POST.get('background_check')
        request.session['application_data'] = application_data
        return redirect('apply_step4')
    return render(request, 'application/step3.html')

# Step 4: Review and Submit
@login_required
def apply_step4(request):
    application_data = request.session.get('application_data', {})
    if request.method == 'POST':
        # You need a way to know which job posting is being applied to.
        # For example, you might pass a job_posting_id as a GET parameter or store it in session.
        job_posting_id = request.GET.get('job_posting_id') or request.session.get('job_posting_id')
        if not job_posting_id:
            messages.error(request, "Job posting not specified.")
            return redirect('guest')
        job_posting = get_object_or_404(JobPosting, id=job_posting_id)
        
        # Create the JobApplication instance.
        # You can combine the data from various steps into a single JSON field or separate fields.
        job_answers = {
            # Combine personal info and job question answers as needed.
            'personal_info': {
                'title': application_data.get('title'),
                'first_name': application_data.get('first_name'),
                'last_name': application_data.get('last_name'),
                'preferred_name': application_data.get('preferred_name'),
                'email': application_data.get('email'),
                'phone': application_data.get('phone'),
                'address': {
                    'line1': application_data.get('address_line1'),
                    'line2': application_data.get('address_line2'),
                    'line3': application_data.get('address_line3'),
                    'city': application_data.get('city'),
                    'county': application_data.get('county'),
                    'postcode': application_data.get('postcode'),
                },
                'education': {
                    'institution': application_data.get('institution'),
                    'degree': application_data.get('degree'),
                    'edu_start': application_data.get('edu_start'),
                    'edu_end': application_data.get('edu_end'),
                },
                'work_experience': {
                    'company': application_data.get('company_name_exp'),
                    'position': application_data.get('position'),
                    'work_start': application_data.get('work_start'),
                    'work_end': application_data.get('work_end'),
                },
                'skills': application_data.get('skills'),
            },
            'job_questions': {
                'eligible_to_work': application_data.get('eligible_to_work'),
                'previously_employed': application_data.get('previously_employed'),
                'require_sponsorship': application_data.get('require_sponsorship'),
                'how_did_you_hear': application_data.get('how_did_you_hear'),
                'why_good_fit': application_data.get('why_good_fit'),
                'salary_expectations': application_data.get('salary_expectations'),
                'background_check': application_data.get('background_check'),
            }
        }
        job_application = JobApplication.objects.create(
            applicant=request.user,
            job_posting=job_posting,
            company=job_posting.company,  # automatically get the company from the posting
            cover_letter=application_data.get('cover_letter'),
            job_answers=job_answers
        )

        # --- Trigger Notifications ---
        # Create a notification for the applicant
        Notification.objects.create(
            recipient=request.user,
            message=f"Your application {job_application.application_id} for '{job_posting.job_title}' has been submitted.",
            notification_type='application'
        )

        # Create a notification for the company
        Notification.objects.create(
            recipient=job_posting.company,
            message=f"You have received a new application for '{job_posting.job_title}' from {request.user.get_full_name()}.",
            notification_type='application'
        )
        # ------------------------------
        
        
        # Store the generated application ID in the session
        request.session['application_id'] = job_application.application_id

        # Clear the session data for the application
        if 'application_data' in request.session:
            del request.session['application_data']
        if 'job_posting_id' in request.session:
            del request.session['job_posting_id']
        return redirect('application_success')
    # On GET, render the review page showing all collected data
    return render(request, 'application/step4.html', {'application_data': application_data})

@login_required
def application_success(request):
    application_id = request.session.get('application_id', None)
    if 'application_id' in request.session:
        del request.session['application_id']
    return render(request, 'application/success.html', {'application_id': application_id})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # If the request is AJAX or the URL includes ?format=json, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
         unread_count = notifs.filter(is_read=False).count()
         return JsonResponse({'unread_count': unread_count})
    # Otherwise, render the full notifications page
    return render(request, 'jobseeker/notifications.html', {'notifications': notifs})




@login_required
def mark_notification_read(request, notification_id):
    # Retrieve the notification for the current user
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'success'})

# 1. User Applications: List of applications submitted by the logged-in user
@login_required
def user_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    return render(request, 'jobseeker/user_applications.html', {'applications': applications})

# 2. User Application Detail: Detail view for a single application
@login_required
def user_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    return render(request, 'jobseeker/user_application_detail.html', {'application': application})

# 3. Company Applications: List of applications received for jobs posted by the logged-in company
@login_required
def company_applications(request):
    if not request.user.is_company:
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login')
    applications = JobApplication.objects.filter(company=request.user).order_by('-submitted_at')
    return render(request, 'company/company_applications.html', {'applications': applications})

# 4. Company Application Detail: Detail view for a single application for the company
@login_required
def company_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, company=request.user)
    return render(request, 'company/company_application_detail.html', {'application': application})

# 5. Update Application Status: Allow a company to update an application's status
@login_required
def update_application_status(request, application_id, new_status):
    # Validate new_status is one of the allowed statuses
    allowed_statuses = dict(JobApplication.STATUS_CHOICES).keys()
    if new_status not in allowed_statuses:
        messages.error(request, "Invalid status.")
        return redirect('company_applications')
    application = get_object_or_404(JobApplication, id=application_id, company=request.user)
    application.status = new_status
    application.save()
    
    # Notify the applicant about the status update
    Notification.objects.create(
        recipient=application.applicant,
        message=f"Your application {application.application_id} for '{application.job_posting.job_title}' has been updated to '{new_status}'.",
        notification_type='application'
    )
    
    messages.success(request, "Application status updated.")
    return redirect('company_applications')



def job_postings_api(request):
    # Query all job postings and select the required fields.
    job_postings = JobPosting.objects.all().values(
        'id',
        'job_title',
        'location',
        'salary_range',
        'contract_type',
        'job_overview',
        'roles_responsibilities',
        'required_skills'
    )
    # Return the results as a JSON response.
    return JsonResponse(list(job_postings), safe=False)

@csrf_exempt
@require_POST
@login_required
def upload_cv(request):
    user = request.user
    file = request.FILES.get('cv_file')

    if not file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        text = extract_text_from_pdf(temp_path)
        structured = classify_resume_with_together(text)

        structured['education'] = remove_duplicate_education(structured.get('education', []))
        structured['work_experience'] = remove_duplicate_experience(structured.get('work_experience', []))

        skills_raw = structured.get("skills", [])
        technical_skills, soft_skills = split_skills(skills_raw)

        cv, _ = CVApplication.objects.update_or_create(
            user=user,
            defaults={
                'full_name': user.get_full_name(),
                'email': user.email or 'unknown@example.com',
                'phone': structured.get("personal_info", {}).get("phone", "N/A"),
                'address': structured.get("personal_info", {}).get("address", "N/A"),
                'postcode': structured.get("personal_info", {}).get("postcode", "N/A"),
                'key_skills': ", ".join(sorted(soft_skills)),
                'technical_skills': ", ".join(sorted(technical_skills)),
                'languages': ", ".join(structured.get("languages", [])),
                'motivation_statement': structured.get("motivations", ""),
                'fit_for_role': structured.get("fit_for_role", ""),
                'career_aspirations': structured.get("career_aspirations", ""),
                'preferred_start_date': parse_date(structured.get("preferred_start_date", "")) if structured.get("preferred_start_date") else None,
            }
        )

        cv.cv_file.save(file.name, file)
        cv.save()


        user_cv, _ = UserCV.objects.get_or_create(user=user)
        user_cv.personal_info = structured.get("personal_info", {})

        if user_cv.education is None:
            user_cv.education = []
        if user_cv.work_experience is None:
            user_cv.work_experience = []

        user_cv.education = [
            {
                'university': edu.get("university", ""),
                'degreeType': edu.get("degree_type", ""),
                'fieldOfStudy': edu.get("field_of_study", ""),
                'grade': edu.get("grade", ""),
                'dates': edu.get("dates", ""),
                'modules': edu.get("modules", "")
            }
            for edu in structured.get("education", [])
        ]


        user_cv.work_experience = [
            {
                'employer_name': exp.get("company", ""),
                'job_title': exp.get("job_title", ""),
                'responsibilities': exp.get("responsibilities", ""),
                'dates': exp.get("dates", "")
            }
            for exp in structured.get("work_experience", [])
        ]

        existing_skills = set(user_cv.key_skills.split(",")) if user_cv.key_skills else set()
        new_skills = set(soft_skills)
        user_cv.key_skills = ", ".join(sorted(existing_skills.union(new_skills)))

        user_cv.technical_skills = user_cv.technical_skills or ", ".join(technical_skills)
        user_cv.languages = user_cv.languages or ", ".join(structured.get("languages", []))
        user_cv.interest = user_cv.interest or cv.motivation_statement
        user_cv.fit_for_role = user_cv.fit_for_role or cv.fit_for_role
        user_cv.aspirations = user_cv.aspirations or cv.career_aspirations

        user_cv.save()
        os.remove(temp_path)

        return JsonResponse({
            'success': True,
            'message': 'CV updated from upload.',
            'data': {
                'personalInfo': user_cv.personal_info,
                'education': user_cv.education,
                'workExperience': user_cv.work_experience,
                'skills': {
                    'keySkills': user_cv.key_skills,
                    'technicalSkills': user_cv.technical_skills,
                    'languages': user_cv.languages
                }
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@csrf_exempt
@login_required
@require_POST
def upload_raw_cv(request):
    user = request.user
    file = request.FILES.get('cv_file')
    if not file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    try:
        uploaded_cv, _ = UploadedCV.objects.get_or_create(user=user)

        # Delete old file if it exists
        if uploaded_cv.file and os.path.exists(uploaded_cv.file.path):
            os.remove(uploaded_cv.file.path)

        # Save new one
        uploaded_cv.file.save(file.name, file)
        uploaded_cv.save()

        return JsonResponse({
            'success': True,
            'filename': uploaded_cv.file.name,
            'uploaded_at': uploaded_cv.uploaded_at.strftime("%Y-%m-%d %H:%M")
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def get_user_documents(request):
    user = request.user
    if UserDocument.objects.filter(user=user).count() >= 5:
        return JsonResponse({'success': False, 'error': 'You can only upload up to 5 documents.'}, status=400)

    uploaded_file = request.FILES.get('document')
    if not uploaded_file:
        return JsonResponse({'success': False, 'error': 'No file uploaded.'}, status=400)

    doc = UserDocument.objects.create(user=user, file=uploaded_file)
    return JsonResponse({
        'success': True,
        'filename': doc.file.name.split('/')[-1],
        'file_url': doc.file.url,
        'uploaded_at': doc.uploaded_at.strftime('%b %d, %Y %I:%M %p'),
        'uploaded_at_human': 'just now'
    })
@csrf_exempt
@login_required
@require_POST
def delete_user_document(request):
    file_name = request.POST.get('filename')
    doc = UserDocument.objects.filter(user=request.user, file__icontains=file_name).first()


    if doc:
        doc.file.delete()
        doc.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Document not found'})

@login_required
def profile_settings(request):
    user = request.user  # Get the logged-in user
    
    if request.method == 'POST':
        if 'update_details' in request.POST:
            details_form = UserUpdateForm(request.POST, request.FILES, instance=user)  # ✅ Include request.FILES for image upload
            password_form = MyPasswordChangeForm(user=user)
            
            if details_form.is_valid():
                details_form.save()
                messages.success(request, "Your details have been updated.")
                return redirect('settings')
            else:
                messages.error(request, "Update failed.")

        elif 'change_password' in request.POST:
            details_form = UserUpdateForm(instance=user)
            password_form = MyPasswordChangeForm(user=user, data=request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed.")
                return redirect('settings')
            else:
                messages.error(request, "Password change failed.")

        elif 'delete_account' in request.POST:
            username = user.username
            
            # ✅ Delete profile photo before deleting the account (optional)
            if user.user_profile_photo:
                if os.path.isfile(user.user_profile_photo.path):
                    os.remove(user.user_profile_photo.path)
            
            user.delete()
            logout(request)
            messages.success(request, f"Account '{username}' has been deleted successfully.")
            return redirect('guest')

    else:
        details_form = UserUpdateForm(instance=user)
        password_form = MyPasswordChangeForm(user=user)
        

    return render(request, 'pages/settings.html', {
        'details_form': details_form,
        'password_form': password_form,
    })

@csrf_exempt
@login_required
@require_POST
def delete_raw_cv(request):
    try:
        uploaded_cv = UploadedCV.objects.filter(user=request.user).first()
        if uploaded_cv and uploaded_cv.file:
            # Delete the file from storage
            if os.path.exists(uploaded_cv.file.path):
                os.remove(uploaded_cv.file.path)
            uploaded_cv.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No uploaded CV found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delete_account(request):
    """Allow a logged-in user to delete their own account."""
    if request.method == 'POST':
        user = request.user
        username = user.username
        try:
            with transaction.atomic():
                user.delete()
                logout(request)
                messages.success(request, f"Account '{username}' has been deleted successfully.")
        except Exception as e:
            messages.error(request, "An error occurred while deleting your account.")

        return redirect('guest')
    return render(request, 'confirm_delete_account.html')


def help_centre(request):
    return render(request, 'pages/help_centre.html')

def accessibility(request):
    return render(request, 'pages/accessibility.html')

@login_required
def add_job_by_code(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        code = data.get('code')
        if not code:
            return JsonResponse({'success': False, 'error': 'No code provided.'}, status=400)

        user = request.user
        job_application = JobApplication.objects.filter(application_id=code).first()
        # If your code is stored in application_id or another field, adjust accordingly.

        if not job_application:
            return JsonResponse({'success': False, 'error': 'Job application not found.'}, status=404)
        if job_application.applicant != user:
            return JsonResponse({'success': False, 'error': 'This job application does not belong to you.'}, status=403)

        # Mark tracked
        job_application.tracked = True
        job_application.save()

        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from tutorials.models.applications import JobApplication  # adjust import to match your structure

@login_required
def tracked_jobs_api(request):
    # The user must be logged in or else @login_required will redirect to login.
    user = request.user
    
    # Filter for tracked applications. 
    tracked_apps = JobApplication.objects.filter(applicant=user, tracked=True)

    # Build a list of dicts for JSON output.
    data = []
    for app in tracked_apps:
        data.append({
            'id': app.id,
            'title': app.job_posting.job_title,
            'company': str(app.job_posting.company),
            # If you store a current_stage or similar, adapt accordingly:
            'currentStage': 0,  
        })

    return JsonResponse(data, safe=False)


def normalize_edu(e):
    return (
        e.get("university", "").strip().lower(),
        e.get("degree_type", "").strip().lower(),
        e.get("field_of_study", "").strip().lower(),
        e.get("grade", "").strip().lower(),
        e.get("dates", "").strip().lower(),
        e.get("modules", "").strip().lower(),
    )

def normalize_exp(e):
    return (
        e.get("company", "").strip().lower(),
        e.get("job_title", "").strip().lower(),
        e.get("responsibilities", "").strip().lower(),
        e.get("dates", "").strip().lower(),
    )

def normalize_str(s):
    return str(s or '').strip().lower().replace('–', '-').replace('—', '-').replace('’', "'")
    
def remove_duplicate_education(entries):
    seen = set()
    cleaned = []
    for edu in entries:
        key = f"{normalize_str(edu.get('university'))}|{normalize_str(edu.get('degreeType'))}|{normalize_str(edu.get('fieldOfStudy'))}|{normalize_str(edu.get('dates'))}"
        if key not in seen:
            seen.add(key)
            cleaned.append(edu)
    return cleaned

def remove_duplicate_experience(entries):
    seen = set()
    cleaned = []
    for exp in entries:
        key = f"{normalize_str(exp.get('employer'))}|{normalize_str(exp.get('jobTitle'))}|{normalize_str(exp.get('dates'))}"
        if key not in seen:
            seen.add(key)
            cleaned.append(exp)
    return cleaned
