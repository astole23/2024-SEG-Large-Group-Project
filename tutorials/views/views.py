from django.shortcuts import render

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def signup(request):
    return render(request, 'signup.html')

def signup_test(request):
    return render(request, 'signup_test.html')

def login(request):
    return render(request, 'login.html')

def guest(request):
    return render(request, 'guest.html')

def base_content(request):
    return render(request, 'base_content.html')


