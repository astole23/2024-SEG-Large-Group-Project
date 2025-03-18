from django.db import models
from django.contrib.auth.models import User as CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

# models.py
class UploadedCV(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/raw_cvs/')
    uploaded_at = models.DateTimeField(auto_now=True)



class UserDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='user_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name