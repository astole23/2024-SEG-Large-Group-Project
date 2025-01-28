from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os
from transformers import pipeline
import fitz


class Company(models.Model):
    company_name = models.CharField(max_length=255) 
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=255)  
    industry = models.CharField(max_length=255)   
    phone = models.CharField(max_length=20) 

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
    

def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')
    

summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
    
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


class CV(models.Model):
    name = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to='uploads/cvs/', 
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )
    summary = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.name and self.pdf_file:
            self.name = os.path.splitext(self.pdf_file.name)[0]
        
        if self.pdf_file:
            pdf_text = extract_text_from_pdf(self.pdf_file.path)

            summary = summarizer(pdf_text, max_length=200, min_length=50, do_sample=False)
            self.summary = summary[0]['summary_text']

        super(CV, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
