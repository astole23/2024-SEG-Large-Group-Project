import json
import os
import tempfile
import traceback
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.timezone import localtime
from django.utils.dateparse import parse_date
from django.utils.timesince import timesince
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator

import logging

from tutorials.models.jobposting import JobPosting
from tutorials.models.company_review import Review
from tutorials.models.accounts import CustomUser
from tutorials.models.applications import JobApplication, Notification
from tutorials.forms import (
    UserLoginForm, CompanyLoginForm,
    UserSignUpForm, CompanySignUpForm,
    CompanyProfileForm, UserUpdateForm, MyPasswordChangeForm)
from tutorials.models.standard_cv import CVApplication, UserCV
from tutorials.models.user_dashboard import UploadedCV, UserDocument
from tutorials.auto_fill import extract_text_from_pdf, classify_resume_with_together
from tutorials.views.function_views import split_skills




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

    return render(request, 'pages/search.html', context)


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