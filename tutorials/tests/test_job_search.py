import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from tutorials.models.accounts import CustomUser, CompanyUser
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

        # Create a company
        self.company = CompanyUser.objects.create(company_name='Tech Corp')

        # Create sample job postings
        self.job1 = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,  # Associate the job posting with the company
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
            company=self.company,  # Associate the job posting with the company
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

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
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

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company=self.company,  # Associate the job posting with the company
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
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_with_no_user_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    
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

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
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

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company=self.company,  # Associate the job posting with the company
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
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_with_no_user_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_location(self):
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_industry_and_no_location(self):
        self.user.user_industry = []
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)


    def test_job_recommendation_with_empty_job_postings(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_multiple_locations(self):
        self.user.user_location = 'New York, San Francisco'
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

    def test_job_recommendation_with_no_matching_jobs(self):
        self.user.user_location = 'London'
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

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

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
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

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company=self.company,  # Associate the job posting with the company
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
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_with_no_user_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

   
    def test_job_recommendation_with_no_location(self):
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_industry_and_no_location(self):
        self.user.user_industry = []
        self.user.user_location = ''
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

   

    def test_job_recommendation_with_empty_job_postings(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_multiple_locations(self):
        self.user.user_location = 'New York, San Francisco'
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

    def test_job_recommendation_with_no_matching_jobs(self):
        self.user.user_location = 'London'
        self.user.save()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

  

  
    def test_job_recommendation_with_no_required_skills_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='',  # No required skills
            preferred_skills='JavaScript, React',
            education_required='Bachelor’s degree in Computer Science',
            perks='Health insurance, 401(k)',
            company_overview='A leading tech company.',
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_preferred_skills_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='Python, Django',
            preferred_skills='',  # No preferred skills
            education_required='Bachelor’s degree in Computer Science',
            perks='Health insurance, 401(k)',
            company_overview='A leading tech company.',
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_education_required_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='Python, Django',
            preferred_skills='JavaScript, React',
            education_required='',  # No education required
            perks='Health insurance, 401(k)',
            company_overview='A leading tech company.',
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_perks_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='Python, Django',
            preferred_skills='JavaScript, React',
            education_required='Bachelor’s degree in Computer Science',
            perks='',  # No perks
            company_overview='A leading tech company.',
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_company_overview_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
            location='New York',
            salary_range='2000',
            contract_type='Full-time',
            job_overview='Develop and maintain software applications.',
            roles_responsibilities='Code, test, and deploy software.',
            required_skills='Python, Django',
            preferred_skills='JavaScript, React',
            education_required='Bachelor’s degree in Computer Science',
            perks='Health insurance, 401(k)',
            company_overview='',  # No company overview
            why_join_us='Innovative environment.',
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_why_join_us_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
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
            why_join_us='',  # No why join us
            company_reviews='5'
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_no_company_reviews_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
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
            company_reviews=''  # No company reviews
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

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

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
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

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company=self.company,  # Associate the job posting with the company
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
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_with_no_user_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

   
  
  
  



   


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

    def test_job_recommendation_no_jobs(self):
        JobPosting.objects.all().delete()
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_empty_industry(self):
        self.user.user_industry = []
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

    def test_job_recommendation_with_duplicate_jobs(self):
        for _ in range(5):
            JobPosting.objects.create(
                job_title='Software Engineer',
                company=self.company,  # Associate the job posting with the company
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
                company_reviews=5  # Ensure company_reviews is a number
            )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

    def test_job_recommendation_with_ajax_request(self):
        request = self.factory.get('/job-recommendation/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_job_recommendation_with_no_user_cv(self):
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

   
    
    

  
   
    def test_job_recommendation_with_no_company_reviews_in_job(self):
        job = JobPosting.objects.create(
            job_title='Software Engineer',
            company=self.company,
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
            company_reviews=None  # No company reviews
        )
        request = self.factory.get('/job-recommendation/')
        request.user = self.user
        response = job_recommendation(request)
        self.assertEqual(response.status_code, 200)

  

 
