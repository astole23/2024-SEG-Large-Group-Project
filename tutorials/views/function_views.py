from django.shortcuts import render, redirect
from tutorials.forms import UserLoginForm, CompanyLoginForm, CompanySignUpForm, UserSignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from tutorials.forms import UserSignUpForm, CompanySignUpForm

from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from tutorials.models.user_dashboard import UploadedCV
from django.http import JsonResponse

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

            # Redirect the "admin" user to the Django admin panel
            if user.username == "admin":
                return redirect('/admin/')

            # Redirect based on user type
            if user.is_company:
                return redirect('employer_dashboard')
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
    

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from tutorials.forms import UserSignUpForm, CompanySignUpForm

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from tutorials.forms import UserSignUpForm, CompanySignUpForm

def process_signup(request):
    """
    Process signup for both user types based on a hidden input in the form.
    """
    if request.method == "POST":
        user_type = request.POST.get("user_type")

        if user_type == "company":
            company_form = CompanySignUpForm(request.POST, prefix='company')
            user_form = UserSignUpForm(prefix='user')  # Ensure user_form exists

            print(f"🏢 Processing company signup - Valid? {company_form.is_valid()}")  # Debug

            if company_form.is_valid():
                company = company_form.save(commit=False)
                company.set_password(company_form.cleaned_data['password1'])  # Hash password
                company.save()

                authenticated_user = authenticate(username=company.username, password=company_form.cleaned_data['password1'])

                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, "Company registered and logged in successfully!")
                    return redirect("employer_dashboard")
                else:
                    messages.error(request, "Company signup successful, but auto-login failed. Please log in manually.")
                    return redirect("login")
            else:
                print(f"❌ Company Form Errors: {company_form.errors}")  # Debugging
                messages.error(request, "Company signup failed. Please check the form and try again.")

        elif user_type == "user":
            user_form = UserSignUpForm(request.POST, prefix='user')
            company_form = CompanySignUpForm(prefix='company')  # Ensure company_form exists

            print(f"👤 Processing user signup - Valid? {user_form.is_valid()}")  # Debug

            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.user_industry = user_form.cleaned_data['user_industry']
                user.user_location = user_form.cleaned_data['user_location']
                user.set_password(user_form.cleaned_data['password1'])  # Hash password
                user.save()

                authenticated_user = authenticate(username=user.username, password=user_form.cleaned_data['password1'])

                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, "User registered and logged in successfully!")
                    return redirect("user_dashboard")
                else:
                    messages.error(request, "User signup successful, but auto-login failed. Please log in manually.")
                    return redirect("login")
            else:
                print(f"❌ User Form Errors: {user_form.errors}")  # Debugging
                messages.error(request, "User signup failed. Please check the form and try again.")

    else:
        print("🟢 GET request received, rendering signup page")  # Debug
        user_form = UserSignUpForm(prefix='user')
        company_form = CompanySignUpForm(prefix='company')

    return render(request, "signup.html", {
        "user_form": user_form,
        "company_form": company_form
    })

def remove_duplicates_by_keys(data_list, keys):
    seen = set()
    result = []
    for item in data_list:
        identifier = tuple(item.get(key, "").strip().lower() for key in keys)
        if identifier not in seen:
            seen.add(identifier)
            result.append(item)
    return result

def split_skills(skills_list):
    tech_keywords = {
        "Python", "Java", "C++", "SQL", "JavaScript", "HTML", "CSS", "React", "Django", "Pygame", "Tkinter",
        "Git", "GitHub", "Excel", "APIs", "WireShark", "Microsoft Teams", "Databases", "Testing", "Debugging",
        "C#", "Node.js", "TypeScript", "Ruby", "Kotlin", "Swift", "Bash", "PowerShell", "NoSQL", "MongoDB",
        "PostgreSQL", "MySQL", "REST", "GraphQL", "CI/CD", "Docker", "Kubernetes", "Linux", "AWS", "Azure", "GCP",
        "Firebase", "Flutter", "Unity", "Unreal Engine", "Jenkins", "Agile", "Scrum", "JIRA", "Notion",
        "NumPy", "Pandas", "Matplotlib", "TensorFlow", "PyTorch", "OpenCV"
    }
    technical = []
    soft = []
    for skill in skills_list:
        if any(k.lower() in skill.lower() for k in tech_keywords):
            technical.append(skill)
        else:
            soft.append(skill)
    return technical, soft


def delete_raw_cv(request):
    if request.method == 'POST':
        try:
            cv = UploadedCV.objects.get(user=request.user)
            cv.file.delete(save=False)
            cv.delete()
            return JsonResponse({"success": True})
        except UploadedCV.DoesNotExist:
            return JsonResponse({"success": False, "error": "No CV found."})
    return JsonResponse({"success": False, "error": "Invalid request."})


