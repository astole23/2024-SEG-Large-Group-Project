from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models.jobposting import JobPosting
from tutorials.models.company_review import Review
import json
from datetime import datetime

CustomUser = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.company_user = CustomUser.objects.create_user(username='companyuser', password='testpass', is_company=True)
        self.normal_user = CustomUser.objects.create_user(username='normaluser', password='testpass', is_company=False)
        self.job_posting = JobPosting.objects.create(
            job_title='Test Job',
            company_name='Test Company',
            location='New York',
            contract_type='Full-time',
            job_overview='A test job overview.',
            roles_responsibilities='Test roles.',
            required_skills='Python, Django',
            education_required='Bachelor’s Degree',
            perks='Remote work',
            application_deadline=datetime.today().date()
        )



# Additional tests for filtering, CSRF-exempt views, and JSON responses can be added similarly.


    
        self.company = CustomUser.objects.create_user(
            username='testcompany', 
            password='testpass123', 
            is_company=True,
            company_name='Test Company'
        )
        self.job_posting = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            contract_type='Full-time',
            job_overview='Develop software',
            roles_responsibilities='Write code',
            required_skills='Python, Django',
            application_deadline='2023-12-31'
        )

 



    # Add more tests as needed to cover all views and scenarios

    from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import JobPosting, Review, JobApplication, Notification
import json
from datetime import datetime, timedelta

CustomUser = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            password='testpass123', 
            is_company=False
        )
        self.company = CustomUser.objects.create_user(
            username='testcompany', 
            password='testpass123', 
            is_company=True,
            company_name='Test Company'
        )
        self.job_posting = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            contract_type='Full-time',
            job_overview='Develop software',
            roles_responsibilities='Write code',
            required_skills='Python, Django',
            education_required='Bachelor\'s Degree',
            application_deadline='2023-12-31'
        )



    # Test 5: Test user dashboard for unauthenticated user
    def test_user_dashboard_unauthenticated(self):
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login



    # Test 8: Test employer dashboard for unauthenticated user
    def test_employer_dashboard_unauthenticated(self):
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

 

    # Test 18: Test leave review for authenticated user
    def test_leave_review_unauthenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('leave_review', args=[self.company.id]), {
            'text': 'Great company!',
            'rating': '5'
        })
        self.assertEqual(response.status_code, 302)

 

    # Test 22: Test create job posting with invalid data
    def test_create_job_posting_invalid_data(self):
        self.client.login(username='testcompany', password='testpass123')
        data = {
            'job_title': '',  # Invalid: Empty field
            'location': 'New York',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software',
            'roles_responsibilities': 'Write code',
            'required_skills': 'Python, Django',
            'education_required': 'Bachelor\'s Degree',
            'application_deadline': '2023-12-31'
        }
        response = self.client.post(reverse('create_job_posting'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad request


    # Test 24: Test start application for authenticated user
    def test_start_application_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step1

    # Test 25: Test start application for unauthenticated user
    def test_start_application_unauthenticated(self):
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login





    # Test 28: Test apply_step2 for authenticated user
    def test_apply_step2_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step2'), {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'country': 'USA',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step3

    # Test 29: Test apply_step2 for unauthenticated user
    def test_apply_step2_unauthenticated(self):
        response = self.client.post(reverse('apply_step2'), {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'preferred_name': 'Johnny',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'country': 'USA',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postcode': '10001'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login



    def test_user_dashboard_company_user(self):
        self.client.force_login(self.company)
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)





   
   
    
  
    
    
   
