from django.db import models
from django.conf import settings

class JobPosting(models.Model):
    job_title = models.CharField(
        max_length=255,
        help_text="The title of the job posting."
    )
    # Link directly to the company account that created the posting.
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_postings',
        help_text="The company posting the job (must be a company account).",
        null=True,  # Allow null values temporarily
        blank=True  # Allow form submissions without this field
    )


    company_name = models.CharField(max_length=255, editable=False)
    
    child_company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the child company."
    )
    location = models.CharField(
        max_length=255,
        help_text="Location of the job (e.g., city, country, or remote)."
    )
    work_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type of work (e.g., remote, hybrid, on-site).",
        choices=[
            ('remote', 'Remote'),
            ('hybrid', 'Hybrid'),
            ('on_site', 'On-site'),
        ]
    )
    salary_range = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Salary offered for the job."
    )
    contract_type = models.CharField(
        max_length=50,
        help_text="Type of contract for the job."
    )
    job_overview = models.TextField(
        help_text="A brief overview of the job responsibilities and expectations."
    )
    roles_responsibilities = models.TextField(
        help_text="Detailed list of job responsibilities and duties."
    )
    required_skills = models.TextField(
        help_text="List of skills required for the job (comma-separated)."
    )
    preferred_skills = models.TextField(
        blank=True,
        null=True,
        help_text="List of preferred skills for the job (comma-separated)."
    )
    education_required = models.CharField(
        max_length=255,
        help_text="Minimum education level required for the job."
    )
    perks = models.TextField(
        help_text="List of benefits and perks provided by the employer."
    )
    application_deadline = models.CharField(
        help_text="Deadline for submitting job applications.",
        max_length=255
    )
    required_documents = models.TextField(
        help_text="List of documents required for the job application.",
        default="Updated CV"
    )
    company_overview = models.TextField(
        blank=True,
        null=True,
        help_text="Brief information about the company."
    )
    why_join_us = models.TextField(
        blank=True,
        null=True,
        help_text="Reasons why candidates should apply for this job."
    )
    company_reviews = models.FloatField(
        blank=True,
        null=True,
        help_text="Average review rating of the company."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the job was posted."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the job details were last updated."
    )

    def __str__(self):
        # If you decide to remove company_name, you can display company.company_name or company.username.
        return f"{self.job_title} at {self.company.company_name if self.company.company_name else self.company.username} ({self.location})"
