from django.contrib import admin
from .models.jobposting import JobPosting  # Import the JobPosting model

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'job_title',
        'company_name',
        'location',
        'salary_range',
        'contract_type',
        'application_deadline',
    )  # Fields displayed in the admin list view
    list_filter = (
        'contract_type',
        'location',
        'company_name',
    )  # Filters for the right-hand sidebar
    search_fields = (
        'job_title',
        'company_name',
        'location',
    )  # Fields searchable in the admin
    ordering = ('-application_deadline',)  # Default ordering
    readonly_fields = ('created_at', 'updated_at')  # Fields that cannot be edited
