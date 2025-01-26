from django.shortcuts import render

# Create your views here.
def employer_dashboard(request):
    return render(request, 'employer_dashboard.html')

def contact_us(request):
    return render(request, 'contact_us.html')



