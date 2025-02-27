from django import forms
from .models import Company
from .models.company_review import Review
from django import forms
from .models import Company, User
from django.contrib.auth.hashers import make_password



class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'industry', 'email', 'phone', 'unique_id']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']

    # You can also add custom widgets or labels if needed
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), label='Review Text')
    rating = forms.IntegerField(min_value=1, max_value=5, label='Rating (1-5)')

class CompanyEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['logo', 'description']  # Fields the company can update

    logo = forms.ImageField(required=False)  # Logo is optional
    description = forms.CharField(widget=forms.Textarea, required=False)



class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Hash password
        if commit:
            user.save()
        return user


class CompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'email', 'industry', 'phone']