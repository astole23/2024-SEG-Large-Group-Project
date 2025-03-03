from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import os
from transformers import pipeline
import fitz  # PyMuPDF
import spacy
import re


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


# Load NLP model
nlp = spacy.load("en_core_web_sm") 
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text.strip()

import re

def classify_by_regex(text):
    data = {'Experience': [], 'Skills': [], 'Education': [], 'Certifications': [], 'Projects': [], 'Publications': [], 'Languages': [], 'Awards': []}

    # List of languages to search for
    languages_list = [
        "English", "Chinese", "Mandarin", "Cantonese", "Hindi", "Spanish", "French", 
        "Standard Arabic", "Bengali", "Russian", "Portuguese", "Indonesian", 
        "Urdu", "Standard German", "Japanese", "Swahili", "Marathi", "Telugu",
        "Western Punjabi", "Wu Chinese", "Tamil", "Turkish", "Korean", "Vietnamese", 
        "Yue Chinese", "Javanese", "Italian", "Egyptian Spoken Arabic", "Hausa", "Thai",
        "Gujarati", "Kannada", "Iranian Persian", "Bhojpuri", "Southern Min Chinese", 
        "Hakka Chinese", "Jinyu Chinese", "Filipino", "Burmese", "Polish", "Yoruba", 
        "Odia", "Malayalam", "Xiang Chinese", "Maithili", "Ukrainian", "Moroccan Spoken Arabic",
        "Eastern Punjabi", "Sunda", "Algerian Spoken Arabic", "Sundanese Spoken Arabic",
        "Nigerian Pidgin", "Zulu", "Igbo", "Amharic", "Northern Uzbek", "Sindhi", 
        "North Levantine Spoken Arabic", "Nepali", "Romanian", "Tagalog", "Dutch",
        "Sa'idi Spoken Arabic", "Gan Chinese", "Northern Pashto", "Magahi", "Saraiki", 
        "Xhosa", "Malay", "Khmer", "Afrikaans", "Sinhala", "Somali", "Chhattisgarhi",
        "Cebuano", "Mesopotamian Spoken Arabic", "Assamese", "Northeastern Thai", 
        "Northern Kurdish", "Hijazi Spoken Arabic", "Nigerian Fulfulde", "Bavarian", 
        "Bamanankan", "South Azerbaijani", "Northern Sotho", "Setswana", "Souther Sotho",
        "Czech", "Greek", "Chittagonian", "Kazakh", "Swedish", "Deccan", "Hungarian", "Jula",
        "Sadri", "Kinyarwanda", "Cameroonian Pidgin", "Sylheti", "South Levantine Spoken Arabic",
        "Tunisian Spoken Arabic", "Sanaani Spoken Arabic", "Azerbaijani", "Tamil", "Hebrew", "Nepali",
        "Armenian", "Georgian", "Icelandic", "Finnish", "Estonian", "Lithuanian", "Latvian", "Belarusian",
        "Uzbek", "Tigrinya", "Quechua", "Basque", "Haitian Creole", "Malagasy", "Sinhala", "Welsh", 
        "Esperanto", "Lao", "Somali", "Maori", "Norwegian", "Danish"
    ]

    # Classify text by regex patterns
    sections = [section.strip() for section in re.split(r"\n{2,}", text)]
    print(f"Sections found: {sections}")  # Print the split sections to check
    
    # Regular expression for detecting languages in text
    language_regex = r"\b(?:'|" + "|".join(map(re.escape, languages_list)) + r")\b"
    
    for section in sections:
        # Check if any of the languages from the list are in the section
        found_languages = re.findall(language_regex, section, re.IGNORECASE)
        if found_languages:
            print(f"Languages found in section: {found_languages}")
            data['Languages'].extend(set(found_languages))  # Using set to avoid duplicates
        # Check for other sections (e.g., Experience, Skills, etc.)
        elif re.search(r"\b(Experience|Work Experience|Career|Employment)\b", section, re.IGNORECASE):
            print(f"Experience section detected: {section[:100]}...")  # Print first 100 characters of the section
            data['Experience'].append(section)
        elif re.search(r"\b(Skills|Skill Set|Core Skills|Technical Skills)\b", section, re.IGNORECASE):
            print(f"Skills section detected: {section[:100]}...")  # Print first 100 characters of the section
            data['Skills'].append(section)
        elif re.search(r"\b(Education|Academic Background|Qualifications)\b", section, re.IGNORECASE):
            print(f"Education section detected: {section[:100]}...")  # Print first 100 characters of the section
            data['Education'].append(section)
        elif re.search(r"\b(Certifications|Certifications and Training|Certifications & Awards)\b", section, re.IGNORECASE):
            print(f"Certifications section detected: {section[:100]}...")
            data['Certifications'].append(section)
        elif re.search(r"\b(Projects|Project Experience)\b", section, re.IGNORECASE):
            print(f"Projects section detected: {section[:100]}...")
            data['Projects'].append(section)
        elif re.search(r"\b(Publications|Research)\b", section, re.IGNORECASE):
            print(f"Publications section detected: {section[:100]}...")
            data['Publications'].append(section)
        elif re.search(r"\b(Awards|Honors)\b", section, re.IGNORECASE):
            print(f"Awards section detected: {section[:100]}...")
            data['Awards'].append(section)
        else:
            print(f"Section not classified: {section[:100]}...")  # Print for unclassified sections

    return data



# NLP-based classification (fallback for unstructured CVs)
def classify_by_nlp(text):
    sections = {
        "Experience": [],
        "Skills": [],
        "Education": [],
        "Certifications": [],
        "Projects": [],
        "Publications": [],
        "Languages": [],
        "Awards": []
    }
    labels = list(sections.keys())
    
    sentences = text.split(". ")
    
    for sentence in sentences:
        result = classifier(sentence, labels)
        best_match = result["labels"][0]  # Get top classification
        sections[best_match].append(sentence)
    
    return sections

# Clean extracted text
def clean_text(text):
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '', text)  # Remove emails
    text = re.sub(r'http[s]?://[^\s]+', '', text)  # Remove URLs
    text = re.sub(r'[^A-Za-z0-9\s,.-]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

# Django Model
class CV(models.Model):
    name = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to='uploads/cvs/', 
        validators=[FileExtensionValidator(['pdf']), validate_file_size]
    )
    structured_data = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.name and self.pdf_file:
            self.name = os.path.splitext(self.pdf_file.name)[0]
        
        if self.pdf_file:
            pdf_text = extract_text_from_pdf(self.pdf_file.path)
            pdf_text = clean_text(pdf_text)
            
            structured_data, order = classify_by_regex(pdf_text)
            
            if not any(structured_data.values()):  # If regex failed, use NLP fallback
                structured_data = classify_by_nlp(pdf_text)
                
            self.structured_data = structured_data
        
        super(CV, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
