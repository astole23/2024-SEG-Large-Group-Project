import random
import string

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from tutorials.models.jobposting import JobPosting

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_applications'
    )

    cover_letter = models.TextField(blank=True, null=True)
    job_answers = models.JSONField(blank=True, null=True)
    tracked = models.BooleanField(default=False)
    application_id = models.CharField(max_length=12, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.company.is_company:
            raise ValidationError("The selected company must be a company account.")
    

    def save(self, *args, **kwargs):
        self.full_clean()
        # Auto-generate a unique application ID if not provided
        if not self.application_id:
            allowed_chars = string.ascii_uppercase + string.digits
            self.application_id = ''.join(random.choices(allowed_chars, k=10))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Application {self.application_id} for {self.job_posting.job_title} by {self.applicant.username}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('application', 'Application'),
        ('job_update', 'Job Update'),
        ('general', 'General'),
    ]
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='general'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}"
