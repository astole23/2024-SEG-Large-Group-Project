from django.shortcuts import render

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

def guest(request):
    return render(request, 'guest.html')

def user_dashboard(request):
    return render(request, 'user_dashboard.html')

def about_us(request):
    return render(request, 'about_us.html')




####
from django.shortcuts import render, redirect
from django.contrib import messages
from tutorials.forms import CompanyRegistrationForm, UserRegistrationForm
from tutorials.models.accounts import Company, User
from django.contrib.auth.hashers import make_password

from django.shortcuts import render, redirect
from django.contrib import messages


from django.shortcuts import render, redirect
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def signup_view(request):
    company_form = CompanyRegistrationForm()
    user_form = UserRegistrationForm()
    
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        
        if user_type == "company":
            company_form = CompanyRegistrationForm(request.POST)
            if company_form.is_valid():
                company = company_form.save()  # Save the company instance
                company_id = company.unique_id  # Get the unique_id of the created company

                # Send an email with the unique ID
                subject = "Welcome to our platform!"
                message = f"Dear {company.company_name},\n\nYour company has been successfully registered.\nYour unique company ID is: {company_id}\n\nThank you for joining us!"
                from_email = settings.DEFAULT_FROM_EMAIL  # Ensure that you have set DEFAULT_FROM_EMAIL in your settings
                recipient_list = [company.email]

                # Send the email
                send_mail(subject, message, from_email, recipient_list)

                messages.success(request, "Company registered successfully! An email has been sent with the company ID.")
                return redirect("employer_dashboard")
            else:
                messages.error(request, "Error in company signup form.")

        elif user_type == "user":
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "User registered successfully!")
                return redirect("user_dashboard")
            else:
                messages.error(request, "Error in user signup form.")

    return render(request, "signup.html", {"company_form": company_form, "user_form": user_form})


   