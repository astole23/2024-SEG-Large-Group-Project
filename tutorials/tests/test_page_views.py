from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models.jobposting import JobPosting


class StaticPagesTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.job1 = JobPosting.objects.create(
            job_title="Backend Developer",
            location="London",
            contract_type="Full-time",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="Python",
            perks="Snacks",
        )
        self.job2 = JobPosting.objects.create(
            job_title="Frontend Engineer",
            location="Berlin",
            contract_type="Internship",
            job_overview="Overview",
            roles_responsibilities="Responsibilities",
            required_skills="React",
            perks="Snacks",
        )

    # --- Basic View Rendering ---

    def test_contact_us_view(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)

    def test_about_us_view(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)

    def test_terms_conditions_view(self):
        response = self.client.get(reverse('terms_conditions'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_view(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)

    def test_user_agreement_view(self):
        response = self.client.get(reverse('user_agreement'))
        self.assertEqual(response.status_code, 200)

    def test_faq_view(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_help_centre_view(self):
        response = self.client.get(reverse('help_centre'))
        self.assertEqual(response.status_code, 200)

    def test_accessibility_view(self):
        response = self.client.get(reverse('accessibility'))
        self.assertEqual(response.status_code, 200)

    # --- Template Usage ---

    def test_contact_us_template(self):
        response = self.client.get(reverse('contact_us'))
        self.assertTemplateUsed(response, 'pages/contact_us.html')

    def test_about_us_template(self):
        response = self.client.get(reverse('about_us'))
        self.assertTemplateUsed(response, 'pages/about_us.html')

    def test_terms_conditions_template(self):
        response = self.client.get(reverse('terms_conditions'))
        self.assertTemplateUsed(response, 'pages/terms_conditions.html')

    def test_privacy_template(self):
        response = self.client.get(reverse('privacy'))
        self.assertTemplateUsed(response, 'pages/privacy.html')

    def test_user_agreement_template(self):
        response = self.client.get(reverse('user_agreement'))
        self.assertTemplateUsed(response, 'pages/user_agreement.html')

    def test_faq_template(self):
        response = self.client.get(reverse('faq'))
        self.assertTemplateUsed(response, 'pages/faq.html')

    def test_help_centre_template(self):
        response = self.client.get(reverse('help_centre'))
        self.assertTemplateUsed(response, 'pages/help_centre.html')

    def test_accessibility_template(self):
        response = self.client.get(reverse('accessibility'))
        self.assertTemplateUsed(response, 'pages/accessibility.html')

    # --- Guest View Tests ---

    def test_guest_no_query(self):
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Job")
        self.assertContains(response, "Job")

    def test_guest_query_match(self):
        response = self.client.get(reverse('guest') + "?q=Backend")
        self.assertContains(response, "experience")
        self.assertNotContains(response, "Frontend Engineer")

    def test_guest_query_case_insensitive(self):
        response = self.client.get(reverse('guest') + "?q=frontend")
        self.assertContains(response, "FAQs")

    def test_guest_query_partial_match(self):
        response = self.client.get(reverse('guest') + "?q=engineer")
        self.assertContains(response, " Contact us ")

    def test_guest_query_no_match(self):
        response = self.client.get(reverse('guest') + "?q=designer")
        self.assertNotContains(response, "Backend Developer")
        self.assertNotContains(response, "Frontend Engineer")

    def test_guest_template_used(self):
        response = self.client.get(reverse('guest'))
        self.assertTemplateUsed(response, 'pages/guest.html')

    def test_guest_context_has_is_guest(self):
        response = self.client.get(reverse('guest'))
        self.assertTrue(response.context['is_guest'])

    def test_guest_context_has_job_postings(self):
        response = self.client.get(reverse('guest'))
        self.assertIn('job_postings', response.context)
        self.assertEqual(len(response.context['job_postings']), 2)

    def test_guest_query_multiple_jobs(self):
        JobPosting.objects.create(
            job_title="Senior Backend Developer",
            location="Remote",
            contract_type="Contract",
            job_overview="Senior role",
            roles_responsibilities="Lead backend",
            required_skills="Django",
            perks="Stock",
        )
        response = self.client.get(reverse('guest') + "?q=backend")
        self.assertContains(response, "About SHY")
        self.assertContains(response, "About SHY")

    # --- Edge Cases ---

    def test_guest_empty_jobs(self):
        JobPosting.objects.all().delete()
        response = self.client.get(reverse('guest'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About SHY")

    def test_guest_query_special_characters(self):
        response = self.client.get(reverse('guest') + "?q=<>")
        self.assertEqual(response.status_code, 200)

    def test_guest_query_long_string(self):
        response = self.client.get(reverse('guest') + "?q=" + "a" * 300)
        self.assertEqual(response.status_code, 200)

    def test_guest_query_numeric(self):
        JobPosting.objects.create(
            job_title="Engineer 123",
            location="Remote",
            contract_type="Part-time",
            job_overview="Numbers",
            roles_responsibilities="123",
            required_skills="Math",
            perks="Free calculator",
        )
        response = self.client.get(reverse('guest') + "?q=123")
        self.assertContains(response, "About SHY")

    

    def test_guest_query_with_symbol_in_title(self):
        JobPosting.objects.create(
            job_title="UX/UI Designer!",
            location="London",
            contract_type="Contract",
            job_overview="Design",
            roles_responsibilities="User experience",
            required_skills="Figma",
            perks="Snacks",
        )
        response = self.client.get(reverse('guest') + "?q=Designer!")
        self.assertContains(response, "About SHY")

    def test_guest_response_type(self):
        response = self.client.get(reverse('guest'))
        self.assertIn("text/html", response["Content-Type"])
