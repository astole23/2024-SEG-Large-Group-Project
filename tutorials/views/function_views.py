from django.shortcuts import render, redirect
from tutorials.forms import UserLoginForm, CompanyLoginForm, CompanySignUpForm, UserSignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.contrib.auth.decorators import login_required

def process_login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'company':
            form = CompanyLoginForm(request=request, data=request.POST, prefix='company')
        else:
            form = UserLoginForm(request=request, data=request.POST, prefix='user')
        
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_company:
                return redirect('edit_company', company_id=user.id)
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            # Pass the form with errors for the correct user type.
            if user_type == 'company':
                return render(request, 'login.html', {
                    'company_form': form,
                    'user_form': UserLoginForm(prefix='user')
                })
            else:
                return render(request, 'login.html', {
                    'user_form': form,
                    'company_form': CompanyLoginForm(prefix='company')
                })
    else:
        return render(request, 'login.html', {
            'user_form': UserLoginForm(prefix='user'),
            'company_form': CompanyLoginForm(prefix='company')
        })


def process_signup(request):
    """
    Process signup for both user types based on a hidden input in the form.
    """
    if request.method == "POST":
        user_type = request.POST.get("user_type")

        if user_type == "company":
            form = CompanySignUpForm(request.POST, prefix='company')
            if form.is_valid():
                form.save()
                
                messages.success(request, "Company registered successfully!")
                return redirect("employer_dashboard")
            else:
                messages.error(request, "Error in company signup form.")
                company_form = form  # Keep the data user just submitted
                user_form = UserSignUpForm(prefix='user')
        elif user_type == "user":
            form = UserSignUpForm(request.POST, prefix='user')
            if form.is_valid():
                user = form.save(commit=False)
                user.user_industry = form.cleaned_data['user_industry']  # Store as JSON list
                user.user_location = form.cleaned_data['user_location']
                form.save()
              
                messages.success(request, "User registered successfully!")
                return redirect("user_dashboard")
            else:
                print(form.errors)  # Debug: print form errors to the terminal
                messages.error(request, "Error in user signup form.")
                user_form = form  # Keep the data user just submitted
                company_form = CompanySignUpForm(prefix='company')
    else:
        # If GET or some other method, show blank forms
        user_form = UserSignUpForm(prefix='user')
        company_form = CompanySignUpForm(prefix='company')

    return render(request, "signup.html", {
        "user_form": user_form,
        "company_form": company_form
    })