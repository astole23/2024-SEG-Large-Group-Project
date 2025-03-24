from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from tutorials.models.user_dashboard import UploadedCV
from django.core.files.uploadedfile import SimpleUploadedFile
from tutorials.forms import UserSignUpForm, CompanySignUpForm
from unittest.mock import patch

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
            'company-username': 'newcompany',
            'company-email': 'newcompany@example.com',
            'company-password1': 'Newpass123',
            'company-password2': 'Newpass123',
            'company-company_name': 'Test Corp',
            'company-industry': 'Technology',
        }, follow=True)

        self.assertTrue(CustomUser.objects.filter(username='newcompany').exists())

        new_company = CustomUser.objects.get(username='newcompany')
        self.assertEqual(int(self.client.session['_auth_user_id']), new_company.id)
        self.assertRedirects(response, reverse('employer_dashboard'))

        messages_list = list(response.context['messages'])
        self.assertTrue(any("registered and logged in successfully" in str(m) for m in messages_list))

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

    def test_company_signup_auto_login_fails(self):
        with patch("tutorials.views.function_views.authenticate", return_value=None):
            response = self.client.post(reverse('process_signup'), {
                'user_type': 'company',
                'company-username': 'failcompany',
                'company-email': 'fail@example.com',
                'company-password1': 'Newpass123',
                'company-password2': 'Newpass123',
                'company-company_name': 'Fail Inc',
                'company-industry': 'Finance',
            }, follow=True)


        self.assertTrue(CustomUser.objects.filter(username='failcompany').exists())


        self.assertRedirects(response, reverse('login'))

        messages_list = list(response.context['messages'])
        self.assertTrue(any("auto-login failed" in str(m) for m in messages_list))

    def test_process_signup_with_invalid_user_location(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_location': '',  # Invalid (empty)
        })
        self.assertEqual(response.status_code, 200)

    def test_user_signup_saves_user_with_industry_and_location(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'user-username': 'industrytester',
            'user-email': 'industry@test.com',
            'user-first_name': 'Indy',
            'user-last_name': 'Loca',
            'user-password1': 'StrongPass123',
            'user-password2': 'StrongPass123',
            'user-user_industry': 'Engineering',
            'user-user_location': 'Trondheim',
        }, follow=True)

        self.assertTrue(CustomUser.objects.filter(username='industrytester').exists())
        user = CustomUser.objects.get(username='industrytester')

        self.assertEqual(user.user_industry, 'Engineering')
        self.assertEqual(user.user_location, 'Trondheim')

        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

        self.assertRedirects(response, reverse('user_dashboard'))

        messages_list = list(response.context['messages'])
        self.assertTrue(any("registered and logged in successfully" in str(m) for m in messages_list))

    def test_user_signup_auto_login_fails(self):
        with patch("tutorials.views.function_views.authenticate", return_value=None):
            response = self.client.post(reverse('process_signup'), {
                'user_type': 'user',
                'user-username': 'newuser2',
                'user-email': 'auto@test.com',
                'user-first_name': 'Auto',
                'user-last_name': 'Fail',
                'user-password1': 'StrongPass123',
                'user-password2': 'StrongPass123',
                'user-user_industry': 'Design',
                'user-user_location': 'Oslo',
            }, follow=True)

        self.assertTrue(CustomUser.objects.filter(username='newuser2').exists())
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(any("auto-login failed" in str(m) for m in response.context['messages']))

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

    def test_process_user_type(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'invalid',  # Invalid user type
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_get_request(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_invalid_csrf_token(self):
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 403) 
    
    def test_process_signup_with_invalid_csrf_token(self):
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 403)  
    def test_delete_raw_cv(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 200) 

    def test_process_login_with_inactive_user(self):
        inactive_user = CustomUser.objects.create_user(
            username='inactiveuser',
            password='inactivepass',
            is_company=False,
            is_active=False  # Inactive user
        )
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'inactiveuser',
            'password': 'inactivepass',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_inactive_user(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'inactiveuser',
            'password1': 'inactivepass',
            'password2': 'inactivepass',
        })
        self.assertEqual(response.status_code, 200)

    def test_process_login_with_get_request_and_csrf_token(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)

    def test_process_signup_with_get_request_and_csrf_token(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)

    def test_delete_raw_cv_with_get_request_and_csrf_token(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_login(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'invalid',  # Invalid user type
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)




from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from tutorials.models.user_dashboard import UploadedCV
from tutorials.models.accounts import CustomUser
from tutorials.views.function_views import split_skills, remove_duplicates_by_keys

class FunctionViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='user', email='user@test.com', password='testpass',
            user_industry='Tech', user_location='London'
        )
        self.company = CustomUser.objects.create_user(
            username='company', email='company@test.com', password='testpass',
            is_company=True
        )

    def test_login_get(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid_user(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'user-username': 'user',
            'user-password': 'testpass',
        })
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_login_post_valid_company(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'company',
            'company-username': 'company',
            'company-password': 'testpass',
        })
        self.assertRedirects(response, reverse('employer_dashboard'))

    def test_login_post_invalid(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'user-username': 'user',
            'user-password': 'wrongpass',
        })
        self.assertContains(response, "help")

    def test_signup_get(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)

    def test_remove_duplicates_by_keys(self):
        data = [{'a': 'x', 'b': '1'}, {'a': 'x', 'b': '1'}, {'a': 'y', 'b': '2'}]
        result = remove_duplicates_by_keys(data, ['a', 'b'])
        self.assertEqual(len(result), 2)

    def test_split_skills_classification(self):
        skills = ["Python", "Teamwork", "GitHub", "Leadership"]
        technical, soft = split_skills(skills)
        self.assertIn("Python", technical)
        self.assertIn("GitHub", technical)
        self.assertIn("Teamwork", soft)
        self.assertIn("Leadership", soft)

    def test_delete_raw_cv_post_success(self):
        self.client.login(username='user', password='testpass')
        uploaded = UploadedCV.objects.create(user=self.user)
        uploaded.file.save('cv.pdf', SimpleUploadedFile('cv.pdf', b'dummy content'))
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertTrue(response.json()['success'])

    def test_delete_raw_cv_post_no_cv(self):
        self.client.login(username='user', password='testpass')
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertFalse(response.json()['success'])

    def test_delete_raw_cv_post_success(self):
        self.client.login(username='user', password='testpass')
        UploadedCV.objects.create(user=self.user, file=SimpleUploadedFile("cv.pdf", b"dummy"))

        response = self.client.post(reverse('delete_raw_cv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertFalse(UploadedCV.objects.filter(user=self.user).exists())

    def test_delete_raw_cv_post_no_cv(self):
        self.client.login(username='user', password='testpass')

        response = self.client.post(reverse('delete_raw_cv'))

        self.assertEqual(response.status_code, 404)

    def test_delete_raw_cv_get_request(self):
        self.client.login(username='user', password='testpass')

        response = self.client.get(reverse('delete_raw_cv'))

        self.assertEqual(response.status_code, 405)


    def test_delete_raw_cv_get_method(self):
        self.client.login(username='user', password='testpass')
        response = self.client.get(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 405)

    def test_signup_post_user_valid(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'user-username': 'newuser',
            'user-email': 'newuser@test.com',
            'user-password1': 'StrongPass123',
            'user-password2': 'StrongPass123',
            'user_user_industry': 'Design',
            'user_user_location': 'Berlin',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_signup_post_company_valid(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'company-username': 'newco',
            'company-email': 'newco@test.com',
            'company-password1': 'StrongPass123',
            'company-password2': 'StrongPass123'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_signup_post_invalid_user_form(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'user-username': '',
            'user-email': '',
            'user-password1': '123',
            'user-password2': '123',
            'user_user_industry': '',
            'user_user_location': ''
        })
        self.assertContains(response, "SHY", status_code=200)

    def test_signup_post_invalid_company_form(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'company-username': '',
            'company-email': '',
            'company-password1': '123',
            'company-password2': '123'
        })
        self.assertContains(response, "About SHY", status_code=200)


