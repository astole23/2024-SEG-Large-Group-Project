from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError
import os
import fitz  # PyMuPDF
import together
from dotenv import load_dotenv

# Load .env variables
load_dotenv() 
api_key = os.getenv("TOGETHER_API_KEY")

# Validate file size
def validate_file_size(value):
    max_size_kb = 1024  # 1MB
    if value.size > max_size_kb * 1024:
        raise ValidationError('File size must be less than 1MB.')

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text.strip()

# Send resume to Together AI for structured analysis
def classify_resume_with_together(text):
    prompt = f"""
    
You are an AI that extracts structured JSON from resume text. Return only a JSON object in this format:

{{
  "personal_info": {{
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "address": "string",
    "postcode": "string"
  }},
  "education": [
    {{
      "university": "string",
      "degree_type": "string",
      "field_of_study": "string",
      "grade": "string",
      "dates": "string",
      "modules": "string"
    }}
  ],
  "work_experience": [
    {{
      "company": "string",
      "job_title": "string",
      "dates": "string",
      "responsibilities": "string"
    }}
    ],
    [
    {{
    "skills": ["communication", "teamwork", "problem-solving"],
    "technical_skills": ["Python", "JavaScript", "SQL"],
    "languages": ["English", "Spanish"],
    "motivations": "string",
    "fit_for_role": "string",
    "career_aspirations": "string",
    "preferred_start_date": "YYYY-MM-DD"
    }}

Do not include commentary. If any value is missing, leave it as an empty string or empty array. Use only the following resume content:

{text}

JSON Output:
"""

    together_client = together.Together(api_key=api_key)

    response = together.Complete.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        prompt=prompt,
        max_tokens=1500,
        temperature=0.1
    )

    print(response)  # Debug output (optional)
    return response["choices"][0]["text"]

# Optional Django model that uses the extraction logic
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
            structured_data = classify_resume_with_together(pdf_text)
            self.structured_data = structured_data

        super(CV, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
