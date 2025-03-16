from django.contrib import admin
from django.contrib.auth import get_user_model
from tutorials.models.jobposting import JobPosting
from tutorials.models.standard_cv import CVApplication
from tutorials.models.applications import JobApplication, Notification


CustomUser = get_user_model()

# Register JobPosting as before.
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        'job_title',
        'company_name',
        'location',
        'salary_range',
        'contract_type',
        'application_deadline',
    )
    list_filter = (
        'contract_type',
        'location',
        'company_name',
    )
    search_fields = (
        'job_title',
        'company_name',
        'location',
    )
    ordering = ('-application_deadline',)
    readonly_fields = ('created_at', 'updated_at')


from tutorials.models.accounts import CompanyUser, NormalUser

@admin.register(CompanyUser)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'email',
        'industry',
        'phone',
    )
    list_filter = ('industry',)
    search_fields = (
        'company_name',
        'email',
        'industry',
    )
    ordering = ('company_name',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ensure that only users marked as companies appear here.
        return qs.filter(is_company=True)

@admin.register(NormalUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 
        'first_name',
        'last_name',
        'email',
        'phone',
    )
    search_fields = (
        'username', 
        'first_name',
        'last_name',
        'email',
    )
    ordering = ('username', 'first_name', 'last_name')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show users that are not companies.
        return qs.filter(is_company=False)


admin.site.register(JobApplication)
admin.site.register(Notification)