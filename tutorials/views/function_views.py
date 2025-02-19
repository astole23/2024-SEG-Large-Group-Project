from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from tutorials.forms import UserRegistrationForm, CompanyRegistrationForm
from tutorials.models.accounts import User, Company

# Combined Registration View
def register(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')

        if user_type == "company":
            user_form = UserRegistrationForm(request.POST)
            company_form = CompanyRegistrationForm(request.POST)

            if user_form.is_valid() and company_form.is_valid():
                user = user_form.save(commit=False)
                user.save()
                company = company_form.save(commit=False)
                company.user = user
                company.save()
                login(request, user)
                return redirect('guest')
        else:
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.save()
                login(request, user)
                return redirect('guest')

        # If invalid, re-render the form with errors
        return render(request, 'signup.html', {'user_form': user_form, 'company_form': company_form})

    return redirect('signup')

# User Login
def user_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('guest')
    return render(request, 'login.html')

# User Logout 
def user_logout(request):
    logout(request)
    return redirect('guest')
