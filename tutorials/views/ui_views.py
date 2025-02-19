from django.shortcuts import render
from tutorials.forms import UserRegistrationForm, CompanyRegistrationForm

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    user_form = UserRegistrationForm()
    company_form = CompanyRegistrationForm()
    return render(request, 'signup.html', {'user_form': user_form, 'company_form': company_form})

def login(request):
    return render(request, 'login.html')

def guest(request):
    return render(request, 'guest.html')

def user_dashboard(request):
    return render(request, 'user_dashboard.html')

def about_us(request):
    return render(request, 'about_us.html')

def settings(request):
    return render(request, 'settings.html')

def base_content(request):
    return render(request, 'base_content.html')




"""
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


def signup_view(request):
    company_form = CompanyRegistrationForm()
    user_form = UserRegistrationForm()
    if request.method == "POST":

        user_type = request.POST.get("user_type")
     
        if user_type == "company":
            company_form = CompanyRegistrationForm(request.POST)
            if company_form.is_valid():
                company_form.save()
                messages.success(request, "Company registered successfully!")
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


    company_form = CompanyRegistrationForm()
    user_form = UserRegistrationForm()

    if request.method == "POST":
        user_type = request.POST.get("user_type")

        if user_type == "company":
            company_form = CompanyRegistrationForm(request.POST)
            if company_form.is_valid():
                company_form.save()
                messages.success(request, "Company registered successfully!")
                return redirect("login")  # Redirect to login page
            else:
                messages.error(request, "Company registration failed.")

        elif user_type == "user":
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "User registered successfully!")
                return redirect("login")  # Redirect to login page
            else:
                messages.error(request, "User registration failed.")

    return render(request, "signup.html", {"company_form": company_form, "user_form": user_form})


    if request.method == 'POST':
        print("Form submitted:", request.POST)  # Debug: Print the submitted data
        user_type = request.POST.get('user_type')

        if user_type == 'company':
            form = CompanyRegistrationForm(request.POST)
            if form.is_valid():
                company = form.save(commit=False)
                print("Form is valid. Data:", form.cleaned_data)  # Debug: Log valid data
                company.password = make_password(form.cleaned_data['password'])  # Hash password
                company.save()
                print("Company saved:", company)  # Debug: Confirm saving
                messages.success(request, "Company registered successfully!")
                return redirect('login')  # Adjust to your login URL
            else:
                print("Company form errors:", form.errors)  # Debug: Log form errors
                messages.error(request, "Error in company signup form!")

        elif user_type == 'user':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                print("Form is valid. Data:", form.cleaned_data)  # Debug: Log valid data
                user.password = make_password(form.cleaned_data['password'])  # Hash password
                user.save()
                print("User saved:", user)  # Debug: Confirm saving
                messages.success(request, "User registered successfully!")
                return redirect('login')  # Adjust to your login URL
            else:
                print("User form errors:", form.errors)  # Debug: Log form errors
                messages.error(request, "Error in user signup form!")

    company_form = CompanyRegistrationForm()
    user_form = UserRegistrationForm()
    return render(request, 'signup.html', {'company_form': company_form, 'user_form': user_form})
"""