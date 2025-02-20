from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
=======
import random
>>>>>>> 0133cc1a2efbfe9ddc9d7cc0df321f543b3f298b

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True) 
    first_name = models.CharField(max_length=255) 
    last_name = models.CharField(max_length=255)  
    phone = models.CharField(max_length=20)     
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Company(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="company_profile",
        null=True, blank=True)
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255) 
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
<<<<<<< HEAD
        return self.company_name
=======
        return self.company_name


class User(models.Model):
    first_name = models.CharField(max_length=255) 
    last_name = models.CharField(max_length=255)  
    email = models.EmailField(unique=True)        
    phone = models.CharField(max_length=20)       
    password = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
>>>>>>> 0133cc1a2efbfe9ddc9d7cc0df321f543b3f298b
