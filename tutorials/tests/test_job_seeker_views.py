from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import json

from tutorials.models.accounts import CustomUser
from tutorials.models.applications import JobApplication, Notification, JobPosting
from tutorials.models.standard_cv import UserCV, CVApplication
from tutorials.models.user_dashboard import UploadedCV, UserDocument


class UserDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.cv = UserCV.objects.create(user=self.user, key_skills='Python, Django')
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test.pdf')
        self.document = UserDocument.objects.create(user=self.user, file='test_doc.pdf')

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_company_user_access(self):
        company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        self.client.login(username='company', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_info_rendering(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertContains(response, 'Logout')

    def test_cv_data_rendering(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertContains(response, 'Python, Django')

    def test_raw_cv_upload_info_rendering(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertContains(response, 'test.pdf')

    def test_supporting_documents_rendering(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_dashboard'))
        self.assertContains(response, 'test_doc.pdf')


class MyJobsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('my_jobs'))
        self.assertEqual(response.status_code, 200)

    def test_template_rendering(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('my_jobs'))
        self.assertTemplateUsed(response, 'jobseeker/my_jobs.html')

class DeleteJobTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        
        # Create a JobPosting
        self.job_posting = JobPosting.objects.create(
            company=self.company_user,
            job_title='Software Engineer',
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        
        # Create a JobApplication with the required job_posting
        self.job_application = JobApplication.objects.create(
            applicant=self.user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='12345'
        )

    def test_delete_valid_job(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete-job', args=[self.job_application.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

    def test_delete_non_existent_job(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete-job', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_job_not_belonging_to_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')
        job_application = JobApplication.objects.create(
            applicant=other_user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='67890'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete-job', args=[job_application.id]))
        self.assertEqual(response.status_code, 404)


class NotificationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.notification = Notification.objects.create(recipient=self.user, message='Test notification')

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)

    def test_ajax_unread_count(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notifications'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'unread_count': 1})

    def test_no_notifications(self):
        self.notification.delete()
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'notifications')


class MarkNotificationReadTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.notification = Notification.objects.create(recipient=self.user, message='Test notification')

    def test_mark_notification_read(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('mark_notification_read', args=[self.notification.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})

    def test_mark_non_existent_notification_read(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('mark_notification_read', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_mark_notification_read_not_belonging_to_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')
        notification = Notification.objects.create(recipient=other_user, message='Test notification')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('mark_notification_read', args=[notification.id]))
        self.assertEqual(response.status_code, 404)


class UserApplicationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        
        # Create a JobPosting
        self.job_posting = JobPosting.objects.create(
            company=self.company_user,
            job_title='Software Engineer',
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        
        # Create a JobApplication with the required job_posting
        self.job_application = JobApplication.objects.create(
            applicant=self.user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='12345'
        )

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_applications'))
        self.assertEqual(response.status_code, 200)

    def test_no_applications(self):
        self.job_application.delete()
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Applications')


class UserApplicationDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        
        # Create a JobPosting
        self.job_posting = JobPosting.objects.create(
            company=self.company_user,
            job_title='Software Engineer',
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        
        # Create a JobApplication with the required job_posting
        self.job_application = JobApplication.objects.create(
            applicant=self.user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='12345'
        )

    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_application_detail', args=[self.job_application.id]))
        self.assertEqual(response.status_code, 200)

    def test_non_existent_application(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_application_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_application_not_belonging_to_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')
        job_application = JobApplication.objects.create(
            applicant=other_user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='67890'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_application_detail', args=[job_application.id]))
        self.assertEqual(response.status_code, 404)


class DeleteUserDocumentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.document = UserDocument.objects.create(user=self.user, file='test_doc.pdf')

    def test_delete_valid_document(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_user_document'), {'filename': 'test_doc.pdf'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

    def test_delete_non_existent_document(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_user_document'), {'filename': 'nonexistent.pdf'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Document not found'})

    def test_delete_document_not_belonging_to_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')
        document = UserDocument.objects.create(user=other_user, file='other_doc.pdf')
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_user_document'), {'filename': 'other_doc.pdf'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Document not found'})


class GetUserDocumentsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_upload_document(self):
        self.client.login(username='testuser', password='testpass')
        file = SimpleUploadedFile('test_doc.pdf', b'file_content', content_type='application/pdf')
        response = self.client.post(reverse('upload_user_document'), {'document': file})
        self.assertEqual(response.status_code, 200)
       

    def test_upload_document_limit_reached(self):
        for i in range(5):
            UserDocument.objects.create(user=self.user, file=f'test_doc_{i}.pdf')
        self.client.login(username='testuser', password='testpass')
        file = SimpleUploadedFile('test_doc.pdf', b'file_content', content_type='application/pdf')
        response = self.client.post(reverse('upload_user_document'), {'document': file})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'You can only upload up to 5 documents.'})

    def test_upload_no_file(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('upload_user_document'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'No file uploaded.'})

class AddJobByCodeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.company_user = CustomUser.objects.create_user(username='company', password='testpass', is_company=True)
        
        # Create a JobPosting
        self.job_posting = JobPosting.objects.create(
            company=self.company_user,
            job_title='Software Engineer',
            location='New York',
            salary_range='2000',
            contract_type='Full-time'
        )
        
        # Create a JobApplication with the required job_posting
        self.job_application = JobApplication.objects.create(
            applicant=self.user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='12345'
        )

    def test_add_job_by_code_valid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '12345'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

    def test_add_job_by_code_invalid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '67890'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Job application not found.'})

    def test_add_job_by_code_not_belonging_to_user(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')
        job_application = JobApplication.objects.create(
            applicant=other_user,
            company=self.company_user,
            job_posting=self.job_posting,
            application_id='67890'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_job_by_code'), json.dumps({'code': '67890'}), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'This job application does not belong to you.'})


class UploadCVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_upload_cv_invalid(self):
        self.client.login(username='testuser', password='testpass')
        file = SimpleUploadedFile('test_cv.pdf', b'file_content', content_type='application/pdf')
        response = self.client.post(reverse('upload_cv'), {'cv_file': file})
        self.assertEqual(response.status_code, 500)

    def test_upload_cv_invalid_file_type(self):
        self.client.login(username='testuser', password='testpass')
        file = SimpleUploadedFile('test_cv.txt', b'file_content', content_type='text/plain')
        response = self.client.post(reverse('upload_cv'), {'cv_file': file})
        self.assertEqual(response.status_code, 500)

    def test_upload_cv_no_file(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('upload_cv'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'No file uploaded'})


class UploadRawCVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_upload_raw_cv_valid(self):
        self.client.login(username='testuser', password='testpass')
        file = SimpleUploadedFile('test_cv.pdf', b'file_content', content_type='application/pdf')
        response = self.client.post(reverse('upload_raw_cv'), {'cv_file': file})
        self.assertEqual(response.status_code, 200)
     

    def test_upload_raw_cv_no_file(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('upload_raw_cv'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'No file uploaded'})


class DeleteRawCVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.uploaded_cv = UploadedCV.objects.create(user=self.user, file='test_cv.pdf')

    def test_delete_raw_cv_valid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

    def test_delete_raw_cv_no_file(self):
        self.uploaded_cv.delete()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_raw_cv'))
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'No uploaded CV found.'})





