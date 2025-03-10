"""
URL configuration for SHY project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tutorials.views import ui_views, function_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ui_views.guest, name='guest'),
    path('logout/', ui_views.user_logout, name='logout'),
    path('employer_dashboard/', ui_views.employer_dashboard, name='employer_dashboard'),
    path('contact_us/', ui_views.contact_us, name='contact_us'),
    path('login/', ui_views.login_view, name='login'),
    path('login/process/', function_views.process_login, name='process_login'),
    path('signup/', ui_views.signup_view, name='signup'),
    path('signup/process/', function_views.process_signup, name='process_signup'),
    path('user_dashboard/', ui_views.user_dashboard, name='user_dashboard'),
    path('search/', ui_views.search, name='search'),
    path('about_us/', ui_views.about_us, name='about_us'),
    path('company/<int:company_id>/', ui_views.company_detail, name='company_detail'),
    path('company/<int:company_id>/review/', ui_views.leave_review, name='leave_review'),
    path('company/<int:company_id>/edit/', ui_views.edit_company, name='edit_company'),
    path('settings/', ui_views.profile_settings, name='settings'),
    path('your-job-posting-endpoint/', ui_views.create_job_posting, name='create_job_posting'),
    path('company/<int:company_id>/add_job/', ui_views.create_job_posting, name='add_job_listing'),
    path('apply/start/<int:job_posting_id>/', ui_views.start_application, name='start_application'),
    path('apply/step1/', ui_views.apply_step1, name='apply_step1'),
    path('apply/step2/', ui_views.apply_step2, name='apply_step2'),
    path('apply/step3/', ui_views.apply_step3, name='apply_step3'),
    path('apply/step4/', ui_views.apply_step4, name='apply_step4'),
    path('apply/success/', ui_views.application_success, name='application_success'),
    path('notifications/', ui_views.notifications, name='notifications'),
    path('notifications/mark_read/<int:notification_id>/', ui_views.mark_notification_read, name='mark_notification_read'),
    # User applications
    path('user/applications/', ui_views.user_applications, name='user_applications'),
    path('user/applications/<int:application_id>/', ui_views.user_application_detail, name='user_application_detail'),

    # Company applications
    path('company/applications/', ui_views.company_applications, name='company_applications'),
    path('company/applications/<int:application_id>/', ui_views.company_application_detail, name='company_application_detail'),
    path('company/applications/update/<int:application_id>/<str:new_status>/', ui_views.update_application_status, name='update_application_status'),

    path('api/job_postings/', ui_views.job_postings_api, name='job_postings_api'),
    path('my_jobs/', ui_views.my_jobs, name='my_jobs'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)