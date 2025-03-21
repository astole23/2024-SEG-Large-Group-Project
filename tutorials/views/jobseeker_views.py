import json
import os
import tempfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from django.utils.dateparse import parse_date
from django.utils.timesince import timesince
from django.core.serializers.json import DjangoJSONEncoder

from tutorials.models.applications import JobApplication, Notification
from tutorials.models.standard_cv import CVApplication, UserCV
from tutorials.models.user_dashboard import UploadedCV, UserDocument
from tutorials.auto_fill import extract_text_from_pdf, classify_resume_with_together
from tutorials.views.function_views import split_skills


from tutorials.helpers.base_helpers import remove_duplicate_education, remove_duplicate_experience, normalize_to_string_list


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

def my_jobs(request):
    return render(request, 'jobseeker/my_jobs.html')

def delete_job(request, job_id):
    job = get_object_or_404(JobApplication, id=job_id, applicant=request.user)
    job.delete()
    return JsonResponse({'success': True})

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

@login_required
def user_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-submitted_at')
    return render(request, 'jobseeker/user_applications.html', {'applications': applications})

# 2. User Application Detail: Detail view for a single application
@login_required
def user_application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    return render(request, 'jobseeker/user_application_detail.html', {'application': application})

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

def my_jobs(request):
    return render(request, 'jobseeker/my_jobs.html')

def status(request):
    return render(request, 'jobseeker/status.html')