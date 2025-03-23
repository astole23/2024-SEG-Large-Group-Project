from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from tutorials.models.jobposting import JobPosting
from tutorials.models.applications import JobApplication, Notification
from tutorials.models.standard_cv import UserCV

# Use the custom user model
CustomUser = get_user_model()

class ApplicationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a regular user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            is_company=False
        )
        # Create a company user
        self.company = CustomUser.objects.create_user(
            username='testcompany',
            password='testpass123',
            is_company=True
        )
        # Create a job posting
        self.job_posting = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            contract_type='Full-time',
            job_overview='Develop software applications.',
            roles_responsibilities='Write code and debug.',
            required_skills='Python, Django',
            perks='Health insurance',
            application_deadline='2023-12-31'
        )
        # Create a CV for the user
        self.cv = UserCV.objects.create(
            user=self.user,
            personal_info={
                'title': 'Mr',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '1234567890',
                'country': 'USA',
                'address_line1': '123 Main St',
                'city': 'New York',
                'postcode': '10001'
            },
            key_skills='Python, Django',
            education=[{'university': 'University A', 'degreeType': 'Bachelor', 'dates': '2015-2019'}],
            work_experience=[{'employer_name': 'Company A', 'job_title': 'Developer', 'dates': '2020-2022'}]
        )

    # ====================
    # Tests for start_application
    # ====================

    def test_start_application_with_valid_job_posting_id(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertRedirects(response, reverse('apply_step1'))
        self.assertEqual(self.client.session.get('job_posting_id'), self.job_posting.id)

    def test_start_application_with_invalid_job_posting_id(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('start_application', args=[999]))  # Non-existent job posting ID
        self.assertEqual(response.status_code, 302)

    def test_start_application_with_unauthenticated_user(self):
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('start_application', args=[self.job_posting.id])}")

    # ====================
    # Tests for apply_step1
    # ====================

    def test_apply_step1_with_valid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step1'), {
            'application_type': 'cv',
            'cover_letter': 'This is a cover letter.'
        })
        self.assertRedirects(response, reverse('apply_step2'))
        self.assertEqual(self.client.session['application_data']['application_type'], 'cv')
        self.assertEqual(self.client.session['application_data']['cover_letter'], 'This is a cover letter.')

    def test_apply_step1_with_invalid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step1'), {})  # Missing required fields
        self.assertEqual(response.status_code, 302)

    def test_apply_step1_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('apply_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 1")

    # ====================
    # Tests for apply_step2
    # ====================

    def test_apply_step2_with_valid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.post(reverse('apply_step2'), {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'John',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'country': 'USA',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skill': ['Python', 'Django'],
            'institution': ['University A'],
            'degree': ['Bachelor'],
            'edu_start': ['2015'],
            'edu_end': ['2019'],
            'company_name': ['Company A'],
            'position': ['Developer'],
            'work_start': ['2020'],
            'work_end': ['2022']
        })
        self.assertRedirects(response, reverse('apply_step3'))
        application_data = self.client.session['application_data']
        self.assertEqual(application_data['first_name'], 'John')
        self.assertEqual(application_data['skills'], ['Python', 'Django'])

    def test_apply_step2_with_invalid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.post(reverse('apply_step2'), {})  # Missing required fields
        self.assertEqual(response.status_code, 302)

    def test_apply_step2_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.get(reverse('apply_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 2")

    # ====================
    # Tests for apply_step3
    # ====================

    def test_apply_step3_with_valid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.post(reverse('apply_step3'), {
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I am a great fit.',
            'salary_expectations': '50000',
            'background_check': 'Yes'
        })
        self.assertRedirects(response, reverse('apply_step4'))
        application_data = self.client.session['application_data']
        self.assertEqual(application_data['eligible_to_work'], 'Yes')
        self.assertEqual(application_data['salary_expectations'], '50000')

    def test_apply_step3_with_invalid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.post(reverse('apply_step3'), {})  # Missing required fields
        self.assertEqual(response.status_code, 302)

    def test_apply_step3_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.get(reverse('apply_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 3")

    # ====================
    # Tests for apply_step4
    # ====================

    def test_apply_step4_with_invalid_post_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skills': ['Python', 'Django'],
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I am a great fit.',
            'salary_expectations': '50000',
            'background_check': 'Yes'
        }
        self.client.session['job_posting_id'] = self.job_posting.id
        response = self.client.post(reverse('apply_step4'))
        self.assertEqual(response.status_code, 302)

    def test_apply_step4_with_missing_job_posting_id(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.post(reverse('apply_step4'))
        self.assertRedirects(response, reverse('guest'))
        self.assertIn("Job posting not specified.", [m.message for m in messages.get_messages(response.wsgi_request)])

    def test_apply_step4_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.get(reverse('apply_step4'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 4")

    # ====================
    # Tests for application_success
    # ====================

    def test_application_success_with_valid_application_id(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_id'] = '12345'
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)

    def test_application_success_with_missing_application_id(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "12345")

    # ====================
    # Tests for add_job_by_code
    # ====================

    def test_add_job_by_code_with_valid_code(self):
        job_application = JobApplication.objects.create(
            applicant=self.user,
            job_posting=self.job_posting,
            company=self.company,
            application_id='12345'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '12345'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})
        self.assertTrue(JobApplication.objects.get(application_id='12345').tracked)

    def test_add_job_by_code_with_invalid_code(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': 'invalid'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'success': False, 'error': 'Job application not found.'})

    def test_add_job_by_code_with_unauthorized_user(self):
        job_application = JobApplication.objects.create(
            applicant=self.company,  # Different user
            job_posting=self.job_posting,
            company=self.company,
            application_id='12345'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '12345'}), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'success': False, 'error': 'This job application does not belong to you.'})

    # ====================
    # Additional Edge Cases
    # ====================

    def test_apply_step2_with_cv_data_preload(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.get(reverse('apply_step2'))
        self.assertEqual(response.status_code, 200)

    def test_apply_step4_with_missing_application_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['job_posting_id'] = self.job_posting.id
        response = self.client.post(reverse('apply_step4'))
        self.assertRedirects(response, reverse('guest'))
        self.assertIn("Job posting not specified.", [m.message for m in messages.get_messages(response.wsgi_request)])

    def test_add_job_by_code_with_empty_code(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': ''}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'success': False, 'error': 'No code provided.'})

    def test_add_job_by_code_with_invalid_json(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), 'invalid_json', content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'success': False, 'error': 'Expecting value: line 1 column 1 (char 0)'})

    def test_apply_step2_with_empty_education_and_work_experience(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.post(reverse('apply_step2'), {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'country': 'USA',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skill': ['Python', 'Django'],
            'institution': [''],
            'degree': [''],
            'edu_start': [''],
            'edu_end': [''],
            'company_name': [''],
            'position': [''],
            'work_start': [''],
            'work_end': ['']
        })
        self.assertRedirects(response, reverse('apply_step3'))
        application_data = self.client.session['application_data']
        self.assertEqual(application_data['education_list'], [])
        self.assertEqual(application_data['work_experience_list'], [])

    def test_apply_step4_with_invalid_job_posting_id(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skills': ['Python', 'Django'],
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I am a great fit.',
            'salary_expectations': '50000',
            'background_check': 'Yes'
        }
        self.client.session['job_posting_id'] = 999  # Invalid job posting ID
        response = self.client.post(reverse('apply_step4'))
        self.assertEqual(response.status_code, 302)

    def test_apply_step4_with_missing_session_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step4'))
        self.assertRedirects(response, reverse('guest'))
        self.assertIn("Job posting not specified.", [m.message for m in messages.get_messages(response.wsgi_request)])

    def test_application_success_with_cleared_session(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_id'] = '12345'
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('application_id', self.client.session)  # Session cleared



    def test_apply_step2_with_missing_application_type(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}  # Missing application type
        response = self.client.get(reverse('apply_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 2")
    def test_apply_step3_with_missing_application_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}  # Missing application data
        response = self.client.get(reverse('apply_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 3")
    def test_add_job_by_code_with_invalid_json_in_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), 'invalid_json', content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'success': False, 'error': 'Expecting value: line 1 column 1 (char 0)'})

    def test_add_job_by_code_with_missing_code_in_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'success': False, 'error': 'No code provided.'})

    def test_application_success_with_missing_application_id_in_session(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "12345")

    def test_add_job_by_code_with_unauthenticated_user(self):
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '12345'}), content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_apply_step2_with_missing_cv_data(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        UserCV.objects.filter(user=self.user).delete()  # Delete CV data
        response = self.client.get(reverse('apply_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 2")
                    

    def test_apply_step2_with_empty_education_and_work_experience(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {'application_type': 'cv'}
        response = self.client.post(reverse('apply_step2'), {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'country': 'USA',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skill': ['Python', 'Django'],
            'institution': [''],
            'degree': [''],
            'edu_start': [''],
            'edu_end': [''],
            'company_name': [''],
            'position': [''],
            'work_start': [''],
            'work_end': ['']
        })
        self.assertRedirects(response, reverse('apply_step3'))
        application_data = self.client.session['application_data']
        self.assertEqual(application_data['education_list'], [])
        self.assertEqual(application_data['work_experience_list'], [])

    def test_apply_step3_with_missing_required_fields(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.post(reverse('apply_step3'), {
            'eligible_to_work': '',  # Missing required field
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I am a great fit.',
            'salary_expectations': '50000',
            'background_check': 'Yes'
        })
        self.assertEqual(response.status_code, 302)

    def test_apply_step4_with_missing_job_posting_id_in_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {}
        response = self.client.get(reverse('apply_step4'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 4")

    def test_application_success_with_cleared_session(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_id'] = '12345'
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('application_id', self.client.session)  # Session cleared


    
    def test_apply_step4_with_invalid_job_posting_id_in_post_request(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.session['application_data'] = {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001',
            'skills': ['Python', 'Django'],
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I am a great fit.',
            'salary_expectations': '50000',
            'background_check': 'Yes'
        }
        self.client.session['job_posting_id'] = 999  # Invalid job posting ID
        response = self.client.post(reverse('apply_step4'))
        self.assertEqual(response.status_code, 302)

    def test_add_job_by_code_with_missing_code_in_json(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'success': False, 'error': 'No code provided.'})

    def test_apply_step1_with_invalid_application_type(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step1'), {
            'application_type': 'invalid',  # Invalid application type
            'cover_letter': 'This is a cover letter.'
        })
        self.assertEqual(response.status_code, 302)
                                                    