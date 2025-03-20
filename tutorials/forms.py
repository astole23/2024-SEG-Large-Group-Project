from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from tutorials.models.jobposting import JobPosting
from .models.company_review import Review
from .models.standard_cv import CVApplication
from django.contrib.auth.forms import PasswordChangeForm




User = get_user_model()

# Form to edit or create a complete company profile (for company users)
class CompanyProfileForm(forms.ModelForm):
    
    class Meta:
        
        model = User
        # Include the fields specific to company profiles
        fields = ['company_name', 'industry', 'email', 'phone', 'location', 'logo', 'description']

# Review form remains the same
class ReviewForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        label='Review Text'
    )
    rating = forms.IntegerField(
        min_value=1, max_value=5,
        label='Rating (1-5)'
    )

    class Meta:
        model = Review
        fields = ['text', 'rating']

# Form for companies to update certain profile fields (e.g. logo and description)
class CompanyEditForm(forms.ModelForm):
    logo = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        # Only allow editing of company-specific fields here
        fields = ['logo', 'description']

# Form for job postings remains unchanged
class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'job_title', 'location', 'contract_type', 'salary_range',
            'job_overview', 'roles_responsibilities', 'education_required',
            'application_deadline'
        ]

# Login forms for both users and companies (they both use the same authentication backend)
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class CompanyLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Company Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class UserSignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'First Name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Last Name'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm Password'
    }))
    user_industry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter industries (press Enter to add)', 'id': 'industry-input'})
    )
    user_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter locations (press Enter to add)'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_industry', 'user_location')


class CompanySignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm Password'
    }))
    company_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Company Name'
    }))
    industry = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Industry'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'company_name', 'industry')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.company_name = self.cleaned_data['company_name']
        user.industry = self.cleaned_data['industry']
        user.is_company = True  # Mark this user as a company account.
        if commit:
            user.save()
        return user

class CVApplicationForm(forms.ModelForm):
    class Meta:
        model = CVApplication
        fields = '__all__'



User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'industry', 'location')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your industry'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your location'}),
        }

class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
