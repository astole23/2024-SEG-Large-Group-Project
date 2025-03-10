# accounts.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
import json




class CustomUser(AbstractUser):
    # Common field already provided by AbstractUser:
    #   username, first_name, last_name, email, password, etc.
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_industry = models.JSONField(default=list, blank=True, null=True)  # Stores a list of industries
    user_location = models.JSONField(default=list, blank=True, null=True)  # Sto
    

    
    # If True, the account is for a company; if False, a regular user.
    is_company = models.BooleanField(default=False)
    
    # Company-specific fields – only applicable if is_company is True.
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    
    # Unique identifier for companies.
    unique_id = models.CharField(max_length=8, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # For company accounts, generate a unique 8-character code if not already set.
        if self.is_company and not self.unique_id:
            allowed = string.ascii_uppercase + string.digits + "!@#$%^&*()"
            while True:
                new_id = ''.join(random.choices(allowed, k=8))
                if not CustomUser.objects.filter(unique_id=new_id).exists():
                    self.unique_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_company and self.company_name:
            return self.company_name
        return self.username

class CompanyUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

class NormalUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'