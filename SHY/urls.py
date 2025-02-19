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
from tutorials.views import ui_views 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ui_views.guest, name='guest'),
    path('employer_dashboard/', ui_views.employer_dashboard, name='employer_dashboard'),
    path('contact_us/', ui_views.contact_us, name='contact_us'),
   
    path('login/', ui_views.login, name='login'),
    path('user_dashboard/', ui_views.user_dashboard, name='user_dashboard'),
    path('signup/', ui_views.signup, name='signup'),
 
    
    path('about_us/', ui_views.about_us, name='about_us'),
    path('settings/', ui_views.settings, name='settings'),
] 
