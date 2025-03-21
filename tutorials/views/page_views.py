from django.shortcuts import render

from tutorials.models.jobposting import JobPosting

def contact_us(request):
    return render(request, 'pages/contact_us.html')

def guest(request):
    query = request.GET.get('q', '')
    if query:
        job_postings = JobPosting.objects.filter(job_title__icontains=query)
    else:
        job_postings = JobPosting.objects.all()
    return render(request, 'pages/guest.html', {'job_postings': job_postings,'is_guest': True})


def about_us(request):
    return render(request, 'pages/about_us.html')

def terms_conditions(request):
    return render(request, 'pages/terms_conditions.html')



def privacy(request):
    return render(request, 'pages/privacy.html')

def user_agreement(request):
    return render(request, 'pages/user_agreement.html')

def faq(request):
    return render(request, 'pages/faq.html')


def help_centre(request):
    return render(request, 'pages/help_centre.html')

def accessibility(request):
    return render(request, 'pages/accessibility.html')
