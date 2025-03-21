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


# Additional tests for filtering, CSRF-exempt views, and JSON responses can be added similarly.


    def test_login_page_loads(self):
        response = self.client.get(reverse("process_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
    
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



    def test_employer_dashboard_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login



    def test_contact_us(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')

    def test_guest_search(self):
        response = self.client.get(reverse('guest'), {'q': 'Software'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest.html')



    def test_user_dashboard_authenticated_company(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_search(self):
        response = self.client.get(reverse('search'), {
            'q': 'Software',
            'education_required': ['Bachelor'],
            'job_type': ['Full-time'],
            'industry': ['technology'],
            'location_filter': ['New York'],
            'benefits': ['Health insurance'],
            'work_flexibility': ['Remote'],
            'salary_range': '50000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')

    def test_about_us(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')

    def test_my_jobs(self):
        response = self.client.get(reverse('my_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_jobs.html')



   


    def test_start_application(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step1

    def test_apply_step1(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step1'), {
            'application_type': 'Online',
            'cover_letter': 'I am a great fit for this job.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step2

    def test_apply_step2(self):
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

    def test_apply_step3(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step3'), {
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I have relevant experience.',
            'salary_expectations': '80000',
            'background_check': 'Yes'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step4

    def test_apply_step4(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step4'))
        self.assertEqual(response.status_code, 302)  # Redirect to application_success

   

    def test_notifications(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 302)
   



    def test_job_postings_api(self):
        response = self.client.get(reverse('job_postings_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 1)

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



    # Test 3: Test guest view with no matching results
    def test_guest_view_no_results(self):
        response = self.client.get(reverse('guest'), {'q': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest.html')
        self.assertNotContains(response, 'Software Engineer')

    # Test 4: Test user dashboard for authenticated user
    def test_user_dashboard_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

    # Test 5: Test user dashboard for unauthenticated user
    def test_user_dashboard_unauthenticated(self):
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    # Test 6: Test employer dashboard for authenticated company
    def test_employer_dashboard_authenticated_company(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employer_dashboard.html')



    # Test 8: Test employer dashboard for unauthenticated user
    def test_employer_dashboard_unauthenticated(self):
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    # Test 9: Test contact us page
    def test_contact_us(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')

    # Test 10: Test about us page
    def test_about_us(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')

    # Test 11: Test my jobs page for authenticated user
    def test_my_jobs_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_jobs.html')



    # Test 18: Test leave review for authenticated user
    def test_leave_review_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('leave_review', args=[self.company.id]), {
            'text': 'Great company!',
            'rating': '5'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)

 

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

    # Test 23: Test create job posting for unauthenticated user
    def test_create_job_posting_unauthenticated(self):
        data = {
            'job_title': 'Software Engineer',
            'location': 'New York',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software',
            'roles_responsibilities': 'Write code',
            'required_skills': 'Python, Django',
            'education_required': 'Bachelor\'s Degree',
            'application_deadline': '2023-12-31'
        }
        response = self.client.post(reverse('create_job_posting'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code,302)  # Forbidden

    # Test 24: Test start application for authenticated user
    def test_start_application_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step1

    # Test 25: Test start application for unauthenticated user
    def test_start_application_unauthenticated(self):
        response = self.client.get(reverse('start_application', args=[self.job_posting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    # Test 26: Test apply_step1 for authenticated user
    def test_apply_step1_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step1'), {
            'application_type': 'Online',
            'cover_letter': 'I am a great fit for this job.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step2

    # Test 27: Test apply_step1 for unauthenticated user
    def test_apply_step1_unauthenticated(self):
        response = self.client.post(reverse('apply_step1'), {
            'application_type': 'Online',
            'cover_letter': 'I am a great fit for this job.'
        })
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

    # Test 30: Test apply_step3 for authenticated user
    def test_apply_step3_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('apply_step3'), {
            'eligible_to_work': 'Yes',
            'previously_employed': 'No',
            'require_sponsorship': 'No',
            'how_did_you_hear': 'Friend',
            'why_good_fit': 'I have relevant experience.',
            'salary_expectations': '80000',
            'background_check': 'Yes'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to apply_step4

    def test_employer_dashboard_non_company_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('employer_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_contact_us(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_us.html')

    def test_guest(self):
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest.html')

    def test_guest_search(self):
        response = self.client.get(reverse('guest'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest.html')

    def test_user_dashboard_normal_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

    def test_user_dashboard_company_user(self):
        self.client.force_login(self.company)
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_search(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')

    def test_search_query(self):
        response = self.client.get(reverse('search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)

    def test_about_us(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')

    def test_my_jobs(self):
        response = self.client.get(reverse('my_jobs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_jobs.html')


    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


   
   
    
  
    
    
   
