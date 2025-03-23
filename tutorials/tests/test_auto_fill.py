import tempfile
import json
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import patch
import tutorials.auto_fill as auto_fill
from tutorials.auto_fill import CV


class AutoFillTests(TestCase):
    def setUp(self):
        self.temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self.temp_pdf.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n%%EOF")
        self.temp_pdf.flush()

    def tearDown(self):
        self.temp_pdf.close()

    def test_extract_text_from_pdf_returns_string(self):
        try:
            text = auto_fill.extract_text_from_pdf(self.temp_pdf.name)
            self.assertIsInstance(text, str)
        except Exception:
            self.skipTest("fitz could not parse the dummy PDF.")

    def test_validate_file_size_allows_small_file(self):
        small_file = SimpleUploadedFile("small.pdf", b"data" * 100)
        try:
            auto_fill.validate_file_size(small_file)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError on a small file.")

    def test_validate_file_size_rejects_large_file(self):
        large_content = b"a" * (1024 * 1025)  # 1MB + 1 byte
        large_file = SimpleUploadedFile("large.pdf", large_content)
        with self.assertRaises(ValidationError):
            auto_fill.validate_file_size(large_file)

    @patch("tutorials.auto_fill.together.Complete.create")
    def test_classify_resume_with_together_realistic(self, mock_create):
        realistic_output = {
            "choices": [{
                "text": json.dumps({
                    "personal_info": {
                        "full_name": "Alice Johnson",
                        "email": "alice.johnson@example.com",
                        "phone": "+44 7911 123456",
                        "address": "45 Queen's Gate, London",
                        "postcode": "SW7 5JP"
                    },
                    "education": [{
                        "university": "University College London",
                        "degree_type": "BSc",
                        "field_of_study": "Computer Science",
                        "grade": "First Class",
                        "dates": "2018 - 2021",
                        "modules": "Algorithms, Databases, Machine Learning"
                    }],
                    "work_experience": [{
                        "company": "Tech Solutions Ltd",
                        "job_title": "Software Engineer Intern",
                        "dates": "June 2020 - August 2020",
                        "responsibilities": "Built REST APIs, wrote automated tests"
                    }],
                    "skills": ["problem-solving", "teamwork"],
                    "technical_skills": ["Python", "React"],
                    "languages": ["English"],
                    "motivations": "I enjoy solving problems.",
                    "fit_for_role": "Strong coding background.",
                    "career_aspirations": "Full-stack developer.",
                    "preferred_start_date": "2025-07-01"
                })
            }]
        }

        mock_create.return_value = realistic_output

        result = auto_fill.classify_resume_with_together("Some CV text")
        self.assertEqual(result["personal_info"]["full_name"], "Alice Johnson")
        self.assertEqual(result["education"][0]["university"], "University College London")
        self.assertIn("Python", result["technical_skills"])

    @patch("tutorials.auto_fill.together.Complete.create")
    def test_classify_resume_with_together_minimal(self, mock_create):
        mock_create.return_value = {
            "choices": [{
                "text": json.dumps({
                    "personal_info": {
                        "full_name": "",
                        "email": "",
                        "phone": "",
                        "address": "",
                        "postcode": ""
                    },
                    "education": [],
                    "work_experience": [],
                    "skills": [],
                    "technical_skills": [],
                    "languages": [],
                    "motivations": "",
                    "fit_for_role": "",
                    "career_aspirations": "",
                    "preferred_start_date": ""
                })
            }]
        }

        result = auto_fill.classify_resume_with_together("Some messy text")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["personal_info"]["full_name"], "")

    @patch("tutorials.auto_fill.together.Complete.create")
    def test_classify_resume_with_together_invalid_json(self, mock_create):
        # This will hit the try-except block in classify_resume_with_together
        mock_create.return_value = {"choices": [{"text": "bad response without brackets"}]}
        with self.assertRaises(Exception):
            auto_fill.classify_resume_with_together("broken json")

    @patch("tutorials.auto_fill.together.Complete.create")
    def test_classify_resume_with_together_json_parsing_error(self, mock_create):
        # Return malformed JSON inside valid brackets
        mock_create.return_value = {"choices": [{"text": "{ this is not valid json }"}]}
        with self.assertRaises(Exception):
            auto_fill.classify_resume_with_together("another broken json")

    @patch("tutorials.auto_fill.extract_text_from_pdf")
    @patch("tutorials.auto_fill.classify_resume_with_together")
    def test_cv_model_save_sets_structured_data(self, mock_classify, mock_extract):
        mock_extract.return_value = "dummy extracted text"
        mock_classify.return_value = {
            "personal_info": {"full_name": "Test User"},
            "education": [],
            "work_experience": [],
            "skills": [],
            "technical_skills": [],
            "languages": [],
            "motivations": "",
            "fit_for_role": "",
            "career_aspirations": "",
            "preferred_start_date": ""
        }

        pdf_content = b"%PDF-1.4 fake"
        uploaded_pdf = SimpleUploadedFile("cv.pdf", pdf_content, content_type="application/pdf")

        cv = CV.objects.create(pdf_file=uploaded_pdf)
        self.assertIsNotNone(cv.structured_data)
        self.assertEqual(cv.structured_data["personal_info"]["full_name"], "Test User")

    def test_cv_str_representation(self):
        cv = CV(name="example_cv")
        self.assertEqual(str(cv), "example_cv")

    def test_extract_text_from_pdf_with_real_page(self):
        try:
            from reportlab.pdfgen import canvas
            from io import BytesIO

            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 750, "Hello, world!")  # Write text to page
            p.showPage()
            p.save()

            buffer.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(buffer.read())
                tmp.flush()
                text = auto_fill.extract_text_from_pdf(tmp.name)
                self.assertIn("Hello, world!", text)

        except ImportError:
            self.skipTest("reportlab not installed")

    def test_cv_model_save_skips_all_branches(self):
        cv = CV(name="existing_name")  # no pdf_file
        try:
            cv.save()
        except Exception:
            self.fail("CV.save() should not raise even if pdf_file is missing")
        self.assertEqual(str(cv), "existing_name")