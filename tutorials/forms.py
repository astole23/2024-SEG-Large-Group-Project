from django import forms
from .models import Company, User
from django.contrib.auth.hashers import make_password

from django import forms
from django.contrib.auth.hashers import make_password
from .models import Company, User

class CompanyRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Company
        fields = ['company_name', 'email', 'password', 'industry', 'phone']

    def save(self, commit=True):
        company = super().save(commit=False)
        company.password = make_password(self.cleaned_data['password'])  # Hash password
        if commit:
            company.save()
        return company

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Hash password
        if commit:
            user.save()
        return user
