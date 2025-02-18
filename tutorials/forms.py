from django import forms
from .models import Company
from .models.company_review import Review

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'industry', 'email', 'phone', 'location', 'logo']

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
    description = forms.CharField(widget=forms.Textarea, required=False)  # Description can be updated