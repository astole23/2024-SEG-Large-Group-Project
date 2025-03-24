from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models.jobposting import JobPosting
from tutorials.models.applications import JobApplication
from django.contrib.messages import get_messages

User = get_user_model()


class JobPortalViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='pass'
        )

        # ✅ Ensure this matches your actual model: could be is_company, user_type, etc.
        self.company_user = User.objects.create_user(
            username='company',
            email='company@example.com',
            password='pass',
            is_company=True  # <-- This line is essential
        )

        self.job1 = JobPosting.objects.create(
            job_title="Software Developer",
            location="New York",
            salary_range=60000,
            contract_type="Full-time",
            education_required="Bachelor's",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="Python, Django",
            company=self.company_user,
            perks="Remote work opportunities|Free lunch/snacks"
        )

        self.job2 = JobPosting.objects.create(
            job_title="Marketing Intern",
            location="Los Angeles",
            salary_range=20000,
            contract_type="Internship",
            education_required="High School",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="SEO, Content Creation",
            company=self.company_user,
            perks="Paid time off (PTO)|Free training and certifications"
        )

        self.application = JobApplication.objects.create(
            applicant=self.user,
            job_posting=self.job1,
            company=self.company_user,
            tracked=True,
            status='rejected'  # ✅ Must match one of your model's STATUS_CHOICES
        )

    # --- Search view tests ---

    def test_search_empty_query(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Software Developer")
        self.assertContains(response, "Marketing Intern")

    def test_search_by_query(self):
        response = self.client.get(reverse('search'), {'q': 'Software'})
        self.assertContains(response, "Software Developer")
        self.assertNotContains(response, "Marketing Intern")

    def test_filter_by_education(self):
        response = self.client.get(reverse('search'), {'education_required': ["Bachelor's"]})
        self.assertContains(response, "Software Developer")
        self.assertNotContains(response, "Marketing Intern")

    def test_filter_by_job_type(self):
        response = self.client.get(reverse('search'), {'job_type': ['Internship']})
        self.assertContains(response, "Marketing Intern")

    def test_filter_by_industry(self):
        response = self.client.get(reverse('search'), {'industry': ['Software Developer']})
        self.assertContains(response, "Software Developer")

    def test_filter_by_location(self):
        response = self.client.get(reverse('search'), {'location_filter': ['Los Angeles']})
        self.assertContains(response, "Marketing Intern")

    def test_filter_by_perks(self):
        response = self.client.get(reverse('search'), {'benefits': ['Remote work opportunities']})
        self.assertContains(response, "Software Developer")

    def test_filter_by_work_flexibility(self):
        self.job1.work_type = 'Hybrid'
        self.job1.save()
        response = self.client.get(reverse('search'), {'work_flexibility': ['Hybrid']})
        self.assertContains(response, "Software Developer")

    def test_filter_by_salary(self):
        response = self.client.get(reverse('search'), {'salary_range': 50000})
        self.assertContains(response, "Software Developer")
        self.assertNotContains(response, "Marketing Intern")

    def test_combined_filters(self):
        response = self.client.get(reverse('search'), {
            'education_required': ["Bachelor's"],
            'job_type': ['Full-time'],
            'location_filter': ['New York'],
        })
        self.assertContains(response, "Software Developer")

    def test_invalid_filter_values(self):
        response = self.client.get(reverse('search'), {
            'education_required': ['PhD'],
            'job_type': ['Temporary']
        })
        self.assertNotContains(response, "Software Developer")
        self.assertNotContains(response, "Marketing Intern")

    def test_search_pagination(self):
        response = self.client.get(reverse('search'), {'page': 1})
        self.assertEqual(response.status_code, 200)

    def test_special_characters_in_perks(self):
        self.job1.perks = "Free snacks & drinks"
        self.job1.save()
        response = self.client.get(reverse('search'), {'benefits': ['Free snacks & drinks']})
        self.assertContains(response, "Software Developer")

    def test_multiple_filter_values(self):
        response = self.client.get(reverse('search'), {
            'location_filter': ['New York', 'Los Angeles'],
            'job_type': ['Full-time', 'Internship'],
        })
        self.assertContains(response, "Software Developer")
        self.assertContains(response, "Marketing Intern")

    def test_search_template_context(self):
        response = self.client.get(reverse('search'))
        self.assertIn('job_postings', response.context)
        self.assertIn('industries', response.context)
        self.assertIn('perks_list', response.context)

    # --- tracked_jobs_api tests ---

    def test_tracked_jobs_requires_login(self):
        response = self.client.get(reverse('tracked_jobs_api'))
        self.assertEqual(response.status_code, 302)

    def test_tracked_jobs_empty(self):
        self.application.tracked = False
        self.application.save()
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('tracked_jobs_api'))
        self.assertJSONEqual(response.content, [])

    def test_tracked_jobs_present(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('tracked_jobs_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Developer')

    # --- job_postings_api tests ---

    def test_job_postings_api_response(self):
        response = self.client.get(reverse('job_postings_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_job_postings_api_structure(self):
        response = self.client.get(reverse('job_postings_api'))
        first = response.json()[0]
        self.assertIn('job_title', first)
        self.assertIn('location', first)
        self.assertIn('salary_range', first)

    # --- update_application_status ---

    def test_update_application_status_valid(self):
        self.client.login(username='company', password='pass')
        url = reverse('update_application_status', args=[self.application.id, 'rejecteq'])
        response = self.client.get(url)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'rejected')

    def test_update_application_status_invalid(self):
        self.client.login(username='company', password='pass')
        url = reverse('update_application_status', args=[self.application.id, 'not_a_status'])
        response = self.client.get(url)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Invalid status.", messages)

    def test_update_application_status_wrong_user(self):
        self.client.login(username='user', password='pass')
        url = reverse('update_application_status', args=[self.application.id, 'interviewing'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
