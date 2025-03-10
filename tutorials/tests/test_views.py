from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models.jobposting import JobPosting
from tutorials.models.company_review import Review
import json
from datetime import datetime
from tutorials.views.ui_views import signup_view, login_view, employer_dashboard, user_dashboard, search, contact_us, about_us, company_detail, leave_review, edit_company, profile_settings, create_job_posting, apply_step1, apply_step2, apply_step3, apply_step4, application_success


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

    def test_employer_dashboard_access(self):
        self.client.login(username='companyuser', password='testpass')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_employer_dashboard_restricted_for_normal_users(self):
        self.client.login(username='normaluser', password='testpass')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_contact_us_page(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)

    def test_guest_page_no_query(self):
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)

  

    def test_user_dashboard_access(self):
        self.client.login(username='normaluser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_user_dashboard_restricted_for_companies(self):
        self.client.login(username='companyuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_search_no_query(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get(reverse('search') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_about_us_page(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)

    

    def test_company_detail_page(self):
        response = self.client.get(reverse('company_detail', args=[self.company_user.id]))
        self.assertEqual(response.status_code, 200)

    def test_leave_review_post(self):
        response = self.client.post(reverse('leave_review', args=[self.company_user.id]), {'text': 'Great company', 'rating': 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)

    def test_edit_company_post(self):
        self.client.login(username='companyuser', password='testpass')
        response = self.client.post(reverse('edit_company', args=[self.company_user.id]), {'description': 'Updated description'})
        self.assertEqual(response.status_code, 200)
        self.company_user.refresh_from_db()
        self.assertEqual(self.company_user.description, 'Updated description')

    
    def test_apply_step1(self):
        response = self.client.get(reverse('apply_step1'))
        self.assertEqual(response.status_code, 200)
    
    def test_apply_step2(self):
        response = self.client.get(reverse('apply_step2'))
        self.assertEqual(response.status_code, 200)
    
    def test_apply_step3(self):
        response = self.client.get(reverse('apply_step3'))
        self.assertEqual(response.status_code, 200)
    
    def test_apply_step4(self):
        response = self.client.get(reverse('apply_step4'))
        self.assertEqual(response.status_code, 200)

    def test_application_success(self):
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)

   

    def test_company_detail_404(self):
        response = self.client.get(reverse('company_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

   

# Additional tests for filtering, CSRF-exempt views, and JSON responses can be added similarly.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.forms import UserLoginForm, CompanyLoginForm, CompanySignUpForm, UserSignUpForm

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_password = "testpassword123"
        self.company_password = "companypassword123"
        
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password=self.user_password, is_company=False
        )
        
        self.company = User.objects.create_user(
            username="testcompany", email="testcompany@example.com", password=self.company_password, is_company=True
        )
    
    # --- LOGIN TESTS ---
    
    def test_login_page_loads(self):
        response = self.client.get(reverse("process_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
    
   
  
   
    
    
    # --- SIGNUP TESTS ---
    
  
    
    
   