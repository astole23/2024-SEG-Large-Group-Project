from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import os

# Validate file size
def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

class CVApplication(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postcode = models.CharField(max_length=20)
    
    # Right to Work
    right_to_work = models.BooleanField()  # True for Yes, False for No
    visa_details = models.TextField(blank=True, null=True)  # If applicable
    
    # Education
    institution = models.CharField(max_length=255)
    degree_type = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    expected_grade = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    relevant_modules = models.TextField(blank=True, null=True)
    
    # Work Experience
    employer_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    work_start_date = models.DateField()
    work_end_date = models.DateField()
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
    preferred_start_date = models.DateField()
    internship_duration = models.CharField(max_length=50)
    willingness_to_relocate = models.BooleanField()
    
    # References (At least one, second is optional)
    reference_1_name = models.CharField(max_length=255)
    reference_1_position = models.CharField(max_length=255)
    reference_1_company = models.CharField(max_length=255)
    reference_1_contact = models.CharField(max_length=255)
    reference_2_name = models.CharField(max_length=255, blank=True, null=True)
    reference_2_position = models.CharField(max_length=255, blank=True, null=True)
    reference_2_company = models.CharField(max_length=255, blank=True, null=True)
    reference_2_contact = models.CharField(max_length=255, blank=True, null=True)
    
    # Optional Equal Opportunities Monitoring
    equal_opportunities_monitoring = models.TextField(blank=True, null=True)
    
    # CV Upload
    cv_file = models.FileField(
        upload_to='uploads/cvs/', 
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )

    # AI-Extracted Resume Data
    structured_experience_education = models.TextField(blank=True, null=True)
    structured_skills = models.TextField(blank=True, null=True)
    structured_projects = models.TextField(blank=True, null=True)
    structured_languages = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = os.path.splitext(self.cv_file.name)[0]
        super(CVApplication, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.full_name
