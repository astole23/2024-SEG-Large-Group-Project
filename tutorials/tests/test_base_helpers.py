from django.test import TestCase
from tutorials.helpers.base_helpers import (
    normalize_to_string_list,
    normalize_edu,
    normalize_exp,
    normalize_str,
    remove_duplicate_education,
    remove_duplicate_experience
)

class HelperFunctionTests(TestCase):

    def test_normalize_to_string_list_with_list(self):
        data = [" Python ", " Django "]
        result = normalize_to_string_list(data)
        self.assertEqual(result, "Python, Django")

    def test_normalize_to_string_list_with_string(self):
        result = normalize_to_string_list("   hello world   ")
        self.assertEqual(result, "hello world")

    def test_normalize_to_string_list_with_none(self):
        self.assertEqual(normalize_to_string_list(None), "")

    def test_normalize_edu_full(self):
        edu = {
            "university": " Oxford ",
            "degree_type": "BSc",
            "field_of_study": "Computer Science",
            "grade": "A",
            "dates": "2020 - 2023",
            "modules": "AI, ML"
        }
        result = normalize_edu(edu)
        self.assertEqual(result, ('oxford', 'bsc', 'computer science', 'a', '2020 - 2023', 'ai, ml'))

    def test_normalize_edu_missing_keys(self):
        result = normalize_edu({})
        self.assertEqual(result, ('', '', '', '', '', ''))

    def test_normalize_exp_full(self):
        exp = {
            "company": " Google ",
            "job_title": "Engineer ",
            "responsibilities": "Code ",
            "dates": "2021 - 2022"
        }
        result = normalize_exp(exp)
        self.assertEqual(result, ('google', 'engineer', 'code', '2021 - 2022'))

    def test_normalize_exp_missing_keys(self):
        result = normalize_exp({})
        self.assertEqual(result, ('', '', '', ''))

    def test_normalize_str_with_special_chars(self):
        self.assertEqual(normalize_str("  Google—AI – Dev ’23 "), "google-ai - dev '23")

    def test_normalize_str_with_none(self):
        self.assertEqual(normalize_str(None), '')

    def test_remove_duplicate_education(self):
        entries = [
            {
                "university": "Oxford",
                "degreeType": "BSc",
                "fieldOfStudy": "CS",
                "dates": "2020-2023"
            },
            {
                "university": "Oxford",
                "degreeType": "BSc",
                "fieldOfStudy": "CS",
                "dates": "2020-2023"
            },
            {
                "university": "MIT",
                "degreeType": "MSc",
                "fieldOfStudy": "AI",
                "dates": "2023-2024"
            }
        ]
        result = remove_duplicate_education(entries)
        self.assertEqual(len(result), 2)

    def test_remove_duplicate_experience(self):
        entries = [
            {
                "employer": "Google",
                "jobTitle": "Engineer",
                "dates": "2021"
            },
            {
                "employer": "Google",
                "jobTitle": "Engineer",
                "dates": "2021"
            },
            {
                "employer": "Meta",
                "jobTitle": "Analyst",
                "dates": "2022"
            }
        ]
        result = remove_duplicate_experience(entries)
        self.assertEqual(len(result), 2)

class ExtendedHelperFunctionTests(TestCase):

    # --- normalize_to_string_list ---
    def test_normalize_to_string_list_empty_list(self):
        self.assertEqual(normalize_to_string_list([]), "")

    def test_normalize_to_string_list_list_with_whitespace(self):
        self.assertEqual(normalize_to_string_list(["   A   ", "   B "]), "A, B")



    def test_normalize_to_string_list_int_input(self):
        self.assertEqual(normalize_to_string_list(123), "")

    # --- normalize_edu ---
    def test_normalize_edu_mixed_case_and_spaces(self):
        edu = {
            "university": "  MIT ",
            "degree_type": " MSc ",
            "field_of_study": " AI ",
            "grade": " A+ ",
            "dates": "2023 - 2024 ",
            "modules": " NLP, Robotics "
        }
        self.assertEqual(normalize_edu(edu), ('mit', 'msc', 'ai', 'a+', '2023 - 2024', 'nlp, robotics'))

    def test_normalize_edu_partial_data(self):
        edu = {"university": "UCL"}
        result = normalize_edu(edu)
        self.assertEqual(result[0], "ucl")
        self.assertEqual(result[1:], ('', '', '', '', ''))

    # --- normalize_exp ---
   

    def test_normalize_exp_empty_dict(self):
        self.assertEqual(normalize_exp({}), ('', '', '', ''))

    # --- normalize_str ---
    def test_normalize_str_variants(self):
        self.assertEqual(normalize_str("–—’"), "--'")
        self.assertEqual(normalize_str("Hello–World"), "hello-world")

    def test_normalize_str_blank_string(self):
        self.assertEqual(normalize_str("   "), "")

    # --- remove_duplicate_education ---
    def test_remove_duplicate_education_empty_list(self):
        self.assertEqual(remove_duplicate_education([]), [])

    def test_remove_duplicate_education_all_unique(self):
        edu_list = [
            {"university": "A", "degreeType": "B", "fieldOfStudy": "C", "dates": "2020"},
            {"university": "D", "degreeType": "E", "fieldOfStudy": "F", "dates": "2021"},
        ]
        self.assertEqual(len(remove_duplicate_education(edu_list)), 2)

    def test_remove_duplicate_education_case_insensitive(self):
        edu_list = [
            {"university": "Harvard", "degreeType": "BSc", "fieldOfStudy": "CS", "dates": "2020"},
            {"university": "  harvard ", "degreeType": "bsc", "fieldOfStudy": "cs", "dates": "2020"},
        ]
        self.assertEqual(len(remove_duplicate_education(edu_list)), 1)

    # --- remove_duplicate_experience ---
    def test_remove_duplicate_experience_empty_list(self):
        self.assertEqual(remove_duplicate_experience([]), [])

    def test_remove_duplicate_experience_all_unique(self):
        exp = [
            {"employer": "Google", "jobTitle": "Dev", "dates": "2022"},
            {"employer": "Meta", "jobTitle": "PM", "dates": "2023"},
        ]
        self.assertEqual(len(remove_duplicate_experience(exp)), 2)

    def test_remove_duplicate_experience_whitespace_sensitive(self):
        exp = [
            {"employer": "SpaceX", "jobTitle": "Engineer", "dates": "2021"},
            {"employer": " SpaceX ", "jobTitle": " Engineer ", "dates": "2021 "},
        ]
        self.assertEqual(len(remove_duplicate_experience(exp)), 1)

    def test_remove_duplicate_experience_missing_keys(self):
        exp = [
            {"employer": "NASA"},
            {"employer": "NASA", "jobTitle": "Scientist"},
        ]
        self.assertEqual(len(remove_duplicate_experience(exp)), 2)


    def test_normalize_to_string_list_list(self):
        self.assertEqual(normalize_to_string_list([" Python ", "Django "]), "Python, Django")

    def test_normalize_to_string_list_string(self):
        self.assertEqual(normalize_to_string_list("  Just a string  "), "Just a string")

    def test_normalize_to_string_list_none(self):
        self.assertEqual(normalize_to_string_list(None), "")

    def test_normalize_str_symbols(self):
        self.assertEqual(normalize_str("–—’Dash’s"), "--'dash's")

    def test_normalize_edu_basic(self):
        data = {
            "university": "MIT", "degree_type": "BSc", "field_of_study": "CS",
            "grade": "A", "dates": "2019-2023", "modules": "AI"
        }
        result = normalize_edu(data)
        self.assertEqual(result, ("mit", "bsc", "cs", "a", "2019-2023", "ai"))

    def test_normalize_exp_basic(self):
        data = {
            "company": "Google", "job_title": "Dev", "responsibilities": "Stuff", "dates": "2020-2022"
        }
        result = normalize_exp(data)
        self.assertEqual(result, ("google", "dev", "stuff", "2020-2022"))

    def test_remove_duplicate_education(self):
        entries = [
            {"university": "Oxford", "degreeType": "BA", "fieldOfStudy": "History", "dates": "2020"},
            {"university": "oxford", "degreeType": "BA", "fieldOfStudy": "History", "dates": "2020"},
        ]
        result = remove_duplicate_education(entries)
        self.assertEqual(len(result), 1)

    def test_remove_duplicate_experience(self):
        entries = [
            {"employer": "Amazon", "jobTitle": "Manager", "dates": "2021"},
            {"employer": "amazon", "jobTitle": "Manager", "dates": "2021"},
        ]
        result = remove_duplicate_experience(entries)
        self.assertEqual(len(result), 1)

    def test_remove_duplicate_education_missing_fields(self):
        entries = [
            {"university": "Cambridge", "degreeType": "", "fieldOfStudy": "", "dates": ""},
            {"university": "Cambridge", "degreeType": "", "fieldOfStudy": "", "dates": ""}
        ]
        self.assertEqual(len(remove_duplicate_education(entries)), 1)

    def test_remove_duplicate_experience_empty_fields(self):
        entries = [{"employer": "", "jobTitle": "", "dates": ""}, {"employer": "", "jobTitle": "", "dates": ""}]
        self.assertEqual(len(remove_duplicate_experience(entries)), 1)
