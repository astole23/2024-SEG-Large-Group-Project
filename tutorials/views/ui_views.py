from django.shortcuts import render, redirect
from tutorials.forms import UserRegistrationForm, CompanyRegistrationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from tutorials.models.accounts import Company
from tutorials.models.jobposting import JobPosting
from tutorials.forms import CompanyForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from tutorials.models.company_review import Review
from tutorials.forms import CompanyEditForm
from django.contrib.auth import authenticate, login as auth_login

from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.contrib.auth.decorators import login_required


# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

@login_required
def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    user_form = UserRegistrationForm()
    company_form = CompanyRegistrationForm()

    if user_form.is_valid() and company_form.is_valid():
        user = user_form.save(commit=False)
        password = user_form.cleaned_data.get('password')
        user.set_password(password)
        user.save()

        company = company_form.save(commit=False)
        company.user = user
        company.save()

        user = authenticate(username=user.email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('user_dashboard')
        else: 
            messages.error(request, 'Authentication failed.')

        return redirect('login')
    
    else:
        user_form = UserRegistrationForm()
        company_form = CompanyRegistrationForm()


    return render(request, 'signup.html', {'user_form': user_form, 'company_form': company_form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            company = Company.objects.get(email=email)
            user = company.user
        except Company.DoesNotExist:
            company = None

        if company and check_password(password, user.password):
            # Authenticate the user
            user = authenticate(username=email, password=password)
            if user is not None:
                auth_login(request, user)  # This sets up the session
                # return redirect('edit_company', company_id=company.id)
            else:
                return render(request, 'login.html', {'error': 'Authentication failed'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

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

def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
    else:
        form = CompanyForm(instance=company)

    return render(request, 'company_detail.html', {'company': company, 'form': form})

def leave_review(request, company_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating')

        # Create and save the review
        review = Review(text=text, rating=rating)
        review.save()

        return JsonResponse({'message': 'Review submitted successfully!'}, status=200)
    
    return render(request, 'company_detail.html', {'company_id': company_id})


def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        company.description = request.POST.get('description')
        company.logo = request.FILES.get('logo')  # If uploading logo
        company.save()
        
        # Optionally, provide feedback to the user
        return render(request, 'edit_company.html', {'company': company, 'message': 'Company details updated!'})

    return render(request, 'edit_company.html', {'company': company})
