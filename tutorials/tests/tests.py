from django.test import TestCase

from django.test import TestCase
from tutorials.models.accounts import Company, User
from django.core.exceptions import ValidationError

class CompanyModelTest(TestCase):
    def setUp(self):
        """Create a test company before each test."""
        self.company = Company.objects.create(
            company_name="Tech Innovators",
            email="contact@techinnovators.com",
            password="securepassword",
            industry="Technology",
            phone="123-456-7890"
        )

    def test_company_creation(self):
        """Test if the company instance is created successfully."""
        self.assertEqual(self.company.company_name, "Tech Innovators")
        self.assertEqual(self.company.email, "contact@techinnovators.com")
        self.assertEqual(self.company.industry, "Technology")
        self.assertEqual(self.company.phone, "123-456-7890")

    def test_company_str_method(self):
        """Test the __str__ method returns the company name."""
        self.assertEqual(str(self.company), "Tech Innovators")

    def test_company_email_unique(self):
        """Test that the email field enforces uniqueness."""
        with self.assertRaises(Exception):  # Email is unique
            Company.objects.create(
                company_name="Duplicate Tech",
                email="contact@techinnovators.com",  # Duplicate email
                password="anotherpassword",
                industry="IT",
                phone="987-654-3210"
            )

class UserModelTest(TestCase):
    def setUp(self):
        """Create a test user before each test."""
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword",
            phone="555-555-5555"
        )

    def test_user_creation(self):
        """Test if the user instance is created successfully."""
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.email, "john.doe@example.com")
        self.assertEqual(self.user.phone, "555-555-5555")

    def test_user_str_method(self):
        """Test the __str__ method returns 'First Name Last Name'."""
        self.assertEqual(str(self.user), "John Doe")

    def test_user_email_unique(self):
        """Test that the email field enforces uniqueness."""
        with self.assertRaises(Exception):  # Email is unique
            User.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="john.doe@example.com",  # Duplicate email
                password="anotherpassword",
                phone="444-444-4444"
            )


###



class CompanyModelTest(TestCase):

    def setUp(self):
        """Create a test company before each test."""
        self.company = Company.objects.create(
            company_name="Tech Innovators",
            email="contact@techinnovators.com",
            password="securepassword",
            industry="Technology",
            phone="123-456-7890"
        )

    def test_company_creation(self):
        """Test if the company instance is created successfully."""
        self.assertEqual(self.company.company_name, "Tech Innovators")
        self.assertEqual(self.company.email, "contact@techinnovators.com")
        self.assertEqual(self.company.industry, "Technology")
        self.assertEqual(self.company.phone, "123-456-7890")

    def test_company_str_method(self):
        """Test the __str__ method returns the company name."""
        self.assertEqual(str(self.company), "Tech Innovators")

    def test_company_email_unique(self):
        """Test that the email field enforces uniqueness."""
        with self.assertRaises(Exception):  # Email should be unique
            Company.objects.create(
                company_name="Duplicate Tech",
                email="contact@techinnovators.com",  # Duplicate email
                password="anotherpassword",
                industry="IT",
                phone="987-654-3210"
            )

    def test_invalid_email(self):
        """Test if invalid emails raise an error."""
        company = Company(
            company_name="Invalid Email Corp",
            email="invalid-email",  # Invalid email format
            password="testpassword",
            industry="Retail",
            phone="987-654-3210"
        )
        with self.assertRaises(ValidationError):
            company.full_clean()  # Triggers model validation

    def test_blank_fields_not_allowed(self):
        """Test that required fields cannot be blank."""
        company = Company(
            company_name="",
            email="",
            password="",
            industry="Technology",
            phone="1234567890"
        )
        with self.assertRaises(ValidationError):
            company.full_clean()  # Triggers validation

class UserModelTest(TestCase):

    def setUp(self):
        """Create a test user before each test."""
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="securepassword",
            phone="555-555-5555"
        )

    def test_user_creation(self):
        """Test if the user instance is created successfully."""
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.email, "john.doe@example.com")
        self.assertEqual(self.user.phone, "555-555-5555")

    def test_user_str_method(self):
        """Test the __str__ method returns 'First Name Last Name'."""
        self.assertEqual(str(self.user), "John Doe")

  