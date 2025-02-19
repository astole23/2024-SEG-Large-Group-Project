from django.conf import settings
from django.shortcuts import redirect


def user_type_redirect(email):
     from tutorials.models.accounts import Company, User

     """ Redirects a user based on whether they are a company or individual user"""

     if Company.objects.filter(email=email).exists():
            return redirect('company_dashboard')
     elif User.objects.filter(email=email).exists():
           return redirect('user_dashboard')
     else:
           return redirect('guest')