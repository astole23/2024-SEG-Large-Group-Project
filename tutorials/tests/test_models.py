from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import os
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from tutorials.models.accounts import CustomUser, NormalUser, CompanyUser
from tutorials.models.company_review import Review
from tutorials.models.jobposting import JobPosting
from tutorials.models.standard_cv  import CVApplication




import os
import string

class CustomUserModelTests(TestCase):

    def setUp(self):
        # Common setup for all tests
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }

    # Test 1: Create a normal user
    def test_create_normal_user(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_company)

    # Test 2: Create a superuser
    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(**self.user_data)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    # Test 3: Create a company user
    def test_create_company_user(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertTrue(company.is_company)
        self.assertEqual(company.company_name, 'Test Corp')

   
  

    # Test 6: Normal user should not have a unique ID
    def test_normal_user_no_unique_id(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.unique_id)

    # Test 7: Company user with existing unique ID
    def test_company_user_with_existing_unique_id(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp', 'unique_id': 'EXISTING1'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertEqual(company.unique_id, 'EXISTING1')

    # Test 8: Company user without company name
    def test_company_user_without_company_name(self):
        company_data = {**self.user_data, 'is_company': True}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.company_name)

  

    # Test 10: Normal user with phone number
    def test_normal_user_with_phone(self):
        user_data = {**self.user_data, 'phone': '+1234567890'}
        user = CustomUser.objects.create_user(**user_data)
        self.assertEqual(user.phone, '+1234567890')

    # Test 11: Company user with phone number
    def test_company_user_with_phone(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp', 'phone': '+1234567890'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertEqual(company.phone, '+1234567890')

    # Test 12: Normal user without phone number
    def test_normal_user_without_phone(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.phone)

    # Test 13: Company user without phone number
    def test_company_user_without_phone(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.phone)

    # Test 14: Normal user string representation
    def test_normal_user_str(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    # Test 15: Company user string representation
    def test_company_user_str(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertEqual(str(company), 'Test Corp')

    # Test 16: Company user without company name string representation
    def test_company_user_without_company_name_str(self):
        company_data = {**self.user_data, 'is_company': True}
        company = CustomUser.objects.create_user(**company_data)
        self.assertEqual(str(company), 'testuser')

    # Test 17: Normal user proxy model
    def test_normal_user_proxy_model(self):
        user = NormalUser.objects.create_user(**self.user_data)
        self.assertFalse(user.is_company)
        self.assertEqual(user._meta.verbose_name, 'User')

    # Test 18: Company user proxy model
    def test_company_user_proxy_model(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertTrue(company.is_company)
        self.assertEqual(company._meta.verbose_name, 'Company')

    # Test 19: Normal user proxy model string representation
    def test_normal_user_proxy_str(self):
        user = NormalUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')

    # Test 20: Company user proxy model string representation
    def test_company_user_proxy_str(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertEqual(str(company), 'Test Corp')

    # Test 21: Normal user proxy model without phone
    def test_normal_user_proxy_without_phone(self):
        user = NormalUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.phone)

    # Test 22: Company user proxy model with phone
    def test_company_user_proxy_with_phone(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp', 'phone': '+1234567890'}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertEqual(company.phone, '+1234567890')

    # Test 23: Normal user proxy model with phone
    def test_normal_user_proxy_with_phone(self):
        user_data = {**self.user_data, 'phone': '+1234567890'}
        user = NormalUser.objects.create_user(**user_data)
        self.assertEqual(user.phone, '+1234567890')

    # Test 24: Company user proxy model without company name
    def test_company_user_proxy_without_company_name(self):
        company_data = {**self.user_data, 'is_company': True}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertIsNone(company.company_name)

    # Test 25: Normal user proxy model with all fields
    def test_normal_user_proxy_with_all_fields(self):
        user_data = {**self.user_data, 'phone': '+1234567890', 'first_name': 'John', 'last_name': 'Doe'}
        user = NormalUser.objects.create_user(**user_data)
        self.assertEqual(user.phone, '+1234567890')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

  

    # Test 27: Normal user proxy model with email
    def test_normal_user_proxy_with_email(self):
        user = NormalUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')

    # Test 28: Company user proxy model with email
    def test_company_user_proxy_with_email(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertEqual(company.email, 'test@example.com')

    # Test 29: Normal user proxy model with password
    def test_normal_user_proxy_with_password(self):
        user = NormalUser.objects.create_user(**self.user_data)
        self.assertTrue(user.check_password('testpassword123'))

    # Test 30: Company user proxy model with password
    def test_company_user_proxy_with_password(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CompanyUser.objects.create_user(**company_data)
        self.assertTrue(company.check_password('testpassword123'))

    def tearDown(self):
        # Clean up any files created during the tests
        for user in CustomUser.objects.all():
            if user.logo:
                if os.path.isfile(user.logo.path):
                    os.remove(user.logo.path)

class CustomUserModelAdditionalTests(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }

   


    # Test 33: Ensure phone number is optional
    def test_phone_optional(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.phone)

    # Test 34: Ensure phone number can be saved
    def test_phone_saved(self):
        user_data = {**self.user_data, 'phone': '+1234567890'}
        user = CustomUser.objects.create_user(**user_data)
        self.assertEqual(user.phone, '+1234567890')

    # Test 35: Ensure company name is optional for company users
    def test_company_name_optional(self):
        company_data = {**self.user_data, 'is_company': True}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.company_name)

    # Test 36: Ensure industry is optional for company users
    def test_industry_optional(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.industry)

    # Test 37: Ensure location is optional for company users
    def test_location_optional(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.location)

   
    # Test 39: Ensure description is optional for company users
    def test_description_optional(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertIsNone(company.description)

    # Test 40: Ensure unique ID is not generated for normal users
    def test_unique_id_not_generated_for_normal_users(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.unique_id)

    # Test 41: Ensure unique ID is generated only once for company users
    def test_unique_id_generated_once(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp'}
        company = CustomUser.objects.create_user(**company_data)
        original_unique_id = company.unique_id
        company.save()  # Save again to ensure unique ID doesn't change
        self.assertEqual(company.unique_id, original_unique_id)

    # Test 42: Ensure unique ID is not overwritten if manually set
    def test_unique_id_not_overwritten(self):
        company_data = {**self.user_data, 'is_company': True, 'company_name': 'Test Corp', 'unique_id': 'CUSTOM123'}
        company = CustomUser.objects.create_user(**company_data)
        self.assertEqual(company.unique_id, 'CUSTOM123')


    # Test 45: Ensure company name is not required for normal users
    def test_company_name_not_required_for_normal_users(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.company_name)

    # Test 46: Ensure industry is not required for normal users
    def test_industry_not_required_for_normal_users(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.industry)

    # Test 47: Ensure location is not required for normal users
    def test_location_not_required_for_normal_users(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.location)

   

    # Test 49: Ensure description is not required for normal users
    def test_description_not_required_for_normal_users(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertIsNone(user.description)

    # Test 50: Ensure proxy models inherit from CustomUser
    def test_proxy_model_inheritance(self):
        self.assertTrue(issubclass(CompanyUser, CustomUser))
        self.assertTrue(issubclass(NormalUser, CustomUser))

    def tearDown(self):
        # Clean up any files created during the tests
        for user in CustomUser.objects.all():
            if user.logo:
                if os.path.isfile(user.logo.path):
                    os.remove(user.logo.path)





class ReviewModelTests(TestCase):

    

    # Test review with empty text (should fail)
    def test_create_review_with_empty_text(self):
        review = Review(text="", rating=3)
        with self.assertRaises(ValidationError):
            review.full_clean()

   

    # Test review with rating below minimum (should fail)
    def test_create_review_with_rating_below_min(self):
        review = Review(text="Bad", rating=0)
        with self.assertRaises(ValidationError):
            review.full_clean()

    # Test review with rating above maximum (should fail)
    def test_create_review_with_rating_above_max(self):
        review = Review(text="Amazing", rating=6)
        with self.assertRaises(ValidationError):
            review.full_clean()

    # Test review string representation
    def test_review_str_representation(self):
        review = Review(text="This is a test review", rating=4)
        self.assertEqual(str(review), "Review (4/5): This is a test review")




   

    # Test review with rating as negative integer (should fail)
    def test_create_review_with_negative_rating(self):
        with self.assertRaises(ValidationError):
            review = Review(text="Test", rating=-1)
            review.full_clean()

    # Test review with rating as zero (should fail)
    def test_create_review_with_zero_rating(self):
        with self.assertRaises(ValidationError):
            review = Review(text="Test", rating=0)
            review.full_clean()

    # Test review with rating as six (should fail)
    def test_create_review_with_rating_as_six(self):
        with self.assertRaises(ValidationError):
            review = Review(text="Test", rating=6)
            review.full_clean()

    # Test review with rating as a large number (should fail)
    def test_create_review_with_large_rating(self):
        with self.assertRaises(ValidationError):
            review = Review(text="Test", rating=100)
            review.full_clean()

    # Test review with rating as a negative large number (should fail)
    def test_create_review_with_negative_large_rating(self):
        with self.assertRaises(ValidationError):
            review = Review(text="Test", rating=-100)
            review.full_clean()

   

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime






class CVApplicationTests(TestCase):

    def setUp(self):
        self.valid_cv_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        self.invalid_cv_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        self.large_cv_file = SimpleUploadedFile("large.pdf", b"x" * (1025 * 1024), content_type="application/pdf")


    # Test 2: Invalid email format
    def test_invalid_email(self):
        cv = CVApplication(
            full_name="John Doe",
            email="invalid-email",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 250,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.valid_cv_file
        )
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 3: Missing required fields
    def test_missing_required_fields(self):
        cv = CVApplication()
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 4: Invalid file extension
    def test_invalid_file_extension(self):
        cv = CVApplication(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 250,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.invalid_cv_file
        )
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 5: File size exceeds limit
    def test_file_size_exceeds_limit(self):
        cv = CVApplication(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 250,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.large_cv_file
        )
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 6: Motivation statement too short
    def test_motivation_statement_too_short(self):
        cv = CVApplication(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 249,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.valid_cv_file
        )
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 7: Motivation statement too long
    def test_motivation_statement_too_long(self):
        cv = CVApplication(
            full_name="John Doe",
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 501,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.valid_cv_file
        )
        with self.assertRaises(ValidationError):
            cv.full_clean()

    # Test 8: Full name derived from CV file name
    def test_full_name_derived_from_cv_file(self):
        cv = CVApplication(
            email="john.doe@example.com",
            phone="1234567890",
            address="123 Main St",
            postcode="12345",
            right_to_work=True,
            institution="University of Test",
            degree_type="Bachelor",
            field_of_study="Computer Science",
            expected_grade="First Class",
            start_date="2020-09-01",
            end_date="2024-06-30",
            employer_name="Test Corp",
            job_title="Software Engineer",
            work_start_date="2021-06-01",
            work_end_date="2021-08-31",
            responsibilities="Developed software",
            key_skills="Python, Django",
            technical_skills="Git, Docker",
            languages="English, Spanish",
            motivation_statement="a" * 250,
            fit_for_role="I fit well",
            career_aspirations="Become a senior developer",
            preferred_start_date="2024-07-01",
            internship_duration="6 months",
            willingness_to_relocate=True,
            reference_1_name="Jane Smith",
            reference_1_position="Manager",
            reference_1_company="Test Corp",
            reference_1_contact="jane.smith@example.com",
            cv_file=self.valid_cv_file
        )
        cv.save()
        self.assertEqual(cv.full_name, "test")


  
   