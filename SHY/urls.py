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
from tutorials.views import views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.guest, name='guest'),
    path('employer_dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('login/', views.login_view, name='login'),
    path('login/process/', views.process_login, name='process_login'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/process/', views.process_signup, name='process_signup'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('search/', views.search, name='search'),
    path('about_us/', views.about_us, name='about_us'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('company/<int:company_id>/review/', views.leave_review, name='leave_review'),
    path('company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('settings/', views.profile_settings, name='settings'),
    path('your-job-posting-endpoint/', views.create_job_posting, name='create_job_posting'),
    path('company/<int:company_id>/add_job/', views.create_job_posting, name='add_job_listing'),
    path('apply/step1/', views.apply_step1, name='apply_step1'),
    path('apply/step2/', views.apply_step2, name='apply_step2'),
    path('apply/step3/', views.apply_step3, name='apply_step3'),
    path('apply/step4/', views.apply_step4, name='apply_step4'),
    path('apply/success/', views.application_success, name='application_success'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)