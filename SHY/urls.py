from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from tutorials.views import (
    auth_views, company_views, function_views, jobseeker_views, 
    search_views, job_applications_views, page_views, job_search
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication & User Management
    path('logout/', auth_views.user_logout, name='logout'),
    path('login/', auth_views.login_view, name='login'),
    path('login/process/', function_views.process_login, name='process_login'),
    path('signup/', auth_views.signup_view, name='signup'),
    path('signup/process/', function_views.process_signup, name='process_signup'),
    path('delete_account/', auth_views.delete_account, name='delete_account'),
    path('settings/', auth_views.profile_settings, name='settings'),

    # Company Views
    path('employer_dashboard/', company_views.employer_dashboard, name='employer_dashboard'),
    path('company/profile/', company_views.company_profile, name='company_profile'),
    path('company/<int:company_id>/', company_views.company_detail, name='company_detail'),
    path('company/<int:company_id>/review/', company_views.leave_review, name='leave_review'),
    path('company/<int:company_id>/edit/', company_views.edit_company, name='edit_company'),
    path('company/<int:company_id>/add_job/', company_views.create_job_posting, name='add_job_listing'),
    path('your-job-posting-endpoint/', company_views.create_job_posting, name='create_job_posting'),

    # Jobseeker Views
    path('user_dashboard/', jobseeker_views.user_dashboard, name='user_dashboard'),
    path('user/applications/', jobseeker_views.user_applications, name='user_applications'),
    path('user/applications/<int:application_id>/', jobseeker_views.user_application_detail, name='user_application_detail'),
    path('notifications/', jobseeker_views.notifications, name='notifications'),
    path('notifications/mark_read/<int:notification_id>/', jobseeker_views.mark_notification_read, name='mark_notification_read'),
    path('upload_cv/', jobseeker_views.upload_cv, name='upload_cv'),
    path('upload_raw_cv/', jobseeker_views.upload_raw_cv, name='upload_raw_cv'),
    path('upload_user_document/', jobseeker_views.get_user_documents, name="upload_user_document"),
    path('delete_user_document/', jobseeker_views.delete_user_document, name="delete_user_document"),
    path('delete_raw_cv/', jobseeker_views.delete_raw_cv, name='delete_raw_cv'),
    path('add-job-by-code/', jobseeker_views.add_job_by_code, name='add_job_by_code'),
    path('my_jobs/', jobseeker_views.my_jobs, name='my_jobs'),

    # Page Views & Legal Pages 
    path('', page_views.guest, name='guest'),
    path('contact_us/', page_views.contact_us, name='contact_us'),
    path('about_us/', page_views.about_us, name='about_us'),
    path('terms_conditions/', page_views.terms_conditions, name='terms_conditions'),
    path('privacy/', page_views.privacy, name='privacy'),
    path('user_agreement/', page_views.user_agreement, name='user_agreement'),
    path('faq/', page_views.faq, name='faq'),
    path('help_centre/', page_views.help_centre, name='help_centre'),
    path('accessibility/', page_views.accessibility, name='accessibility'),

    # Job Search & Applications
    path('search/', search_views.search, name='search'),
    path('apply/start/<int:job_posting_id>/', job_applications_views.start_application, name='start_application'),
    path('apply/step1/', job_applications_views.apply_step1, name='apply_step1'),
    path('apply/step2/', job_applications_views.apply_step2, name='apply_step2'),
    path('apply/step3/', job_applications_views.apply_step3, name='apply_step3'),
    path('apply/step4/', job_applications_views.apply_step4, name='apply_step4'),
    path('apply/success/', job_applications_views.application_success, name='application_success'),

    # Company Job Applications Management 
    path('company/applications/', company_views.company_applications, name='company_applications'),
    path('company/applications/<int:application_id>/', company_views.company_application_detail, name='company_application_detail'),
    path('company/applications/update/<int:application_id>/<str:new_status>/', company_views.update_application_status, name='update_application_status'),

    # APIs & Other Features 
    path('api/job_postings/', search_views.job_postings_api, name='job_postings_api'),
    path('api/tracked-jobs/', search_views.tracked_jobs_api, name='tracked_jobs_api'),
    path('job_recommendation/', job_search.job_recommendation, name='job_recommendations'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
