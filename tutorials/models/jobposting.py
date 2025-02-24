from django.db import models

class JobPosting(models.Model):
    """
    Model representing a job posting.
    """

    # Basic job details
    job_title = models.CharField(
        max_length=255,
        help_text="The title of the job posting."
    )
    company_name = models.CharField(
        max_length=255,
        help_text="The name of the company offering the job."
    )
    child_company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Child or subsidiary company name, if applicable."
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
    salary_range = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Salary offered for the job."
    )

    # Contract type (e.g., Full-time, Part-time, Contract)
    contract_type = models.CharField(
        max_length=50,
        help_text="Type of contract for the job."
    )

    # Job description and details
    job_overview = models.TextField(
        help_text="A brief overview of the job responsibilities and expectations."
    )
    roles_responsibilities = models.TextField(
        help_text="Detailed list of job responsibilities and duties."
    )

    # Required and preferred skills (stored as comma-separated values)
    required_skills = models.TextField(
        help_text="List of skills required for the job (comma-separated)."
    )
    preferred_skills = models.TextField(
        blank=True,
        null=True,
        help_text="List of preferred skills for the job (comma-separated)."
    )

    # Education and qualifications
    education_required = models.CharField(
        max_length=255,
        help_text="Minimum education level required for the job."
    )

    # Perks and benefits (as provided by the employer)
    perks = models.TextField(
        help_text="List of benefits and perks provided by the employer."
    )

    # Job application deadline (expects format 'YYYY-MM-DD')
<<<<<<< HEAD
    application_deadline = models.CharField(
        help_text="Deadline for submitting job applications.",
        max_length=255
=======

    application_deadline = models.CharField(
        help_text="Deadline for submitting job applications.",
        max_length=255

>>>>>>> 679a10d18f973b48e204d4b25ee73907734c3492
    )

    # Extra field: Required Documents for the application
    required_documents = models.TextField(
        blank=True,
        null=True,
        help_text="Documents required for application."
    )

    # Additional details about the company and the job offer
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

    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the job was posted."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the job details were last updated."
    )

    work_type = models.CharField(max_length=255, help_text="Type of work flexibility offered by the employer.")
    child_company_name = models.CharField(max_length=255, null = True, blank = True, help_text="Name of the child company.")
    required_documents = models.TextField(help_text="List of documents required for the job application.", default="Updated CV")

    def __str__(self):
        return f"{self.job_title} at {self.company_name} ({self.location})"
