from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.forms import UserLoginForm, CompanyLoginForm, UserSignUpForm, CompanySignUpForm, UserUpdateForm, MyPasswordChangeForm
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings

# Use the custom user model
CustomUser = get_user_model()

class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a regular user
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass123', is_company=False)
        # Create a company user
        self.company = CustomUser.objects.create_user(username='testcompany', password='testpass123', is_company=True)
        self.login_url = reverse('login')
        self.signup_url = reverse('signup')
        self.settings_url = reverse('settings')
        self.delete_account_url = reverse('delete_account')
        self.guest_url = reverse('guest')
        self.user_dashboard_url = reverse('user_dashboard')
        self.employer_dashboard_url = reverse('employer_dashboard')



    # 2. Test `login_view` View
    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], UserLoginForm)




    # 3. Test `signup_view` View
    def test_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], UserSignUpForm)
        self.assertIsInstance(response.context['company_form'], CompanySignUpForm)




    # 4. Test `profile_settings` View
    def test_profile_settings_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['details_form'], UserUpdateForm)
        self.assertIsInstance(response.context['password_form'], MyPasswordChangeForm)

    def test_profile_settings_update_details_valid(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'username': 'updateduser',
        })
        self.assertRedirects(response, self.settings_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')


   

    def test_profile_settings_delete_account(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'delete_account': 'on',
        })
        self.assertRedirects(response, self.guest_url)
        self.assertFalse(CustomUser.objects.filter(username='testuser').exists())

    
    def test_login_with_space(self):
        response = self.client.post(self.login_url, {
            'company-username': '',  # Empty username
            'company-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        
        # Check for the error message in the response content
       
    def test_login_view_with_empty_username(self):
        response = self.client.post(self.login_url, {
            'company-username': '',  # Empty username
            'company-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_empty_company_password(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': '',  # Empty password
        })
        self.assertEqual(response.status_code, 200)
        
      
            

    # 5. Test `delete_account` View
    def test_delete_account_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.delete_account_url)
        self.assertRedirects(response, self.guest_url)
        self.assertFalse(CustomUser.objects.filter(username='testuser').exists())
    
    def test_profile_settings_change_password_with_invalid_old_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'wrongpass',  # Incorrect old password
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)
        
    # Extract the password_form from the response context
        password_form = response.context['password_form']



   

    # 3. Test `profile_settings` View
    def test_profile_settings_update_details_with_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
        'update_details': 'on',
        'username': '',  # Empty username
        })
        self.assertEqual(response.status_code, 200)
    
         # Extract the details_form from the response context
        details_form = response.context['details_form']
    
    
    def test_profile_settings_change_password_with_mismatched_new_passwords(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass',  # Mismatched new passwords
        })
        self.assertEqual(response.status_code, 200)
        
        # Extract the form from the response context
        password_form = response.context['password_form']
        
        # Check for the error in the form
        self.assertFormError(password_form, 'new_password2', 'The two password fields didn’t match.')

    # 4. Test `delete_account` View
    def test_delete_account_with_unauthenticated_user(self):
        response = self.client.post(self.delete_account_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_account_url}")

    def test_login_view_with_valid_company_credentials(self):
        response = self.client.post(self.login_url, {
            'company_username': 'testcompany',
            'company_password': 'testpass123',
        })
        
        self.assertEqual(response.status_code, 200)


    def test_delete_account(self):
        response = self.client.post(self.delete_account_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_account_url}")

    
    def test_valid_login(self):
        response = self.client.post(self.login_url, {
            'company_username': 'testcompany',
            'company_password': 'testpass123',
        })
        
        self.assertEqual(response.status_code, 200)
    
    def test_not_found_account(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.company)
        self.assertEqual(response.status_code, 404)

    def test_profile_settings_change_password_with_weak_new_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'testpass123',
            'new_password1': '123',  # Weak password
            'new_password2': '123',  # Weak password
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_settings_update_details_with_invalid_email(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'email': 'invalidemail',  # Invalid email
        })
        self.assertEqual(response.status_code, 200)
        
        # Extract the details_form from the response context
        details_form = response.context['details_form']
        
        # Check for the error in the form
        self.assertFormError(details_form, 'email', 'Enter a valid email address.')
    

    def test_profile_settings_update_details_with_valid_email(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'email': 'newemail@example.com',  # Valid email
        })
    
        self.assertEqual(response.status_code,200)

    def test_login(self):
        response = self.client.post(self.login_url, {
            'user-username': 'testuser',
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code,200)

    def test_valid_username(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code,200)
   
    
    def test_login_view(self):
        response = self.client.post(self.login_url, {
            'user-username': '',  # Empty username
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with(self):
        response = self.client.post(self.login_url, {
            'user-username': '',  # Empty username
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        

    def test_login_view_with_credentials(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': 'wrongpass', 
        })
        self.assertEqual(response.status_code, 200)
        


    def test_login_view_company(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': '',  # Empty password
        })
        self.assertEqual(response.status_code, 200)
    

    # 1. Test `login_view` View
    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], UserLoginForm)

    def test_login_view_with_valid_user_credentials(self):
        response = self.client.post(self.login_url, {
            'user-username': 'testuser',
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)


    def test_login_view_with_invalid_user_credentials(self):
        response = self.client.post(self.login_url, {
            'user-username': 'testuser',
            'user-password': 'wrongpass',  # Incorrect password
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_empty_user_password(self):
        response = self.client.post(self.login_url, {
            'user-username': 'testuser',
            'user-password': '',  # Empty password
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_empty_user_username(self):
        response = self.client.post(self.login_url, {
            'user-username': '',  # Empty username
            'user-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_valid_company_credentials(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)


    def test_login_view_with_invalid_company_credentials(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': 'wrongpass',  # Incorrect password
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_empty_company_password(self):
        response = self.client.post(self.login_url, {
            'company-username': 'testcompany',
            'company-password': '',  # Empty password
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_with_empty_company_username(self):
        response = self.client.post(self.login_url, {
            'company-username': '',  # Empty username
            'company-password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)



    # 3. Test `profile_settings` View
    def test_profile_settings_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['details_form'], UserUpdateForm)
        self.assertIsInstance(response.context['password_form'], MyPasswordChangeForm)

    def test_profile_settings_update_details_valid(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'username': 'updateduser',
        })
        self.assertRedirects(response, self.settings_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_profile_settings_update_details_with_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'username': '',  # Empty username
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_profile_settings_update_details_with_valid_email(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'email': 'newemail@example.com',  # Valid email
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)


    def test_profile_settings_update_details_with_invalid_email(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'update_details': 'on',
            'email': 'invalidemail',  # Invalid email
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')

    def test_profile_settings_change_password_with_valid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)


    def test_profile_settings_change_password_with_invalid_old_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'wrongpass',  # Incorrect old password
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your old password was entered incorrectly.')

    def test_profile_settings_change_password_with_mismatched_new_passwords(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass',  # Mismatched new passwords
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')

    def test_profile_settings_change_password_with_weak_new_password(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'change_password': 'on',
            'old_password': 'testpass123',
            'new_password1': '123',  # Weak password
            'new_password2': '123',  # Weak password
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_settings_delete_account(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.settings_url, {
            'delete_account': 'on',
        })
        self.assertRedirects(response, self.guest_url)
        self.assertFalse(CustomUser.objects.filter(username='testuser').exists())

    # 4. Test `delete_account` View
    def test_delete_account_with_unauthenticated_user(self):
        response = self.client.post(self.delete_account_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_account_url}")

    def test_delete_account_with_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.employer_dashboard_url)
        self.assertEqual(response.status_code, 302)



        

    
    



    
        
     
      
