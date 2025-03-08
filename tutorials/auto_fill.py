from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError
import os
import fitz  # PyMuPDF
import re
import together

# Your Together API key
api_key = os.getenv("api_key")

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

def classify_resume_with_together(text):
    prompt = f"""
    You are an AI trained to summarize resumes into clearly defined sections.

    Provide a structured JSON output with the following fields:
    {{
        "Experience & Education": "Summarize work and educational background.",
        "Skills": "List key skills and competencies.",
        "Projects": "Summarize important projects.",
        "Languages": "List languages spoken."
    }}

    Only use information directly from the resume, do not make assumptions. Do not include personal information.

    Resume text:
    {text}

    JSON Output:
    """

    together_client = together.Together(api_key=api_key)

    response = together.Complete.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        prompt=prompt,
        max_tokens=1500,
        temperature=0.1,  # Lower temperature for more deterministic results
    )

    print(response)  # Debugging: See the actual response structure

    return response["choices"][0]["text"]  # Extract the actual content

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
            # Extract and clean text from the PDF
            pdf_text = extract_text_from_pdf(self.pdf_file.path)
            
            # Classify the resume text using Together AI
            structured_data = classify_resume_with_together(pdf_text)
            
            # Store the structured data
            self.structured_data = structured_data
        
        super(CV, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

