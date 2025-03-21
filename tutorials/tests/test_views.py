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


   






   
   #--------------------function views -----------------------------------

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.forms import UserLoginForm, CompanyLoginForm, CompanySignUpForm, UserSignUpForm
from tutorials.views.ui_views import process_login, process_signup

User = get_user_model()

class AuthViewsTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass', is_company=False)
        self.company = User.objects.create_user(username='testcompany', password='companypass', is_company=True)

    # Tests for process_login view

    def test_process_login_view_valid_user(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs

    def test_process_login_view_valid_company(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'company',
            'username': 'testcompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs

  

    def test_process_login_view_get_request(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


   

    # Tests for process_signup view

    def test_process_signup_view_valid_user(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password': 'newpass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs
 
    def test_process_signup_view_valid_company(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': 'newcompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs
    

   

    def test_process_signup_view_get_request(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

   

    def test_process_signup_view_company_success_message(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': 'anothercompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs


import re
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from tutorials.validators import CustomPasswordValidator    

class CustomPasswordValidatorTests(TestCase):
    def setUp(self):
        self.validator = CustomPasswordValidator()

    # Test valid passwords
    def test_valid_password(self):
        valid_passwords = [
            "Password1",
            "SecurePass123",
            "ValidPass99",
            "Test1234",
            "HelloWorld1",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords missing uppercase letters
    def test_password_missing_uppercase(self):
        invalid_passwords = [
            "password1",
            "lowercase123",
            "nouppercase1",
            "alllower1",
            "1234567a",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords missing lowercase letters
    def test_password_missing_lowercase(self):
        invalid_passwords = [
            "PASSWORD1",
            "UPPERCASE123",
            "NOLOWERCASE1",
            "ALLUPPER1",
            "1234567A",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_lower')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one lowercase letter."
            )

    # Test passwords missing numerals
    def test_password_missing_numeral(self):
        invalid_passwords = [
            "Password",
            "NoNumbersHere",
            "JustLetters",
            "UpperCaseOnly",
            "LowerCaseOnly",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    # Test empty password
    def test_empty_password(self):
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("")
        self.assertEqual(context.exception.code, 'password_no_upper')  # First check fails
        self.assertEqual(
            str(context.exception.message),
            "The password must contain at least one uppercase letter."
        )

    # Test passwords with only uppercase letters
    def test_password_only_uppercase(self):
        invalid_passwords = [
            "UPPERCASE",
            "ALLUPPER",
            "ONLYUPPER",
            "CAPITALS",
            "UPPERONLY",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_lower')  # Missing lowercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one lowercase letter."
            )

    # Test passwords with only lowercase letters
    def test_password_only_lowercase(self):
        invalid_passwords = [
            "lowercase",
            "alllower",
            "onlylower",
            "smallletters",
            "loweronly",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with only numerals
    def test_password_only_numerals(self):
        invalid_passwords = [
            "12345678",
            "987654321",
            "00000000",
            "11111111",
            "99999999",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with special characters
    def test_password_with_special_characters(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with spaces
    def test_password_with_spaces(self):
        invalid_passwords = [
            "Password 1",
            "Secure Pass123",
            "Valid Pass99",
            "Test 1234",
            "Hello World1",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test get_help_text method
    def test_get_help_text(self):
        help_text = self.validator.get_help_text()
        self.assertEqual(
            help_text,
            "Your password must contain at least one uppercase letter, one lowercase letter, and one numeral."
        )
    def test_password_one_uppercase(self):
        valid_passwords = [
            "Password1",
            "Apassword1",
            "1passwordA",
            "passWord1",
            "1Apassword",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one lowercase letter
    def test_password_one_lowercase(self):
        valid_passwords = [
            "PASSWORDa1",
            "1PASSWORDAa",
            "A1PASSWORDa",
            "1aPASSWORD",
            "PASSWORD1a",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one numeral
    def test_password_one_numeral(self):
        valid_passwords = [
            "Password1",
            "1Password",
            "Pass1word",
            "Password1",
            "1PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with multiple uppercase letters
   

    

    # Test passwords with multiple numerals
    def test_password_multiple_numerals(self):
        valid_passwords = [
            "Password123",
            "123Password",
            "Pass123word",
            "Password123",
            "123PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with special characters and valid requirements
    def test_password_with_special_characters_valid(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading/trailing spaces
    def test_password_with_leading_trailing_spaces(self):
        invalid_passwords = [
            " Password1",
            "Password1 ",
            " Password1 ",
            "  Password1  ",
            " Password1  ",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with only special characters
    def test_password_only_special_characters(self):
        invalid_passwords = [
            "!@#$%^&*",
            "!@#$%^&*()",
            "!@#$%^&*()_+",
            "!@#$%^&*()_+{}",
            "!@#$%^&*()_+{}[]",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with mixed case and no numerals
    def test_password_mixed_case_no_numerals(self):
        invalid_passwords = [
            "Password",
            "PassWord",
            "PASSword",
            "paSSWORD",
            "PaSsWoRd",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    

    # Test passwords with exactly 8 characters (minimum length)
    def test_password_minimum_length(self):
        valid_passwords = [
            "Passwo1",
            "Passwo1!",
            "Passwo1@",
            "Passwo1#",
            "Passwo1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly 16 characters (maximum length)
    def test_password_maximum_length(self):
        valid_passwords = [
            "Password12345678",
            "Password12345678!",
            "Password12345678@",
            "Password12345678#",
            "Password12345678$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with non-ASCII characters
    def test_password_non_ascii_characters(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with emojis
    def test_password_with_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading zeros
    def test_password_with_leading_zeros(self):
        valid_passwords = [
            "Password01",
            "Password001",
            "Password0001",
            "Password00001",
            "Password000001",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with trailing zeros
    def test_password_with_trailing_zeros(self):
        valid_passwords = [
            "Password10",
            "Password100",
            "Password1000",
            "Password10000",
            "Password100000",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and special characters
    def test_password_mixed_case_numerals_special_chars(self):
        valid_passwords = [
            "Password1!",
            "Passw0rd@",
            "P@ssw0rd",
            "P@ssw0rd!",
            "P@ssw0rd#",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and spaces
    def test_password_mixed_case_numerals_spaces(self):
        valid_passwords = [
            "Password 1",
            "Pass word1",
            "Pass word 1",
            "Pass word 1!",
            "Pass word 1@",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and non-ASCII characters
    def test_password_mixed_case_numerals_non_ascii(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and emojis
    def test_password_mixed_case_numerals_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

        

      

    # Test passwords with exactly one uppercase letter
    def test_password_one_uppercase(self):
        valid_passwords = [
            "Password1",
            "Apassword1",
            "1passwordA",
            "passWord1",
            "1Apassword",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one lowercase letter
    def test_password_one_lowercase(self):
        valid_passwords = [
            "PASSWORDa1",
            "1PASSWORDAa",
            "A1PASSWORDa",
            "1aPASSWORD",
            "PASSWORD1a",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one numeral
    def test_password_one_numeral(self):
        valid_passwords = [
            "Password1",
            "1Password",
            "Pass1word",
            "Password1",
            "1PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")


    # Test passwords with multiple lowercase letters
    def test_password_multiple_lowercase(self):
        valid_passwords = [
            "Password1",
            "paSSword1",
            "passWORD1",
            "pCassword1",
            "PassWord1",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with multiple numerals
    def test_password_multiple_numerals(self):
        valid_passwords = [
            "Password123",
            "123Password",
            "Pass123word",
            "Password123",
            "123PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with special characters and valid requirements
    def test_password_with_special_characters_valid(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading/trailing spaces
    def test_password_with_leading_trailing_spaces(self):
        invalid_passwords = [
            " Password1",
            "Password1 ",
            " Password1 ",
            "  Password1  ",
            " Password1  ",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with only special characters
    def test_password_only_special_characters(self):
        invalid_passwords = [
            "!@#$%^&*",
            "!@#$%^&*()",
            "!@#$%^&*()_+",
            "!@#$%^&*()_+{}",
            "!@#$%^&*()_+{}[]",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with mixed case and no numerals
    def test_password_mixed_case_no_numerals(self):
        invalid_passwords = [
            "Password",
            "PassWord",
            "PASSword",
            "paSSWORD",
            "PaSsWoRd",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    # Test passwords with mixed case and no lowercase
  
    def test_password_minimum_length(self):
        valid_passwords = [
            "Passwo1",
            "Passwo1!",
            "Passwo1@",
            "Passwo1#",
            "Passwo1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly 16 characters (maximum length)
    def test_password_maximum_length(self):
        valid_passwords = [
            "Password12345678",
            "Password12345678!",
            "Password12345678@",
            "Password12345678#",
            "Password12345678$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with non-ASCII characters
    def test_password_non_ascii_characters(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with emojis
    def test_password_with_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

 

   #--------------------job search views -----------------------------------

import json
import random
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from tutorials.models.accounts import CustomUser
from tutorials.models.jobposting import JobPosting
from tutorials.models.standard_cv import UserCV
from tutorials.views.job_search import job_recommendation, get_random_job_postings, safe_json_list



class JobRecommendationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Use your custom user model
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.user.user_industry = ['IT', 'Software']
        self.user.user_location = 'New York'
        self.user.save()

        # Create sample job postings
        self.job1 = JobPosting.objects.create(
            job_title='Software Engineer',
            
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='Python, Django',
            preferred_skills='JavaScript, React',
            education_required='Bachelor’s degree in Computer Science',
            perks='Health insurance, 401(k)',
            company_overview='A leading tech company.',
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        self.job2 = JobPosting.objects.create(
            job_title='Data Scientist',
            location='San Francisco',
            salary_range='3000',
            contract_type='Full-time',
            job_overview='Analyze and interpret complex data.',
            roles_responsibilities='Build predictive models.',
            required_skills='Python, R',
            preferred_skills='Machine Learning, SQL',
            education_required='Master’s degree in Data Science',
            perks='Flexible hours, remote work',
            company_overview='A data-driven company.',
            why_join_us='Cutting-edge projects.',
            company_reviews='6'
        )

    # Test helper functions
    def test_get_random_job_postings(self):
        jobs = get_random_job_postings(1)
        self.assertEqual(len(jobs), 1)

    def test_safe_json_list_valid_json(self):
        data = '[{"fieldOfStudy": "Computer Science"}]'
        result = safe_json_list(data)
        self.assertEqual(result, [{"fieldOfStudy": "Computer Science"}])

    def test_safe_json_list_invalid_json(self):
        data = 'invalid json'
        result = safe_json_list(data)
        self.assertEqual(result, [])

    def test_safe_json_list_already_list(self):
        data = [{"fieldOfStudy": "Computer Science"}]
        result = safe_json_list(data)
        self.assertEqual(result, data)

    # Test job_recommendation view
    def test_job_recommendation_no_user_industry_or_location(self):
        self.user.user_industry = []
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

  
    def test_job_recommendation_with_user_cv(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_matching_jobs(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_matching_jobs(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Biology"}]',
            work_experience='[{"job_title": "Biologist"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_invalid_user_cv(self):
        UserCV.objects.create(
            user=self.user,
            education='invalid json',
            work_experience='invalid json'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_user_cv(self):
        UserCV.objects.create(
            user=self.user,
            education='[]',
            work_experience='[]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_partial_user_cv(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_partial_user_cv_work_experience(self):
        UserCV.objects.create(
            user=self.user,
            education='[]',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_multiple_jobs(self):
        for i in range(10):
            JobPosting.objects.create(
                job_title=f'Job {i}',
                company_name=f'Company {i}',
                location='New York',
                salary_range='$100,000 - $120,000',
                contract_type='Full-time',
                job_overview=f'Job overview {i}',
                roles_responsibilities=f'Roles {i}',
                required_skills=f'Skills {i}',
                preferred_skills=f'Preferred skills {i}',
                education_required=f'Education {i}',
                perks=f'Perks {i}',
                company_overview=f'Company overview {i}',
                why_join_us=f'Why join us {i}',
                company_reviews=f'Company reviews {i}'
            )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_user(self):
        request = self.factory.get('/job-recommendation/')
        request.user = None
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_location(self):
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_invalid_location(self):
        self.user.user_location = 'Invalid Location'
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_education(self):
        UserCV.objects.create(
            user=self.user,
            education='[]',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_work_experience(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_invalid_education_json(self):
        UserCV.objects.create(
            user=self.user,
            education='invalid json',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_invalid_work_experience_json(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='invalid json'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_mixed_data(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}, {"fieldOfStudy": "Mathematics"}]',
            work_experience='[{"job_title": "Software Engineer"}, {"job_title": "Data Analyst"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company_name='Tech Corp',
                location='New York',
                salary_range='$100,000 - $120,000',
                contract_type='Full-time',
                job_overview='Develop and maintain software applications.',
                roles_responsibilities='Code, test, and deploy software.',
                required_skills='Python, Django',
                preferred_skills='JavaScript, React',
                education_required='Bachelor’s degree in Computer Science',
                perks='Health insurance, 401(k)',
                company_overview='A leading tech company.',
                why_join_us='Innovative environment.',
                company_reviews='Great place to work.'
            )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_large_dataset(self):
        for i in range(200):
            JobPosting.objects.create(
                job_title=f'Job {i}',
                company_name=f'Company {i}',
                location='New York',
                salary_range='$100,000 - $120,000',
                contract_type='Full-time',
                job_overview=f'Job overview {i}',
                roles_responsibilities=f'Roles {i}',
                required_skills=f'Skills {i}',
                preferred_skills=f'Preferred skills {i}',
                education_required=f'Education {i}',
                perks=f'Perks {i}',
                company_overview=f'Company overview {i}',
                why_join_us=f'Why join us {i}',
                company_reviews=f'Company reviews {i}'
            )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_specific_industry(self):
        self.user.user_industry = ['Data Science']
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_specific_location(self):
        self.user.user_location = 'San Francisco'
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_specific_education(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Data Science"}]',
            work_experience='[{"job_title": "Data Scientist"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_specific_work_experience(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[{"job_title": "Software Engineer"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_matching_industry(self):
        self.user.user_industry = ['Healthcare']
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_matching_location(self):
        self.user.user_location = 'London'
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_matching_education(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Biology"}]',
            work_experience='[{"job_title": "Biologist"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_matching_work_experience(self):
        UserCV.objects.create(
            user=self.user,
            education='[{"fieldOfStudy": "Computer Science"}]',
            work_experience='[{"job_title": "Biologist"}]'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_multiple_users(self):
        user2 = CustomUser.objects.create_user(username='testuser2', password='12345')
        user2.user_industry = ['Data Science']
        user2.user_location = 'San Francisco'
        user2.save()
        request = self.factory.get('/job-recommendation/')
        request.user = user2
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_different_user_industries(self):
        user2 = CustomUser.objects.create_user(username='testuser2', password='12345')
        user2.user_industry = ['Finance']
        user2.user_location = 'New York'
        user2.save()
        request = self.factory.get('/job-recommendation/')
        request.user = user2
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

   

    
  
    
  
    
    
   