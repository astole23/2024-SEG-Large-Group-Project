import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from tutorials.forms import (
    UserLoginForm, CompanyLoginForm,
    UserSignUpForm, CompanySignUpForm,
    UserUpdateForm, MyPasswordChangeForm)


def user_logout(request):
    logout(request)
    return redirect('/')



def login_view(request):
    user_form = UserLoginForm(prefix='user')
    company_form = CompanyLoginForm(prefix='company')

    return render(request, 'auth/login.html', {
        'user_form': user_form,
        'company_form': company_form
    })


def signup_view(request):
    if request.method == 'POST':

        is_company = 'is_company' in request.POST  

        if is_company:
            company_form = CompanySignUpForm(request.POST, prefix='company')

            if company_form.is_valid():
                company = company_form.save(commit=False)

                company.set_password(company_form.cleaned_data['password1'])
                company.is_company = True
                company.save()

                authenticated_user = authenticate(username=company.username, password=company_form.cleaned_data['password1'])

                if authenticated_user:
                    login(request, authenticated_user)
                    return redirect('employer_dashboard')
                else:
                    return redirect('signup')
        else:
            user_form = UserSignUpForm(request.POST, prefix='user')

            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.user_industry = user_form.cleaned_data['user_industry'].split(',')
                user.user_location = user_form.cleaned_data['user_location'].split(',')

                user.set_password(user_form.cleaned_data['password1'])
                user.is_company = False 
                user.save()

                authenticated_user = authenticate(username=user.username, password=user_form.cleaned_data['password1'])


                if authenticated_user:
                    login(request, authenticated_user)
                    return redirect('user_dashboard')
                
    else:
        user_form = UserSignUpForm(prefix='user')
        company_form = CompanySignUpForm(prefix='company')

    return render(request, 'auth/signup.html', {'user_form': user_form, 'company_form': company_form})

@login_required
def profile_settings(request):
    user = request.user  
    
    if request.method == 'POST':
        if 'update_details' in request.POST:
            details_form = UserUpdateForm(request.POST, request.FILES, instance=user) 
            password_form = MyPasswordChangeForm(user=user)
            
            if details_form.is_valid():
                details_form.save()
                messages.success(request, "Your details have been updated.")
                return redirect('settings')
            else:
                messages.error(request, "Update failed.")

        elif 'change_password' in request.POST:
            details_form = UserUpdateForm(instance=user)
            password_form = MyPasswordChangeForm(user=user, data=request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed.")
                return redirect('settings')
            else:
                messages.error(request, "Password change failed.")

        elif 'delete_account' in request.POST:
            username = user.username
            
            if user.user_profile_photo:
                if os.path.isfile(user.user_profile_photo.path):
                    os.remove(user.user_profile_photo.path)
            
            user.delete()
            logout(request)
            messages.success(request, f"Account '{username}' has been deleted successfully.")
            return redirect('guest')

    else:
        details_form = UserUpdateForm(instance=user)
        password_form = MyPasswordChangeForm(user=user)
        

    return render(request, 'pages/settings.html', {
        'details_form': details_form,
        'password_form': password_form,
    })


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        try:
            with transaction.atomic():
                user.delete()
                logout(request)
                messages.success(request, f"Account '{username}' has been deleted successfully.")
        except Exception as e:
            messages.error(request, "An error occurred while deleting your account.")

        return redirect('guest')
    return render(request, 'confirm_delete_account.html')
