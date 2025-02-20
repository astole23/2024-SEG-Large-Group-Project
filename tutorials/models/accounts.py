from django.db import models
import random


class Company(models.Model):
    company_name = models.CharField(max_length=255) 
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=255)  
    industry = models.CharField(max_length=255)   
    phone = models.CharField(max_length=20) 
    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Optional: Enter the company's location (up to 100 characters)."
    )
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    unique_id = models.PositiveIntegerField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            while True:
                new_id = random.randint(10000000, 99999999)  # Generates a random 8-digit number
                if not Company.objects.filter(unique_id=new_id).exists():
                    self.unique_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


class User(models.Model):
    first_name = models.CharField(max_length=255) 
    last_name = models.CharField(max_length=255)  
    email = models.EmailField(unique=True)        
    phone = models.CharField(max_length=20)       
    password = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"