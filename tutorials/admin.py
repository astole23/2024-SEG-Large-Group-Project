from django.contrib import admin
from .models.jobposting import JobPosting  # Import the JobPosting model
from .models.accounts import User, Company  # Import the User and Company models


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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'email',
        'industry',
        'phone',
    )  # Fields displayed in the admin list view
    list_filter = ('industry',)  # Filter companies by industry
    search_fields = (
        'company_name',
        'email',
        'industry',
    )  # Fields searchable in the admin
    ordering = ('company_name',)  # Default ordering


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'phone',
    )  # Fields displayed in the admin list view
    search_fields = (
        'first_name',
        'last_name',
        'email',
    )  # Fields searchable in the admin
    ordering = ('first_name', 'last_name')  # Default ordering
    