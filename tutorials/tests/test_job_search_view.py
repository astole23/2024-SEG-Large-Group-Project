from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from tutorials.models.standard_cv import UserCV
from tutorials.models.jobposting import JobPosting
from tutorials.views.job_search import get_random_job_postings, safe_json_list
import json

CustomUser = get_user_model()

class JobRecommendationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="jobseeker",
            password="testpass123",
            user_industry=["Tech"],
            user_location=["London"]
        )
        self.client.login(username="jobseeker", password="testpass123")

        self.job1 = JobPosting.objects.create(
            job_title="Python Developer",
            location="London",
            company=self.user,
            contract_type="Full-time",
            job_overview="Build stuff",
            roles_responsibilities="Code things",
            required_skills="Python",
            perks="Free coffee"
        )
        self.job2 = JobPosting.objects.create(
            job_title="Data Scientist",
            location="Manchester",
            company=self.user,
            contract_type="Part-time",
            job_overview="Analyze stuff",
            roles_responsibilities="Model things",
            required_skills="Stats",
            perks="Remote work"
        )

    def test_get_random_job_postings_returns_jobs(self):
        jobs = get_random_job_postings(10)
        self.assertGreaterEqual(len(jobs), 1)

    @patch("tutorials.views.job_search.JobPosting.objects.count", return_value=0)
    def test_get_random_job_postings_returns_empty_when_no_jobs(self, mock_count):
        result = get_random_job_postings(limit=100)
        self.assertEqual(result, [])

    def test_safe_json_list_from_str(self):
        input_str = '[{"field": "value"}]'
        result = safe_json_list(input_str)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["field"], "value")

    def test_safe_json_list_invalid_str(self):
        result = safe_json_list("invalid_json")
        self.assertEqual(result, [])

    def test_safe_json_list_list_input(self):
        self.assertEqual(safe_json_list([1, 2]), [1, 2])

    def test_safe_json_list_other_input(self):
        self.assertEqual(safe_json_list(None), [])

    def test_job_recommendation_no_preferences_ajax(self):
        self.user.user_industry = []
        self.user.user_location = []
        self.user.save()

        response = self.client.get("/job_recommendation/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommended_jobs", response.json())

    @patch("tutorials.views.job_search.match_job_to_cv_together")
    @patch("tutorials.views.job_search.is_location_match", return_value=0.3)
    def test_job_recommendation_with_cv_and_preferences(self, mock_location, mock_match):
        UserCV.objects.create(
            user=self.user,
            personal_info={"first_name": "Test"},
            key_skills="Python",
            education=[{"fieldOfStudy": "Computer Science"}],
            work_experience=[{"job_title": "Developer"}]
        )
        mock_match.return_value = [("Python Developer", 0.8)]

        response = self.client.get("/job_recommendation/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        jobs = response.json().get("recommended_jobs")
        self.assertTrue(jobs)
        self.assertEqual(jobs[0]["job_title"], "Python Developer")

    @patch("tutorials.views.job_search.match_job_to_cv_together", return_value=[])
    def test_job_recommendation_no_cv(self, mock_match):
        UserCV.objects.filter(user=self.user).delete()
        response = self.client.get("/job_recommendation/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommended_jobs", response.json())

    def test_job_recommendation_html_response(self):
        response = self.client.get("/job_recommendation/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    @patch("tutorials.views.job_search.get_random_job_postings")
    def test_job_recommendation_html_response_fallback(self, mock_get_jobs):
        mock_job = JobPosting.objects.create(
            job_title="Fallback Developer",
            location="Leeds",
            company=self.user,
            contract_type="Internship",
            job_overview="Do stuff",
            roles_responsibilities="More stuff",
            required_skills="Logic",
            perks="Gym"
        )
        mock_get_jobs.return_value = [mock_job]

        self.user.user_industry = []
        self.user.user_location = []
        self.user.save()

        response = self.client.get("/job_recommendation/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fallback Developer")

    @patch("tutorials.views.job_search.match_job_to_cv_together")
    def test_job_recommendation_skips_duplicate_jobs(self, mock_match):
        UserCV.objects.create(
            user=self.user,
            personal_info={"first_name": "Repeat"},
            education=[],
            work_experience=[{"job_title": "Python Developer"}]
        )
        mock_match.return_value = [("Python Developer", 0.5), ("Python Developer", 0.6)]

        response = self.client.get("/job_recommendation/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        jobs = response.json()["recommended_jobs"]
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["job_title"], "Python Developer")
