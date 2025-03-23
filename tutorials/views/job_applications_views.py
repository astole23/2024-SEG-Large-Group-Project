import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from tutorials.models.jobposting import JobPosting
from tutorials.models.applications import JobApplication, Notification
from tutorials.models.standard_cv import UserCV


def get_application_data_from_session(request):
    """Retrieve application data from session."""
    return request.session.get('application_data', {})


def save_application_data_to_session(request, data):
    """Save application data to session."""
    request.session['application_data'] = data


def get_initial_data_from_cv(request, application_type):
    """Preload data from user's CV if 'cv' application type is selected."""
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

    return initial_data


@login_required
def start_application(request, job_posting_id):
    """Set the job posting ID in the session and start the multi-step application."""
    request.session['job_posting_id'] = job_posting_id
    return redirect('apply_step1')


@login_required
def apply_step1(request):
    if request.method == 'POST':
        application_data = get_application_data_from_session(request)
        application_data.update({
            'application_type': request.POST.get('application_type'),
            'cover_letter': request.POST.get('cover_letter')
        })
        save_application_data_to_session(request, application_data)
        return redirect('apply_step2')
    return render(request, 'application/step1.html')


@login_required
def apply_step2(request):
    application_data = get_application_data_from_session(request)
    application_type = application_data.get('application_type')

    if request.method == 'POST':
        # Personal info and address
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

        # Handle education entries
        education_list = [
            {
                'university': institution,
                'degreeType': degree,
                'dates': f"{start} - {end}"
            }
            for institution, degree, start, end in zip(
                request.POST.getlist('institution'),
                request.POST.getlist('degree'),
                request.POST.getlist('edu_start'),
                request.POST.getlist('edu_end')
            ) if institution or degree or start or end
        ]
        application_data['education_list'] = education_list

        # Handle work experience entries
        work_experience_list = [
            {
                'employer_name': company,
                'job_title': position,
                'dates': f"{start} - {end}"
            }
            for company, position, start, end in zip(
                request.POST.getlist('company_name'),
                request.POST.getlist('position'),
                request.POST.getlist('work_start'),
                request.POST.getlist('work_end')
            ) if company or position or start or end
        ]
        application_data['work_experience_list'] = work_experience_list

        save_application_data_to_session(request, application_data)
        return redirect('apply_step3')

    initial_data = get_initial_data_from_cv(request, application_type)
    return render(request, 'application/step2.html', {'initial_data': initial_data})


@login_required
def apply_step3(request):
    if request.method == 'POST':
        application_data = get_application_data_from_session(request)
        application_data.update({
            'eligible_to_work': request.POST.get('eligible_to_work'),
            'previously_employed': request.POST.get('previously_employed'),
            'require_sponsorship': request.POST.get('require_sponsorship'),
            'how_did_you_hear': request.POST.get('how_did_you_hear'),
            'why_good_fit': request.POST.get('why_good_fit'),
            'salary_expectations': request.POST.get('salary_expectations'),
            'background_check': request.POST.get('background_check')
        })
        save_application_data_to_session(request, application_data)
        return redirect('apply_step4')
    return render(request, 'application/step3.html')


@login_required
def apply_step4(request):
    application_data = get_application_data_from_session(request)
    if request.method == 'POST':
        job_posting_id = request.GET.get('job_posting_id') or request.session.get('job_posting_id')
        if not job_posting_id:
            messages.error(request, "Job posting not specified.")
            return redirect('guest')
        job_posting = get_object_or_404(JobPosting, id=job_posting_id)

        # Merge all the collected data into the job_answers JSON
        job_answers = {
            'application_type': application_data.get('application_type'),
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
                'skills': application_data.get('skills'),
            },
            'education_list': application_data.get('education_list'),
            'work_experience_list': application_data.get('work_experience_list'),
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
            company=job_posting.company,
            cover_letter=application_data.get('cover_letter'),
            job_answers=job_answers
        )

        # Notifications
        Notification.objects.create(
            recipient=request.user,
            message=f"Your application {job_application.application_id} for '{job_posting.job_title}' has been submitted.",
            notification_type='application'
        )
        Notification.objects.create(
            recipient=job_posting.company,
            message=f"You have received a new application for '{job_posting.job_title}' from {request.user.get_full_name()}.",
            notification_type='application'
        )

        # Clear session data and store application ID
        request.session['application_id'] = job_application.application_id
        request.session.pop('application_data', None)
        request.session.pop('job_posting_id', None)

        return redirect('application_success')

    return render(request, 'application/step4.html', {'application_data': application_data})



@login_required
def application_success(request):
    application_id = request.session.get('application_id', None)
    request.session.pop('application_id', None)
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
        if not job_application:
            return JsonResponse({'success': False, 'error': 'Job application not found.'}, status=404)
        if job_application.applicant != user:
            return JsonResponse({'success': False, 'error': 'This job application does not belong to you.'}, status=403)

        job_application.tracked = True
        job_application.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
