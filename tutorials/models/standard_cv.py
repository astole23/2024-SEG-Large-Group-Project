from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import os
from transformers import pipeline
import fitz  # PyMuPDF
import spacy
import re
from django.core.files import File

# Validate file size
def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

class CVApplication(models.Model):
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postcode = models.CharField(max_length=20)
    
    # Right to Work
    right_to_work = models.BooleanField()  # True for Yes, False for No
    visa_details = models.TextField(blank=True, null=True)  # If applicable
    
    # Education
    institution = models.CharField(max_length=255)
    degree_type = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    expected_grade = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    relevant_modules = models.TextField(blank=True, null=True)
    
    # Work Experience
    employer_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    work_start_date = models.DateField()
    work_end_date = models.DateField()
    responsibilities = models.TextField()
    
    # Skills
    key_skills = models.TextField()
    technical_skills = models.TextField()
    languages = models.TextField()
    
    # Motivation
    motivation_statement = models.TextField(validators=[MinLengthValidator(250), MaxLengthValidator(500)])
    fit_for_role = models.TextField()
    career_aspirations = models.TextField()
    
    # Availability
    preferred_start_date = models.DateField()
    internship_duration = models.CharField(max_length=50)
    willingness_to_relocate = models.BooleanField()
    
    # References (At least one, second is optional)
    reference_1_name = models.CharField(max_length=255)
    reference_1_position = models.CharField(max_length=255)
    reference_1_company = models.CharField(max_length=255)
    reference_1_contact = models.CharField(max_length=255)
    reference_2_name = models.CharField(max_length=255, blank=True, null=True)
    reference_2_position = models.CharField(max_length=255, blank=True, null=True)
    reference_2_company = models.CharField(max_length=255, blank=True, null=True)
    reference_2_contact = models.CharField(max_length=255, blank=True, null=True)
    
    # Optional Equal Opportunities Monitoring
    equal_opportunities_monitoring = models.TextField(blank=True, null=True)
    
    # CV Upload
    cv_file = models.FileField(
        upload_to='uploads/cvs/', 
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )
    
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = os.path.splitext(self.cv_file.name)[0]
        super(CVApplication, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.full_name


# Validate file size
def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

# Load NLP model
nlp = spacy.load("en_core_web_sm") 
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer="facebook/bart-large-cnn")

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

def clean_text(text):
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove unwanted special characters or digits
    text = re.sub(r'[^A-Za-z\s]', '', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

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

