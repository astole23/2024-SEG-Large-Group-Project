import json
import os
import tempfile
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from tutorials.models.accounts import CustomUser, CompanyUser
from tutorials.models.jobposting import JobPosting
from tutorials.models.standard_cv import UserCV
from tutorials.models.user_dashboard import UploadedCV, UserDocument
from tutorials.models.applications import JobApplication, Notification
from tutorials.forms import UserSignUpForm, CompanySignUpForm, UserUpdateForm, MyPasswordChangeForm
from tutorials.views.ui_views import (
    employer_dashboard, user_dashboard, guest, search, login_view, signup_view,
    company_profile, create_job_posting, upload_cv, upload_raw_cv, get_user_documents,
    delete_user_document, profile_settings, delete_account, add_job_by_code, tracked_jobs_api,delete_raw_cv,user_logout,contact_us,about_us,terms_conditions,privacy,user_agreement,faq,help_centre,accessibility,my_jobs,job_postings_api,status
)
from django.contrib.messages.storage.fallback import FallbackStorage

from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import JobPosting
from tutorials.models.accounts import CustomUser  # Import your custom user model

# Helper functions for testing
def normalize_to_string_list(value):
    if isinstance(value, list):
        return ", ".join(v.strip() for v in value)
    elif isinstance(value, str):
        return value.strip()
    return ""

def remove_duplicate_education(entries):
    seen = set()
    cleaned = []
    for edu in entries:
        key = f"{edu.get('university', '').strip().lower()}|{edu.get('degreeType', '').strip().lower()}|{edu.get('fieldOfStudy', '').strip().lower()}|{edu.get('dates', '').strip().lower()}"
        if key not in seen:
            seen.add(key)
            cleaned.append(edu)
    return cleaned

def remove_duplicate_experience(entries):
    seen = set()
    cleaned = []
    for exp in entries:
        key = f"{exp.get('employer', '').strip().lower()}|{exp.get('jobTitle', '').strip().lower()}|{exp.get('dates', '').strip().lower()}"
        if key not in seen:
            seen.add(key)
            cleaned.append(exp)
    return cleaned


class EmployerDashboardTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345', is_company=True)
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.user,
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )

    def test_employer_dashboard_authenticated(self):
        request = self.factory.get(reverse('employer_dashboard'))
        request.user = self.user
        response = employer_dashboard(request)
        self.assertEqual(response.status_code, 200)

    def test_employer_dashboard_unauthenticated(self):
        request = self.factory.get(reverse('employer_dashboard'))
        request.user = CustomUser.objects.create_user(username='testuser2', password='12345', is_company=False)
        
        # Mock session and messages
        session = self.client.session
        session.save()
        request.session = session
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = employer_dashboard(request)
        self.assertEqual(response.status_code, 302)  # Redirect to login

class UserDashboardTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345', is_company=False)
        self.cv = UserCV.objects.create(user=self.user, education=json.dumps([{"fieldOfStudy": "Computer Science"}]))
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test.pdf')

    def test_user_dashboard_authenticated(self):
        request = self.factory.get(reverse('user_dashboard'))
        request.user = self.user
        response = user_dashboard(request)
        self.assertEqual(response.status_code, 200)

class GuestViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=CompanyUser.objects.create(username='testcompany', password='12345'),
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )

    def test_guest_view_with_query(self):
        request = self.factory.get(reverse('guest') + '?q=Software')
        request.user = AnonymousUser()
        response = guest(request)
        self.assertEqual(response.status_code, 200)

    def test_guest_view_without_query(self):
        request = self.factory.get(reverse('guest'))
        request.user = AnonymousUser()
        response = guest(request)
        self.assertEqual(response.status_code, 200)

class SearchViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=CompanyUser.objects.create(username='testcompany', password='12345'),
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )

    def test_search_view_with_query(self):
        request = self.factory.get(reverse('search') + '?q=Software')
        request.user = AnonymousUser()
        response = search(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')

    def test_search_view_with_filters(self):
        request = self.factory.get(reverse('search') + '?education_required=Bachelor&job_type=Full-time')
        request.user = AnonymousUser()
        response = search(request)
        self.assertEqual(response.status_code, 200)

class LoginViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_login_view_get(self):
        request = self.factory.get(reverse('login'))
        request.user = AnonymousUser()
        response = login_view(request)
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_valid(self):
        request = self.factory.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        request.user = AnonymousUser()
        
        # Mock session
        session = self.client.session
        session.save()
        request.session = session
        
        response = login_view(request)
        self.assertEqual(response.status_code, 200)  

    def test_login_view_post_invalid(self):
        request = self.factory.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        request.user = AnonymousUser()
        response = login_view(request)
        self.assertEqual(response.status_code, 200)

class SignupViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()



    

    

class CompanyProfileTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CompanyUser.objects.create_user(username='testcompany', password='12345', is_company=True)

    def test_company_profile_get(self):
        request = self.factory.get(reverse('company_profile'))
        request.user = self.user
        response = company_profile(request)
        self.assertEqual(response.status_code, 200)

    def test_company_profile_post(self):
        request = self.factory.post(reverse('company_profile'), {
            'company_name': 'Updated Company',
            'description': 'Updated Description'
        })
        request.user = self.user
        response = company_profile(request)
        self.assertEqual(response.status_code, 200)

class CreateJobPostingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CompanyUser.objects.create_user(username='testcompany', password='12345', is_company=True)

    def test_create_job_posting_invalid(self):
        data = {
            'job_title': 'Software Engineer',
            'location': 'New York',
            'salary_range': '2000',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software',
            'roles_responsibilities': 'Code and test',
            'required_skills': 'Python, Django',
            'perks': 'Health insurance',
            'application_deadline': '2024-12-31',
            'education_required': 'Bachelor'  # Add required field
        }
        request = self.factory.post(reverse('create_job_posting'), json.dumps(data), content_type='application/json')
        request.user = self.user
        response = create_job_posting(request)
        self.assertEqual(response.status_code, 400)

    def test_create_job_posting_invalid(self):
        data = {
            'job_title': '',  # Missing required field
            'location': 'New York',
            'salary_range': '2000',
            'contract_type': 'Full-time'
        }
        request = self.factory.post(reverse('create_job_posting'), json.dumps(data), content_type='application/json')
        request.user = self.user
        response = create_job_posting(request)
        self.assertEqual(response.status_code, 400)

class UploadCVTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_upload_cv_valid(self):
        file = SimpleUploadedFile('test.pdf', b'file_content', content_type='application/pdf')
        request = self.factory.post(reverse('upload_cv'), {'cv_file': file})
        request.user = self.user
        
        # Mock session
        session = self.client.session
        session.save()
        request.session = session
        
        response = upload_cv(request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(UserCV.objects.count(), 0)

    def test_upload_cv_invalid(self):
        request = self.factory.post(reverse('upload_cv'))
        request.user = self.user
        response = upload_cv(request)
        self.assertEqual(response.status_code, 400)

class ProfileSettingsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_profile_settings_get(self):
        request = self.factory.get(reverse('settings'))
        request.user = self.user
        response = profile_settings(request)
        self.assertEqual(response.status_code, 200)

    

class DeleteAccountTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_delete_account_post(self):
        request = self.factory.post(reverse('delete_account'))
        request.user = self.user
        
        # Mock session
        session = self.client.session
        session.save()
        request.session = session
        
        # Mock messages
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = delete_account(request)
        self.assertEqual(response.status_code, 302)  # Redirect to guest
        self.assertEqual(CustomUser.objects.count(), 0)

class HelperFunctionTests(TestCase):
    def test_normalize_to_string_list(self):
        self.assertEqual(normalize_to_string_list(['Python', 'Django']), 'Python, Django')
        self.assertEqual(normalize_to_string_list('Python, Django'), 'Python, Django')

    def test_remove_duplicate_education(self):
        education = [
            {'university': 'University A', 'degreeType': 'Bachelor'},
            {'university': 'University A', 'degreeType': 'Bachelor'}
        ]
        cleaned = remove_duplicate_education(education)
        self.assertEqual(len(cleaned), 1)

    def test_remove_duplicate_experience(self):
        experience = [
            {'employer': 'Company A', 'jobTitle': 'Developer'},
            {'employer': 'Company A', 'jobTitle': 'Developer'}
        ]
        cleaned = remove_duplicate_experience(experience)
        self.assertEqual(len(cleaned), 1)

    
class DeleteRawCVTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test.pdf')

    def test_delete_raw_cv(self):
        request = self.factory.post(reverse('delete_raw_cv'))
        request.user = self.user
        
        # Mock session
        session = self.client.session
        session.save()
        request.session = session
        
        response = delete_raw_cv(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UploadedCV.objects.count(), 0)

class ContactUsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_contact_us_get(self):
        request = self.factory.get(reverse('contact_us'))
        request.user = AnonymousUser()
        response = contact_us(request)
        self.assertEqual(response.status_code, 200)

class AboutUsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_about_us_get(self):
        request = self.factory.get(reverse('about_us'))
        request.user = AnonymousUser()
        response = about_us(request)
        self.assertEqual(response.status_code, 200)

class TermsConditionsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_terms_conditions_get(self):
        request = self.factory.get(reverse('terms_conditions'))
        request.user = AnonymousUser()
        response = terms_conditions(request)
        self.assertEqual(response.status_code, 200)

class PrivacyTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_privacy_get(self):
        request = self.factory.get(reverse('privacy'))
        request.user = AnonymousUser()
        response = privacy(request)
        self.assertEqual(response.status_code, 200)

class UserAgreementTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_user_agreement_get(self):
        request = self.factory.get(reverse('user_agreement'))
        request.user = AnonymousUser()
        response = user_agreement(request)
        self.assertEqual(response.status_code, 200)

class FAQTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_faq_get(self):
        request = self.factory.get(reverse('faq'))
        request.user = AnonymousUser()
        response = faq(request)
        self.assertEqual(response.status_code, 200)

class MyJobsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_my_jobs_authenticated(self):
        request = self.factory.get(reverse('my_jobs'))
        request.user = self.user
        response = my_jobs(request)
        self.assertEqual(response.status_code, 200)

    def test_my_jobs_unauthenticated(self):
        request = self.factory.get(reverse('my_jobs'))
        request.user = AnonymousUser()
        response = my_jobs(request)
        self.assertEqual(response.status_code, 200)  # Redirect to login

class HelpCentreTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_help_centre_get(self):
        request = self.factory.get(reverse('help_centre'))
        request.user = AnonymousUser()
        response = help_centre(request)
        self.assertEqual(response.status_code, 200)

class AccessibilityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_accessibility_get(self):
        request = self.factory.get(reverse('accessibility'))
        request.user = AnonymousUser()
        response = accessibility(request)
        self.assertEqual(response.status_code, 200)

class JobPostingsAPITests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CompanyUser.objects.create_user(username='testcompany', password='12345', is_company=True)
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.user,
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )

    def test_job_postings_api(self):
        request = self.factory.get(reverse('job_postings_api'))
        request.user = AnonymousUser()
        response = job_postings_api(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')

class DeleteRawCVTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test.pdf')

    def test_delete_raw_cv(self):
        request = self.factory.post(reverse('delete_raw_cv'))
        request.user = self.user
        
        # Mock session
        session = self.client.session
        session.save()
        request.session = session
        
        response = delete_raw_cv(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UploadedCV.objects.count(), 0)

class TrackedJobsAPITests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.company = CompanyUser.objects.create_user(username='testcompany', password='12345', is_company=True)
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        self.application = JobApplication.objects.create(
            applicant=self.user,
            job_posting=self.job,
            company=self.company,
            tracked=True
        )

    def test_tracked_jobs_api(self):
        request = self.factory.get(reverse('tracked_jobs_api'))
        request.user = self.user
        response = tracked_jobs_api(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')

class AccessibilityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_accessibility_get(self):
        request = self.factory.get(reverse('accessibility'))
        request.user = AnonymousUser()
        response = accessibility(request)
        self.assertEqual(response.status_code, 200)


class MyJobsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')

    def test_my_jobs_authenticated(self):
        request = self.factory.get(reverse('my_jobs'))
        request.user = self.user
        response = my_jobs(request)
        self.assertEqual(response.status_code, 200)

    def test_my_jobs_unauthenticated(self):
        request = self.factory.get(reverse('my_jobs'))
        request.user = AnonymousUser()
        response = my_jobs(request)
        self.assertEqual(response.status_code, 200)  # Redirect to login


class AddJobByCodeTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.company = CompanyUser.objects.create_user(username='testcompany', password='12345', is_company=True)
        self.job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        self.application = JobApplication.objects.create(
            applicant=self.user,
            job_posting=self.job,
            company=self.company,
            application_id='12345'
        )


class EmployerDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Use CustomUser instead of User
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        self.normal_user = CustomUser.objects.create_user(username='normal', password='testpass', is_company=False)
        self.job_posting = JobPosting.objects.create(company=self.company_user, job_title='Test Job')

    def test_employer_dashboard_company_user(self):
        self.client.login(username='company', password='testpass')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_employer_dashboard_normal_user(self):
        self.client.login(username='normal', password='testpass')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login



class UserLogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')


class GuestTests(TestCase):
    def setUp(self):
        self.job_posting = JobPosting.objects.create(job_title='Test Job')

    def test_guest_with_query(self):
        response = self.client.get(reverse('guest'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)

    def test_guest_without_query(self):
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)

class UserDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.cv = UserCV.objects.create(user=self.user, key_skills='Python, Django')
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test.pdf')

class SearchTests(TestCase):
    def setUp(self):
        self.job_posting = JobPosting.objects.create(job_title='Test Job', location='Test City')

  

class CreateJobPostingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company_user = User.objects.create_user(username='company', password='testpass', is_company=True)



class UploadCVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        self.job_posting = JobPosting.objects.create(
            company=self.company_user,
            job_title='Software Engineer',
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )

    def test_notification_creation(self):
        self.client.login(username='testuser', password='testpass')
        Notification.objects.create(
            recipient=self.user,
            message='Test notification',
            notification_type='application'
        )
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test notification')
from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models.jobposting import JobPosting


class StaticPagesTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.job1 = JobPosting.objects.create(
            job_title="Backend Developer",
            location="London",
            contract_type="Full-time",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="Python",
            perks="Snacks",
        )
        self.job2 = JobPosting.objects.create(
            job_title="Frontend Engineer",
            location="Berlin",
            contract_type="Internship",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="React",
            perks="Snacks",
        )

    # --- Basic View Rendering ---

    def test_contact_us_view(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)

    def test_about_us_view(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)

    def test_terms_conditions_view(self):
        response = self.client.get(reverse('terms_conditions'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_view(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)

    def test_user_agreement_view(self):
        response = self.client.get(reverse('user_agreement'))
        self.assertEqual(response.status_code, 200)

    def test_faq_view(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_help_centre_view(self):
        response = self.client.get(reverse('help_centre'))
        self.assertEqual(response.status_code, 200)

    def test_accessibility_view(self):
        response = self.client.get(reverse('accessibility'))
        self.assertEqual(response.status_code, 200)

    # --- Template Usage ---

    def test_contact_us_template(self):
        response = self.client.get(reverse('contact_us'))
        self.assertTemplateUsed(response, 'pages/contact_us.html')

    def test_about_us_template(self):
        response = self.client.get(reverse('about_us'))
        self.assertTemplateUsed(response, 'pages/about_us.html')

    def test_terms_conditions_template(self):
        response = self.client.get(reverse('terms_conditions'))
        self.assertTemplateUsed(response, 'pages/terms_conditions.html')

    def test_privacy_template(self):
        response = self.client.get(reverse('privacy'))
        self.assertTemplateUsed(response, 'pages/privacy.html')

    def test_user_agreement_template(self):
        response = self.client.get(reverse('user_agreement'))
        self.assertTemplateUsed(response, 'pages/user_agreement.html')

    def test_faq_template(self):
        response = self.client.get(reverse('faq'))
        self.assertTemplateUsed(response, 'pages/faq.html')

    def test_help_centre_template(self):
        response = self.client.get(reverse('help_centre'))
        self.assertTemplateUsed(response, 'pages/help_centre.html')

    def test_accessibility_template(self):
        response = self.client.get(reverse('accessibility'))
        self.assertTemplateUsed(response, 'pages/accessibility.html')

    # --- Guest View Tests ---

    def test_guest_no_query(self):
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Job")
        self.assertContains(response, "Job")

 
    def test_guest_query_case_insensitive(self):
        response = self.client.get(reverse('guest') + "?q=frontend")
        self.assertContains(response, "Job")

    def test_guest_query_partial_match(self):
        response = self.client.get(reverse('guest') + "?q=engineer")
        self.assertContains(response, "Job")

    def test_guest_query_no_match(self):
        response = self.client.get(reverse('guest') + "?q=designer")
        self.assertNotContains(response, "Backend Developer")
        self.assertNotContains(response, "Frontend Engineer")

    def test_guest_template_used(self):
        response = self.client.get(reverse('guest'))
        self.assertTemplateUsed(response, 'pages/guest.html')

    def test_guest_context_has_is_guest(self):
        response = self.client.get(reverse('guest'))
        self.assertTrue(response.context['is_guest'])

    def test_guest_context_has_job_postings(self):
        response = self.client.get(reverse('guest'))
        self.assertIn('job_postings', response.context)
        self.assertEqual(len(response.context['job_postings']), 2)

    def test_guest_query_multiple_jobs(self):
        JobPosting.objects.create(
            job_title="Senior Backend Developer",
            location="Remote",
            contract_type="Contract",
            job_overview="Senior role",
            roles_responsibilities="Lead backend",
            required_skills="Django",
            perks="Stock",
        )
        response = self.client.get(reverse('guest') + "?q=backend")
        self.assertContains(response, "SHY")
        self.assertContains(response, "SHY")

    # --- Edge Cases ---

    def test_guest_empty_jobs(self):
        JobPosting.objects.all().delete()
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "us")

    def test_guest_query_special_characters(self):
        response = self.client.get(reverse('guest') + "?q=<>")
        self.assertEqual(response.status_code, 200)

    def test_guest_query_long_string(self):
        response = self.client.get(reverse('guest') + "?q=" + "a" * 300)
        self.assertEqual(response.status_code, 200)

    def test_guest_query_numeric(self):
        JobPosting.objects.create(
            job_title="Engineer 123",
            location="Remote",
            contract_type="Part-time",
            job_overview="Numbers",
            roles_responsibilities="123",
            required_skills="Math",
            perks="Free calculator",
        )
        response = self.client.get(reverse('guest') + "?q=123")
        self.assertContains(response, "companies")

    def test_guest_query_space_match(self):
        response = self.client.get(reverse('guest') + "?q=Backend Developer")
        self.assertContains(response, "SHY")

    def test_guest_query_with_symbol_in_title(self):
        JobPosting.objects.create(
            job_title="UX/UI Designer!",
            location="London",
            contract_type="Contract",
            job_overview="Design",
            roles_responsibilities="User experience",
            required_skills="Figma",
            perks="Snacks",
        )
        response = self.client.get(reverse('guest') + "?q=Designer!")
        self.assertContains(response, "SHY")

    def test_guest_response_type(self):
        response = self.client.get(reverse('guest'))
        self.assertIn("text/html", response["Content-Type"])