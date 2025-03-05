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
from django.utils.dateparse import parse_date
from tutorials.forms import (
    UserLoginForm, CompanyLoginForm,
    UserSignUpForm, CompanySignUpForm,
    CompanyProfileForm
)
from tutorials.models.applications import JobApplication
from tutorials.models.applications import Notification

import logging



CustomUser = get_user_model()

@login_required
def employer_dashboard(request):
    # Only allow company users
    if not request.user.is_company:
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login')  
    
    # Filter job postings by the logged-in company
    job_postings = JobPosting.objects.filter(company=request.user).order_by('-created_at')
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
            company_name=request.user.company_name or request.user.username,
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
    return render(request, 'step1.html')

# Step 2: Personal Information
@login_required
def apply_step2(request):
    if request.method == 'POST':
        application_data = request.session.get('application_data', {})
        # Save personal info (adjust field names to match your form)
        application_data['title'] = request.POST.get('title')
        application_data['first_name'] = request.POST.get('first_name')
        application_data['last_name'] = request.POST.get('last_name')
        application_data['preferred_name'] = request.POST.get('preferred_name')
        application_data['email'] = request.POST.get('email')
        application_data['phone'] = request.POST.get('phone')
        application_data['country'] = request.POST.get('country')
        application_data['address_line1'] = request.POST.get('address_line1')
        application_data['address_line2'] = request.POST.get('address_line2')
        application_data['address_line3'] = request.POST.get('address_line3')
        application_data['city'] = request.POST.get('city')
        application_data['county'] = request.POST.get('county')
        application_data['postcode'] = request.POST.get('postcode')
        # For education, work experience, skills – store as needed (example below)
        application_data['institution'] = request.POST.get('institution')
        application_data['degree'] = request.POST.get('degree')
        application_data['edu_start'] = request.POST.get('edu_start')
        application_data['edu_end'] = request.POST.get('edu_end')
        application_data['company_name_exp'] = request.POST.get('company_name')
        application_data['position'] = request.POST.get('position')
        application_data['work_start'] = request.POST.get('work_start')
        application_data['work_end'] = request.POST.get('work_end')
        # You may also process dynamic skills (this example assumes one field)
        application_data['skills'] = request.POST.getlist('skill')
        
        request.session['application_data'] = application_data
        return redirect('apply_step3')
    return render(request, 'step2.html')

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
    return render(request, 'step3.html')

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
    return render(request, 'step4.html', {'application_data': application_data})

@login_required
def application_success(request):
    application_id = request.session.get('application_id', None)
    if 'application_id' in request.session:
        del request.session['application_id']
    return render(request, 'success.html', {'application_id': application_id})

@login_required
def notifications(request):
    # Retrieve notifications for the current user, ordered by most recent first.
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifs})



@login_required
def mark_notification_read(request, notification_id):
    # Retrieve the notification for the current user
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'success'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tutorials.models.applications import JobApplication, Notification
from tutorials.models.jobposting import JobPosting

# 1. User Applications: List of applications submitted by the logged-in user
@login_required
def user_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    return render(request, 'user_applications.html', {'applications': applications})

# 2. User Application Detail: Detail view for a single application
@login_required
def user_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    return render(request, 'user_application_detail.html', {'application': application})

# 3. Company Applications: List of applications received for jobs posted by the logged-in company
@login_required
def company_applications(request):
    if not request.user.is_company:
        messages.error(request, "Access restricted to company accounts only.")
        return redirect('login')
    applications = JobApplication.objects.filter(company=request.user).order_by('-submitted_at')
    return render(request, 'company_applications.html', {'applications': applications})

# 4. Company Application Detail: Detail view for a single application for the company
@login_required
def company_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, company=request.user)
    return render(request, 'company_application_detail.html', {'application': application})

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
        'company_name',
        'location',
        'salary_range',
        'contract_type',
        'job_overview',
        'roles_responsibilities',
        'required_skills'
    )
    # Return the results as a JSON response.
    return JsonResponse(list(job_postings), safe=False)
