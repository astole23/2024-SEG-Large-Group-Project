from django.test import TestCase
from django.contrib.auth import get_user_model

from tutorials.forms import (
    CompanyProfileForm, ReviewForm, CompanyEditForm, JobPostingForm,
    UserLoginForm, CompanyLoginForm, UserSignUpForm, CompanySignUpForm
)
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='password123'
        )

    # --- CompanyProfileForm Tests ---
    def test_company_profile_form_valid(self):
        form = CompanyProfileForm(data={
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'company@example.com',
            'phone': '1234567890',
            'location': 'New York',
            'description': 'A tech company'
        })
        self.assertTrue(form.is_valid())

    def test_company_profile_form_missing_fields(self):
        form = CompanyProfileForm(data={})
        self.assertFalse(form.is_valid())
    
    def test_company_profile_form_invalid_email(self):
        form = CompanyProfileForm(data={
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'invalid-email',
            'phone': '1234567890',
            'location': 'New York',
            'description': 'A tech company'
        })
        self.assertFalse(form.is_valid())
    
    def test_company_profile_form_missing_company_name(self):
        form = CompanyProfileForm(data={
            'industry': 'Tech',
            'email': 'company@example.com',
            'phone': '1234567890',
            'location': 'New York',
            'description': 'A tech company'
        })
        self.assertFalse(form.is_valid())

    # --- ReviewForm Tests ---
    def test_review_form_valid(self):
        form = ReviewForm(data={'text': 'Great company!', 'rating': 5})
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form = ReviewForm(data={'text': 'Bad company', 'rating': 10})
        self.assertFalse(form.is_valid())
    
    def test_review_form_no_text(self):
        form = ReviewForm(data={'rating': 3})
        self.assertFalse(form.is_valid())
    
    def test_review_form_invalid_negative_rating(self):
        form = ReviewForm(data={'text': 'Terrible company', 'rating': -1})
        self.assertFalse(form.is_valid())

    # --- CompanyEditForm Tests ---
    def test_company_edit_form_valid(self):
        form = CompanyEditForm(data={'description': 'Updated description'})
        self.assertTrue(form.is_valid())

   
    
    def test_company_edit_form_empty(self):
        form = CompanyEditForm(data={})
        self.assertTrue(form.is_valid())

    # --- JobPostingForm Tests ---
    def test_job_posting_form_valid(self):
        form = JobPostingForm(data={
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '50k-70k',
            'job_overview': 'Develop software',
            'roles_responsibilities': 'Coding, Testing',
            'education_required': 'Bachelor’s degree',
            'application_deadline': '2025-12-31'
        })
        self.assertTrue(form.is_valid())

    def test_job_posting_form_missing_fields(self):
        form = JobPostingForm(data={})
        self.assertFalse(form.is_valid())
    
    def test_job_posting_form_invalid_date(self):
        form = JobPostingForm(data={
            'job_title': 'Software Engineer',
            'application_deadline': 'invalid-date'
        })
        self.assertFalse(form.is_valid())

    # --- UserLoginForm Tests ---
    def test_user_login_form_valid(self):
        form = UserLoginForm(data={'username': 'testuser', 'password': 'password123'})
        self.assertTrue(form.is_valid())

    def test_user_login_form_invalid(self):
        form = UserLoginForm(data={'username': '', 'password': ''})
        self.assertFalse(form.is_valid())
    
    def test_user_login_form_missing_password(self):
        form = UserLoginForm(data={'username': 'testuser'})
        self.assertFalse(form.is_valid())

    # --- Additional User & Company Signup Form Tests ---
    def test_user_signup_form_invalid_email(self):
        form = UserSignUpForm(data={
            'username': 'user123',
            'email': 'invalid-email',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertFalse(form.is_valid())
    
    def test_company_signup_form_invalid_email(self):
        form = CompanySignUpForm(data={
            'username': 'company123',
            'email': 'invalid-email',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'company_name': 'New Tech Co',
            'industry': 'Software'
        })
        self.assertFalse(form.is_valid())
    
    def test_company_signup_form_missing_industry(self):
        form = CompanySignUpForm(data={
            'username': 'company123',
            'email': 'company123@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'company_name': 'New Tech Co'
        })
        self.assertFalse(form.is_valid())

    


    from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model


User = get_user_model()


# Test cases for CompanyProfileForm
class CompanyProfileFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_company_name(self):
        form_data = {
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)

    def test_missing_industry(self):
        form_data = {
            'company_name': 'Test Company',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('industry', form.errors)

    def test_invalid_email(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'invalid-email',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_missing_email(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_phone(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': 'invalid-phone',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_missing_location(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)

    def test_invalid_logo(self):
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data, files={'logo': invalid_file})
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_missing_description(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertTrue(form.is_valid())  # Description is not required

    def test_save_form(self):
        form_data = {
            'company_name': 'Test Company',
            'industry': 'Tech',
            'email': 'test@example.com',
            'phone': '1234567890',
            'location': 'Test Location',
            'description': 'Test Description',
        }
        form = CompanyProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        user.save()
        self.assertEqual(user.company_name, 'Test Company')


# Test cases for ReviewForm
class ReviewFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'text': 'This is a great company!',
            'rating': 5,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_text(self):
        form_data = {
            'rating': 5,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

    def test_missing_rating(self):
        form_data = {
            'text': 'This is a great company!',
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_rating_below_min(self):
        form_data = {
            'text': 'This is a great company!',
            'rating': 0,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_rating_above_max(self):
        form_data = {
            'text': 'This is a great company!',
            'rating': 6,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_save_form(self):
        form_data = {
            'text': 'This is a great company!',
            'rating': 5,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        review = form.save(commit=False)
        review.save()
        self.assertEqual(review.text, 'This is a great company!')


# Test cases for CompanyEditForm
class CompanyEditFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'description': 'Updated description',
        }
        form = CompanyEditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_logo(self):
        form_data = {
            'description': 'Updated description',
        }
        form = CompanyEditForm(data=form_data)
        self.assertTrue(form.is_valid())  # Logo is not required

    def test_missing_description(self):
        form_data = {}
        form = CompanyEditForm(data=form_data)
        self.assertTrue(form.is_valid())  # Description is not required

    def test_invalid_logo(self):
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        form_data = {
            'description': 'Updated description',
        }
        form = CompanyEditForm(data=form_data, files={'logo': invalid_file})
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_save_form(self):
        form_data = {
            'description': 'Updated description',
        }
        form = CompanyEditForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = User.objects.create(username='testuser')
        user = form.save(commit=False, instance=user)
        user.save()
        self.assertEqual(user.description, 'Updated description')


# Test cases for JobPostingForm
class JobPostingFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_job_title(self):
        form_data = {
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('job_title', form.errors)

    def test_missing_location(self):
        form_data = {
            'job_title': 'Software Engineer',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)

    def test_missing_contract_type(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('contract_type', form.errors)

    def test_invalid_salary_range(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': 'Invalid',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('salary_range', form.errors)

    def test_missing_job_overview(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('job_overview', form.errors)

    def test_missing_roles_responsibilities(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('roles_responsibilities', form.errors)

    def test_missing_education_required(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('education_required', form.errors)

    def test_invalid_application_deadline(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2020-01-01',  # Past date
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('application_deadline', form.errors)

    def test_save_form(self):
        form_data = {
            'job_title': 'Software Engineer',
            'location': 'Remote',
            'contract_type': 'Full-time',
            'salary_range': '$80,000 - $100,000',
            'job_overview': 'Job overview',
            'roles_responsibilities': 'Roles and responsibilities',
            'education_required': 'Bachelor\'s degree',
            'application_deadline': '2023-12-31',
        }
        form = JobPostingForm(data=form_data)
        self.assertTrue(form.is_valid())
        job_posting = form.save(commit=False)
        job_posting.save()
        self.assertEqual(job_posting.job_title, 'Software Engineer')


# Test cases for UserLoginForm
class UserLoginFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_username(self):
        form_data = {
            'password': 'testpassword123',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        form_data = {
            'username': 'testuser',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


# Test cases for CompanyLoginForm
class CompanyLoginFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'username': 'testcompany',
            'password': 'testpassword123',
        }
        form = CompanyLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_username(self):
        form_data = {
            'password': 'testpassword123',
        }
        form = CompanyLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_password(self):
        form_data = {
            'username': 'testcompany',
        }
        form = CompanyLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


# Test cases for UserSignUpForm
class UserSignUpFormTest(TestCase):
    def test_valid_data(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_username(self):
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_email(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_missing_first_name(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_missing_last_name(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = UserSignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

   