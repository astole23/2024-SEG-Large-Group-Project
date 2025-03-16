from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import os
import fitz  # PyMuPDF
import together
from dotenv import load_dotenv
import json
from django.conf import settings

# Load your API key from environment

load_dotenv() 
api_key = os.getenv("TOGETHER_API_KEY")  # ✅ Match your .env variable name



# ------------------------------
# Utility functions
# ------------------------------

def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

def extract_text_from_pdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def classify_resume_with_together(text):
    prompt = f"""
You are an AI trained to summarise resumes into clearly defined sections.

Provide a structured JSON output like this:
{{
    "Experience & Education": "Summarize work and educational background.",
    "Skills": "List key skills and competencies.",
    "Projects": "Summarize important projects.",
    "Languages": "List languages spoken."
}}

Only use information directly from the resume. Do not guess or make assumptions.

Resume text:
{text}

JSON Output:
"""

    response = together.Complete.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        prompt=prompt,
        max_tokens=1500,
        temperature=0.1,
        api_key=api_key  # ensure this is passed
    )

    return response["choices"][0]["text"]


# ------------------------------
# Main Model
# ------------------------------

class CVApplication(models.Model):
    # Personal Information
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postcode = models.CharField(max_length=20)

    # Right to Work
    right_to_work = models.BooleanField(null = True)
    visa_details = models.TextField(blank=True, null=True)

    # Education
    institution = models.CharField(max_length=255)
    degree_type = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    expected_grade = models.CharField(max_length=50)
    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)
    relevant_modules = models.TextField(blank=True, null=True)

    # Work Experience
    employer_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    work_start_date = models.DateField(null = True)
    work_end_date = models.DateField(null = True)
    responsibilities = models.TextField()

    # Skills
    key_skills = models.TextField()
    technical_skills = models.TextField()
    languages = models.TextField()

    # Motivation
    motivation_statement = models.TextField(validators=[MinLengthValidator(250), MaxLengthValidator(500)])
    fit_for_role = models.TextField()
    career_aspirations = models.TextField()

    # Availability
    preferred_start_date = models.DateField(null = True)
    internship_duration = models.CharField(max_length=50)
    willingness_to_relocate = models.BooleanField(null = True)

    # References
    reference_1_name = models.CharField(max_length=255)
    reference_1_position = models.CharField(max_length=255)
    reference_1_company = models.CharField(max_length=255)
    reference_1_contact = models.CharField(max_length=255)
    reference_2_name = models.CharField(max_length=255, blank=True, null=True)
    reference_2_position = models.CharField(max_length=255, blank=True, null=True)
    reference_2_company = models.CharField(max_length=255, blank=True, null=True)
    reference_2_contact = models.CharField(max_length=255, blank=True, null=True)

    # Equal Opportunities
    equal_opportunities_monitoring = models.TextField(blank=True, null=True)

    # File Upload
    cv_file = models.FileField(
        upload_to='uploads/cvs/',
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )

    # AI fields
    structured_experience_education = models.TextField(blank=True, null=True)
    structured_skills = models.TextField(blank=True, null=True)
    structured_projects = models.TextField(blank=True, null=True)
    structured_languages = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.full_name and self.cv_file:
            self.full_name = os.path.splitext(self.cv_file.name)[0]

        # Run Together AI extraction if CV is uploaded
        if self.cv_file:
            try:
                pdf_path = self.cv_file.path
                pdf_text = extract_text_from_pdf(pdf_path)
                structured = classify_resume_with_together(pdf_text)
                structured_dict = json.loads(structured)

                self.structured_experience_education = structured_dict.get("Experience & Education", "")
                self.structured_skills = structured_dict.get("Skills", "")
                self.structured_projects = structured_dict.get("Projects", "")
                self.structured_languages = structured_dict.get("Languages", "")

            except Exception as e:
                print("❌ Error classifying resume:", e)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class UserCV(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    personal_info = models.JSONField(default=dict)
    key_skills = models.TextField(blank=True)
    technical_skills = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    interest = models.TextField(blank=True)
    fit_for_role = models.TextField(blank=True)
    aspirations = models.TextField(blank=True)
    education = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)


    def __str__(self):
        return f"{self.user.username}'s CV"