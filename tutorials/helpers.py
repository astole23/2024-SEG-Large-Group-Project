from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import os
from transformers import pipeline
import fitz  # PyMuPDF
import spacy
import re



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
