from django.db import models
import random

import string


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

    unique_id = models.CharField(max_length=8, unique=True, blank=True, null=True)

    def generate_unique_id(self):
        """Generate a unique 8-character ID consisting of 3 uppercase letters, 3 digits, and 2 special characters."""
        letters = string.ascii_uppercase
        digits = string.digits
        special_chars = string.punctuation

        while True:
            # Generate 3 random uppercase letters
            random_letters = ''.join(random.choices(letters, k=3))
            # Generate 3 random digits
            random_digits = ''.join(random.choices(digits, k=3))
            # Generate 2 random special characters
            random_specials = ''.join(random.choices(special_chars, k=2))

            # Combine all parts
            combined = random_letters + random_digits + random_specials

            # Shuffle the combined string to randomize the order
            unique_id = ''.join(random.sample(combined, len(combined)))

            # Ensure the generated ID is unique
            if not Company.objects.filter(unique_id=unique_id).exists():
                return unique_id

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
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