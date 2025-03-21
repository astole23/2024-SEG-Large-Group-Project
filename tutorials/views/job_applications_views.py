import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date

from tutorials.models.jobposting import JobPosting
from tutorials.models.applications import JobApplication, Notification
from tutorials.models.standard_cv import UserCV

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


