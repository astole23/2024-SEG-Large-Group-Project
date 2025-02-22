from django.shortcuts import render

# Create your views here.
def employer_dashboard(request):
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    return render(request, 'employer_dashboard.html')
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    # Query the database for all job postings
    job_postings = JobPosting.objects.all()
    # Pass the query results to the template in a context dictionary
    context = {'job_postings': job_postings}
    return render(request, 'employer_dashboard.html', context)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

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