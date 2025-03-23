from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from tutorials.models import JobPosting, JobApplication, Review, Notification
from tutorials.forms import CompanyProfileForm
from django.contrib import messages

# Use the custom user model
CustomUser = get_user_model()

class CompanyViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a regular user
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass123', is_company=False)
        # Create a company user
        self.company = CustomUser.objects.create_user(username='testcompany', password='testpass123', is_company=True)
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
        # Create a job application with a valid status
        self.job_application = JobApplication.objects.create(
            job_posting=self.job_posting,
            applicant=self.user,
            company=self.company,
            status='rejected'  # Use a valid choice
        )
        # URLs
        self.employer_dashboard_url = reverse('employer_dashboard')
        self.company_detail_url = reverse('company_detail', args=[self.company.id])
        self.company_profile_url = reverse('company_profile')
        self.leave_review_url = reverse('leave_review', args=[self.company.id])
        self.edit_company_url = reverse('edit_company', args=[self.company.id])
        self.company_applications_url = reverse('company_applications')
        self.company_application_detail_url = reverse('company_application_detail', args=[self.job_application.id])
        self.update_application_status_url = reverse('update_application_status', args=[self.job_application.id, 'Approved'])  # Use a valid choice
        self.create_job_posting_url = reverse('create_job_posting')

    # 1. Test `employer_dashboard` View
    def test_employer_dashboard_with_company_user(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(self.employer_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/employer_dashboard.html')


    def test_employer_dashboard_with_non_company_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.employer_dashboard_url)
        self.assertRedirects(response, reverse('login'))
        
        # Retrieve messages and check for the expected message
        messages_found = False
        for message in messages.get_messages(response.wsgi_request):
            if str(message) == "Access restricted to company accounts only.":
                messages_found = True
                break
        
        self.assertTrue(messages_found, "Expected 'Access restricted to company accounts only.' message not found in messages.")


    # 3. Test `company_profile` View
    def test_company_profile_with_company_user(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(self.company_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/company_profile.html')


    def test_company_profile_with_non_company_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.company_profile_url)
        self.assertRedirects(response, reverse('login'))
        
        # Retrieve messages and check for the expected message
        messages_found = False
        for message in messages.get_messages(response.wsgi_request):
            if str(message) == "Access restricted to company accounts only.":
                messages_found = True
                break
        
        self.assertTrue(messages_found, "Expected 'Access restricted to company accounts only.' message not found in messages.")

 
    def test_company_profile_post_valid_data(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.post(self.company_profile_url, {
            'company_name': 'Updated Company',
            'description': 'Updated description',
        })
        self.assertEqual(response.status_code, 200)
        self.company.refresh_from_db()
        self.assertEqual(self.company.company_name, 'Updated Company')

    # 4. Test `leave_review` View
    def test_leave_review_with_valid_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.leave_review_url, {
            'text': 'Great company!',
            'rating': '5',
        })
        self.assertEqual(response.status_code,302)

    def test_leave_review_with_missing_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.leave_review_url, {
            'text': '',  # Missing text
            'rating': '5',
        })
        self.assertEqual(response.status_code,302)

    # 5. Test `edit_company` View
    def test_edit_company_get(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(self.edit_company_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/edit_company.html')

  

    # 6. Test `company_applications` View
    def test_company_applications_with_company_user(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(self.company_applications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/company_applications.html')

    def test_company_applications_with_non_company_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.company_applications_url)
        self.assertRedirects(response, reverse('login'))
        
        # Retrieve messages and check for the expected message
        messages_found = False
        for message in messages.get_messages(response.wsgi_request):
            if str(message) == "Access restricted to company accounts only.":
                messages_found = True
                break
    
        self.assertTrue(messages_found, "Expected 'Access restricted to company accounts only.' message not found in messages.")
    # 7. Test `company_application_detail` View
    def test_company_application_detail_with_company_user(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.get(self.company_application_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'company/company_application_detail.html')

    def test_company_application_detail_with_non_company_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.company_application_detail_url)
        self.assertEqual(response.status_code, 404)  

    # 8. Test `update_application_status` View
    def test_update_application_status_with_valid_status(self):
        self.client.login(username='testcompany', password='testpass123')
        update_url = reverse('update_application_status', args=[self.job_application.id, 'rejected'])  
        response = self.client.post(update_url)
        self.assertRedirects(response, reverse('company_applications'))
        self.job_application.refresh_from_db()
        self.assertEqual(self.job_application.status, 'rejected')
   

  
    def test_update_application_status_with_rejected_status(self):
        self.client.login(username='testcompany', password='testpass123')
        update_url = reverse('update_application_status', args=[self.job_application.id, 'Rejected'])  # Use a valid choice
        response = self.client.post(update_url)
        self.assertRedirects(response, reverse('company_applications'))
        self.job_application.refresh_from_db()
        self.assertEqual(self.job_application.status, 'Rejected')

    def test_update_application_status_with_rejected_status(self):
        self.client.login(username='testcompany', password='testpass123')
        update_url = reverse('update_application_status', args=[self.job_application.id, 'rejected'])  # Use a valid choice
        response = self.client.post(update_url)
        self.assertRedirects(response, reverse('company_applications'))
        self.job_application.refresh_from_db()
        self.assertEqual(self.job_application.status, 'rejected')


  
    
    def test_create_job_posting_with_missing_required_fields(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.post(self.create_job_posting_url, {
            'job_title': '',  # Missing job title
            'location': 'Remote',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software applications.',
            'roles_responsibilities': 'Write code and debug.',
            'required_skills': 'Python, Django',
            'perks': 'Health insurance',
            'application_deadline': '2023-12-31'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request

    def test_leave_review_with_unauthenticated_user(self):
        response = self.client.post(self.leave_review_url, {
            'text': 'Great company!',
            'rating': '5',
        })
        self.assertEqual(response.status_code, 302)  

    
    def test_update_application_status_with_nonexistent_application(self):
        self.client.login(username='testcompany', password='testpass123')
        non_existent_application_url = reverse('update_application_status', args=[999, 'Approved'])  # Non-existent application ID
        response = self.client.post(non_existent_application_url)
        self.assertEqual(response.status_code, 302)  

    def test_company_application_detail_with_nonexistent_application(self):
        self.client.login(username='testcompany', password='testpass123')
        non_existent_application_url = reverse('company_application_detail', args=[999])  # Non-existent application ID
        response = self.client.get(non_existent_application_url)
        self.assertEqual(response.status_code, 404)  # Not Found

    def test_company_detail_with_nonexistent_company(self):
        non_existent_company_url = reverse('company_detail', args=[999])  # Non-existent company ID
        response = self.client.get(non_existent_company_url)
        self.assertEqual(response.status_code, 404)  # Not Found

    def test_create_job_posting_with_missing_required_fields(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.post(self.create_job_posting_url, {
            'job_title': '',  # Missing job title
            'location': 'Remote',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software applications.',
            'roles_responsibilities': 'Write code and debug.',
            'required_skills': 'Python, Django',
            'perks': 'Health insurance',
            'application_deadline': '2023-12-31'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request

    def test_create_job_posting_with_other_missing_required_fields(self):
        self.client.login(username='testcompany', password='testpass123')
        response = self.client.post(self.create_job_posting_url, {
            'job_title': '',  # Missing job title
            'location': 'Remote',
            'contract_type': 'Full-time',
            'job_overview': 'Develop software applications.',
            'roles_responsibilities': 'Write code and debug.',
            'required_skills': 'Python, Django',
            'application_deadline': '2023-12-31'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request

  

    def test_company_detail_with_nonexistent_company(self):
        non_existent_company_url = reverse('company_detail', args=[999])  # Non-existent company ID
        response = self.client.get(non_existent_company_url)
        self.assertEqual(response.status_code, 404)  

    def test_update_application_status_with_nonexisten(self):
        self.client.login(username='testcompany', password='testpass123')
        non_existent_application_url = reverse('update_application_status', args=[999, 'Approved'])  # Non-existent application ID
        response = self.client.post(non_existent_application_url)
        self.assertEqual(response.status_code, 302)  

    def test_leave_review_with_nonexistent_company(self):
        self.client.login(username='testuser', password='testpass123')
        non_existent_company_url = reverse('leave_review', args=[999])  # Non-existent company ID
        response = self.client.post(non_existent_company_url, {
            'text': 'Great company!',
            'rating': '5',
        })
        self.assertEqual(response.status_code, 404)  

    def test_edit_company_with_nonexistent_company(self):
        self.client.login(username='testcompany', password='testpass123')
        non_existent_company_url = reverse('edit_company', args=[999])  # Non-existent company ID
        response = self.client.get(non_existent_company_url)
        self.assertEqual(response.status_code, 404)  

    def test_update_application_status_with_unauthorized_user(self):
        self.client.login(username='testuser', password='testpass123')
        update_url = reverse('update_application_status', args=[self.job_application.id, 'Approved'])
        response = self.client.post(update_url)
        self.assertEqual(response.status_code, 302)  #

    def test_leave_review_with_unauthenticated_user(self):
        response = self.client.post(self.leave_review_url, {
            'text': 'Great company!',
            'rating': '5',
        })

        self.assertEqual(response.status_code, 302)  


    def test_employer_dashboard_with_unauthenticated_user(self):
        response = self.client.get(self.employer_dashboard_url)
        self.assertEqual(response.status_code, 302)  

    def test_company_profile_with_unauthenticated_user(self):
        response = self.client.get(self.company_profile_url)
        self.assertEqual(response.status_code, 302)  

   
        

