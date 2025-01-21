from django.shortcuts import render

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')