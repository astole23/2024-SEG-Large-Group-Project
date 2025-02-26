from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import os
from transformers import pipeline
import fitz
import os
import fitz  # PyMuPDF
import json
import spacy
import re
from django.db import models



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
    

# Validate file size
def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

# Load NLP model
nlp = spacy.load("en_core_web_sm")  # Pre-trained model for entity recognition
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Extract named entities (skills, education, jobs)
def extract_named_entities(text):
    doc = nlp(text)
    entities = {
        "Education": [],
        "Skills": [],
        "Experience": []
    }

    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"]:  # Universities & Companies
            entities["Education"].append(ent.text)
        elif ent.label_ in ["WORK_OF_ART", "PRODUCT"]:  # Programming languages, skills
            entities["Skills"].append(ent.text)
        elif ent.label_ in ["PERSON", "NORP"]:  # Job titles
            entities["Experience"].append(ent.text)

    return entities

# Classify sentences into sections
def classify_sentences(text):
    sentences = text.split("\n")
    structured_data = {
        "Experience": [],
        "Skills": [],
        "Education": []
    }

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 3:
            continue

        # Classify based on keywords
        if any(word in sentence.lower() for word in ["developer", "engineer", "manager", "worked", "built", "designed"]):
            structured_data["Experience"].append(sentence)
        elif any(word in sentence.lower() for word in ["python", "java", "c++", "sql", "ai", "machine learning"]):
            structured_data["Skills"].append(sentence)
        elif any(word in sentence.lower() for word in ["bsc", "msc", "phd", "university", "degree"]):
            structured_data["Education"].append(sentence)

    return structured_data

# Summarize extracted sections
def summarize_sections(sections):
    summarized_sections = {}

    for key, value in sections.items():
        text = " ".join(value) if isinstance(value, list) else value

        if text.strip():
            summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
            summarized_sections[key] = summary[0]['summary_text']
        else:
            summarized_sections[key] = ""

    return summarized_sections

# Django Model
class CV(models.Model):
    name = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to='uploads/cvs/', 
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )
    structured_summary = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.name and self.pdf_file:
            self.name = os.path.splitext(self.pdf_file.name)[0]
        
        if self.pdf_file:
            pdf_text = extract_text_from_pdf(self.pdf_file.path)

            # Use both entity extraction & classification
            entity_sections = extract_named_entities(pdf_text)
            classified_sections = classify_sentences(pdf_text)

            # Merge results
            for key in entity_sections:
                classified_sections[key].extend(entity_sections[key])

            structured_summary = summarize_sections(classified_sections)

            self.structured_summary = structured_summary

        super(CV, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

