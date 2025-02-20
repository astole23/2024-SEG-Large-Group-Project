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
<<<<<<< HEAD
from tutorials.views import ui_views 
=======
from tutorials.views import views 
from django.conf import settings
from django.conf.urls.static import static
>>>>>>> 0133cc1a2efbfe9ddc9d7cc0df321f543b3f298b


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ui_views.guest, name='guest'),
    path('employer_dashboard/', ui_views.employer_dashboard, name='employer_dashboard'),
    path('contact_us/', ui_views.contact_us, name='contact_us'),
   
    path('login/', ui_views.login, name='login'),
    path('user_dashboard/', ui_views.user_dashboard, name='user_dashboard'),
    path('signup/', ui_views.signup, name='signup'),
 
    
<<<<<<< HEAD
    path('about_us/', ui_views.about_us, name='about_us'),
    path('settings/', ui_views.settings, name='settings'),

    path('base_content/', ui_views.base_content, name='base_content'),
=======
    path('about_us/', views.about_us, name='about_us'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'),
    path('company/<int:company_id>/review/', views.leave_review, name='leave_review'),
    path('company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('settings/', views.settings, name='settings'),
>>>>>>> 0133cc1a2efbfe9ddc9d7cc0df321f543b3f298b
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)