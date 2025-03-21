from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.dateparse import parse_date

import logging
import json

from tutorials.models.jobposting import JobPosting
from tutorials.models.applications import JobApplication, Notification
from tutorials.models.company_review import Review
from tutorials.models.accounts import CustomUser
from tutorials.forms import (CompanyProfileForm)
from tutorials.helpers.company_helpers import validate_required_fields, parse_reviews, parse_deadline
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


def company_detail(request, company_id):

    company = get_object_or_404(CustomUser, id=company_id, is_company=True)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
    else:
        form = CompanyProfileForm(instance=company)
    return render(request, 'company/company_detail.html', {'company': company, 'form': form})

@login_required
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
        return render(request, 'company/edit_company.html', {
            'company': company,
            'message': 'Company details updated!'
        })
    return render(request, 'company/edit_company.html', {'company': company})


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

logger = logging.getLogger(__name__)

def create_job_posting(request):
    logger.debug(f"create_job_posting called by user: {request.user} (is_company={request.user.is_company})")

    if not request.user.is_company:
        logger.warning("Non-company user attempted to create a job posting.")
        return JsonResponse({'status': 'error', 'error': 'Not authorized'}, status=403)

    try:
        data = json.loads(request.body)
        logger.debug(f"Received data: {data}")

        # Parse deadline
        deadline_str = data.get('application_deadline')
        deadline = parse_deadline(deadline_str)
        logger.debug(f"Parsed deadline: {deadline}")

        # Parse reviews
        reviews = parse_reviews(data.get('company_reviews'))
        logger.debug(f"Company reviews received: {reviews}")

        # Validate required fields
        required_fields = [
            'job_title', 'location', 'contract_type', 
            'job_overview', 'roles_responsibilities', 'required_skills', 
            'perks'
        ]
        validate_required_fields(data, required_fields)

        # Log optional fields (for debugging)
        logger.debug(f"Optional fields - department: {data.get('department')}, work_type: {data.get('work_type')}, "
                     f"salary_range: {data.get('salary_range')}, preferred_skills: {data.get('preferred_skills')}, "
                     f"education_required: {data.get('education_required')}, required_documents: {data.get('required_documents')}, "
                     f"company_overview: {data.get('company_overview')}, why_join_us: {data.get('why_join_us')}")

        # Create the job posting
        job_posting = JobPosting.objects.create(
            job_title=data.get('job_title'),
            company=request.user,
            department=data.get('department'),
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