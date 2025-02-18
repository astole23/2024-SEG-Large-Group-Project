from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from tutorials.models.accounts import Company
from tutorials.models.jobposting import JobPosting
from tutorials.forms import CompanyForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from tutorials.models.company_review import Review
from tutorials.forms import CompanyEditForm

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            company = Company.objects.get(email=email)
        except Company.DoesNotExist:
            company = None

        if company and check_password(password, company.password):
            request.session['company_id'] = company.id

            return redirect('edit_company', company_id=company.id)
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def guest(request):
    return render(request, 'guest.html')

def user_dashboard(request):
    return render(request, 'user_dashboard.html')

def about_us(request):
    return render(request, 'about_us.html')

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