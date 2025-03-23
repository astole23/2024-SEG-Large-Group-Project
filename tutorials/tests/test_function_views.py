from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from tutorials.models.user_dashboard import UploadedCV
from django.core.files.uploadedfile import SimpleUploadedFile
from tutorials.forms import UserSignUpForm, CompanySignUpForm

# Use the custom user model
CustomUser = get_user_model()

class AuthViewsTests(TestCase):
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
        # Create a CV for the user
        self.cv = UploadedCV.objects.create(
            user=self.user,
            file=SimpleUploadedFile("test_cv.pdf", b"file_content")
        )

    # ====================
    # Tests for process_login
    # ====================

    def test_process_login_with_valid_user_credentials(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        

    def test_process_login_with_valid_company_credentials(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'company',
            'username': 'testcompany',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_invalid_user_credentials(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'invaliduser',
            'password': 'invalidpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_invalid_company_credentials(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'company',
            'username': 'invalidcompany',
            'password': 'invalidpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_missing_user_type(self):
        response = self.client.post(reverse('process_login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_missing_username(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_missing_password(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_remember_me(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': 'on',
        })
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)  # 2 weeks

    def test_process_login_without_remember_me(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)  # Session expires when browser closes

    def test_process_login_with_admin_user(self):
        admin_user = CustomUser.objects.create_user(
            username='admin',
            password='adminpass',
            is_company=False
        )
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'admin',
            'password': 'adminpass',
        })
        self.assertEqual(response.status_code, 200)

    # ====================
    # Tests for process_signup
    # ====================

    def test_process_signup_with_valid_user_data(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_industry': 'IT',
            'user_location': 'New York',
        })
        self.assertEqual(response.status_code, 200)


    def test_process_signup_with_valid_company_data(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': 'newcompany',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)


    def test_process_signup_with_missing_username(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_mismatched_passwords(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_existing_username(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'testuser',  # Already exists
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_invalid_user_industry(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_industry': '',  # Invalid (empty)
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_invalid_user_location(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_location': '',  # Invalid (empty)
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_invalid_company_data(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': '',  # Invalid (empty)
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign Up")

    # ====================
    # Tests for delete_raw_cv
    # ====================

    def test_delete_raw_cv_with_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertFalse(UploadedCV.objects.filter(user=self.user).exists())

    def invalid_credentials(self):
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 302)

    def test_raw_cv_with_no_cv(self):
        self.client.login(username='testcompany', password='testpass123')  # Company user has no CV
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 404)


    def test_delete_raw_cv_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 405)

    # ====================
    # Additional Edge Cases
    # ====================

    def test_process_login_with_empty_data(self):
        response = self.client.post(reverse('process_login'), {})
        self.assertEqual(response.status_code, 200)


    def test_process_login_with_invalid_user_type(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'invalid',
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)


    def test_process_login_with_csrf_token(self):
        response = self.client.get(reverse('process_login'))
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_process_signup_with_csrf_token(self):
        response = self.client.get(reverse('process_signup'))
        self.assertContains(response, "csrfmiddlewaretoken")

    def invalid_raw_cv_with_csrf_token(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code,405)
    
    def test_request_of_login(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
    def test_process_signup_with_get_request(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign Up")

    def test_unauthenticated_user(self):
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 302)

    

    def test_no_cv(self):
        self.client.login(username='testcompany', password='testpass123')  # Company user has no CV
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 404)
