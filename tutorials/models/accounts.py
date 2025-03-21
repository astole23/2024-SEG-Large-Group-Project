import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

from PIL import Image



class CustomUser(AbstractUser):
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_industry = models.JSONField(default=list, blank=True, null=True)  
    user_location = models.JSONField(default=list, blank=True, null=True)  
    user_profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    is_company = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    unique_id = models.CharField(max_length=8, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_company and not self.unique_id:
            self.generate_unique_id()

        super().save(*args, **kwargs)

        if self.user_profile_photo:
            self.process_image(self.user_profile_photo, target_size=(150, 150))
        
        if self.logo:
            self.process_image(self.logo, target_size=(200, 200))

    def generate_unique_id(self):
        """
        Generates a unique 8-character code for company accounts.
        """
        allowed = string.ascii_uppercase + string.digits + "!@#$%^&*()"
        while True:
            new_id = ''.join(random.choices(allowed, k=8))
            if not CustomUser.objects.filter(unique_id=new_id).exists():
                self.unique_id = new_id
                break

    def process_image(self, image_field, target_size):
        """
        Processes and resizes the provided image to the specified target size.
        """
        img_path = image_field.path
        img = Image.open(img_path)
        
        width, height = img.size
        min_side = min(width, height)
        left = (width - min_side) / 2
        top = (height - min_side) / 2
        right = (width + min_side) / 2
        bottom = (height + min_side) / 2
        img = img.crop((left, top, right, bottom))

        img = img.resize(target_size, Image.LANCZOS)
        
        img.save(img_path)

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


