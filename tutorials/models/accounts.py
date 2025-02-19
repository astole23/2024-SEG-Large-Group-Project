from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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

    def __str__(self):
        return self.company_name