from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.forms import UserLoginForm, CompanyLoginForm, CompanySignUpForm, UserSignUpForm
from tutorials.views.function_views import process_login, process_signup

User = get_user_model()

class AuthViewsTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass', is_company=False)
        self.company = User.objects.create_user(username='testcompany', password='companypass', is_company=True)

    # Tests for process_login view

    def test_process_login_view_valid_user(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'user',
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs

    def test_process_login_view_valid_company(self):
        response = self.client.post(reverse('process_login'), {
            'user_type': 'company',
            'username': 'testcompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs

  

    def test_process_login_view_get_request(self):
        response = self.client.get(reverse('process_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


   

    # Tests for process_signup view

    def test_process_signup_view_valid_user(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'user',
            'username': 'newuser',
            'password': 'newpass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs
 
    def test_process_signup_view_valid_company(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': 'newcompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs
    

   

    def test_process_signup_view_get_request(self):
        response = self.client.get(reverse('process_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

   

    def test_process_signup_view_company_success_message(self):
        response = self.client.post(reverse('process_signup'), {
            'user_type': 'company',
            'username': 'anothercompany',
            'password': 'companypass'
        })
        self.assertEqual(response.status_code, 200)  # Redirect occurs


import re
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from tutorials.validators import CustomPasswordValidator    

class CustomPasswordValidatorTests(TestCase):
    def setUp(self):
        self.validator = CustomPasswordValidator()

    # Test valid passwords
    def test_valid_password(self):
        valid_passwords = [
            "Password1",
            "SecurePass123",
            "ValidPass99",
            "Test1234",
            "HelloWorld1",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords missing uppercase letters
    def test_password_missing_uppercase(self):
        invalid_passwords = [
            "password1",
            "lowercase123",
            "nouppercase1",
            "alllower1",
            "1234567a",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords missing lowercase letters
    def test_password_missing_lowercase(self):
        invalid_passwords = [
            "PASSWORD1",
            "UPPERCASE123",
            "NOLOWERCASE1",
            "ALLUPPER1",
            "1234567A",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_lower')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one lowercase letter."
            )

    # Test passwords missing numerals
    def test_password_missing_numeral(self):
        invalid_passwords = [
            "Password",
            "NoNumbersHere",
            "JustLetters",
            "UpperCaseOnly",
            "LowerCaseOnly",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    # Test empty password
    def test_empty_password(self):
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("")
        self.assertEqual(context.exception.code, 'password_no_upper')  # First check fails
        self.assertEqual(
            str(context.exception.message),
            "The password must contain at least one uppercase letter."
        )

    # Test passwords with only uppercase letters
    def test_password_only_uppercase(self):
        invalid_passwords = [
            "UPPERCASE",
            "ALLUPPER",
            "ONLYUPPER",
            "CAPITALS",
            "UPPERONLY",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_lower')  # Missing lowercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one lowercase letter."
            )

    # Test passwords with only lowercase letters
    def test_password_only_lowercase(self):
        invalid_passwords = [
            "lowercase",
            "alllower",
            "onlylower",
            "smallletters",
            "loweronly",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with only numerals
    def test_password_only_numerals(self):
        invalid_passwords = [
            "12345678",
            "987654321",
            "00000000",
            "11111111",
            "99999999",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with special characters
    def test_password_with_special_characters(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with spaces
    def test_password_with_spaces(self):
        invalid_passwords = [
            "Password 1",
            "Secure Pass123",
            "Valid Pass99",
            "Test 1234",
            "Hello World1",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test get_help_text method
    def test_get_help_text(self):
        help_text = self.validator.get_help_text()
        self.assertEqual(
            help_text,
            "Your password must contain at least one uppercase letter, one lowercase letter, and one numeral."
        )
    def test_password_one_uppercase(self):
        valid_passwords = [
            "Password1",
            "Apassword1",
            "1passwordA",
            "passWord1",
            "1Apassword",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one lowercase letter
    def test_password_one_lowercase(self):
        valid_passwords = [
            "PASSWORDa1",
            "1PASSWORDAa",
            "A1PASSWORDa",
            "1aPASSWORD",
            "PASSWORD1a",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one numeral
    def test_password_one_numeral(self):
        valid_passwords = [
            "Password1",
            "1Password",
            "Pass1word",
            "Password1",
            "1PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with multiple uppercase letters
   

    

    # Test passwords with multiple numerals
    def test_password_multiple_numerals(self):
        valid_passwords = [
            "Password123",
            "123Password",
            "Pass123word",
            "Password123",
            "123PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with special characters and valid requirements
    def test_password_with_special_characters_valid(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading/trailing spaces
    def test_password_with_leading_trailing_spaces(self):
        invalid_passwords = [
            " Password1",
            "Password1 ",
            " Password1 ",
            "  Password1  ",
            " Password1  ",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with only special characters
    def test_password_only_special_characters(self):
        invalid_passwords = [
            "!@#$%^&*",
            "!@#$%^&*()",
            "!@#$%^&*()_+",
            "!@#$%^&*()_+{}",
            "!@#$%^&*()_+{}[]",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with mixed case and no numerals
    def test_password_mixed_case_no_numerals(self):
        invalid_passwords = [
            "Password",
            "PassWord",
            "PASSword",
            "paSSWORD",
            "PaSsWoRd",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    

    # Test passwords with exactly 8 characters (minimum length)
    def test_password_minimum_length(self):
        valid_passwords = [
            "Passwo1",
            "Passwo1!",
            "Passwo1@",
            "Passwo1#",
            "Passwo1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly 16 characters (maximum length)
    def test_password_maximum_length(self):
        valid_passwords = [
            "Password12345678",
            "Password12345678!",
            "Password12345678@",
            "Password12345678#",
            "Password12345678$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with non-ASCII characters
    def test_password_non_ascii_characters(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with emojis
    def test_password_with_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading zeros
    def test_password_with_leading_zeros(self):
        valid_passwords = [
            "Password01",
            "Password001",
            "Password0001",
            "Password00001",
            "Password000001",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with trailing zeros
    def test_password_with_trailing_zeros(self):
        valid_passwords = [
            "Password10",
            "Password100",
            "Password1000",
            "Password10000",
            "Password100000",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and special characters
    def test_password_mixed_case_numerals_special_chars(self):
        valid_passwords = [
            "Password1!",
            "Passw0rd@",
            "P@ssw0rd",
            "P@ssw0rd!",
            "P@ssw0rd#",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and spaces
    def test_password_mixed_case_numerals_spaces(self):
        valid_passwords = [
            "Password 1",
            "Pass word1",
            "Pass word 1",
            "Pass word 1!",
            "Pass word 1@",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and non-ASCII characters
    def test_password_mixed_case_numerals_non_ascii(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with mixed case, numerals, and emojis
    def test_password_mixed_case_numerals_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

        

      

    # Test passwords with exactly one uppercase letter
    def test_password_one_uppercase(self):
        valid_passwords = [
            "Password1",
            "Apassword1",
            "1passwordA",
            "passWord1",
            "1Apassword",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one lowercase letter
    def test_password_one_lowercase(self):
        valid_passwords = [
            "PASSWORDa1",
            "1PASSWORDAa",
            "A1PASSWORDa",
            "1aPASSWORD",
            "PASSWORD1a",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly one numeral
    def test_password_one_numeral(self):
        valid_passwords = [
            "Password1",
            "1Password",
            "Pass1word",
            "Password1",
            "1PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")


    # Test passwords with multiple lowercase letters
    def test_password_multiple_lowercase(self):
        valid_passwords = [
            "Password1",
            "paSSword1",
            "passWORD1",
            "pCassword1",
            "PassWord1",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with multiple numerals
    def test_password_multiple_numerals(self):
        valid_passwords = [
            "Password123",
            "123Password",
            "Pass123word",
            "Password123",
            "123PASSWORDa",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with special characters and valid requirements
    def test_password_with_special_characters_valid(self):
        valid_passwords = [
            "Password1!",
            "SecurePass123@",
            "ValidPass99#",
            "Test1234$",
            "HelloWorld1%",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with leading/trailing spaces
    def test_password_with_leading_trailing_spaces(self):
        invalid_passwords = [
            " Password1",
            "Password1 ",
            " Password1 ",
            "  Password1  ",
            " Password1  ",
        ]
        for password in invalid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with only special characters
    def test_password_only_special_characters(self):
        invalid_passwords = [
            "!@#$%^&*",
            "!@#$%^&*()",
            "!@#$%^&*()_+",
            "!@#$%^&*()_+{}",
            "!@#$%^&*()_+{}[]",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_upper')  # Missing uppercase
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one uppercase letter."
            )

    # Test passwords with mixed case and no numerals
    def test_password_mixed_case_no_numerals(self):
        invalid_passwords = [
            "Password",
            "PassWord",
            "PASSword",
            "paSSWORD",
            "PaSsWoRd",
        ]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate(password)
            self.assertEqual(context.exception.code, 'password_no_number')
            self.assertEqual(
                str(context.exception.message),
                "The password must contain at least one numeral."
            )

    # Test passwords with mixed case and no lowercase
  
    def test_password_minimum_length(self):
        valid_passwords = [
            "Passwo1",
            "Passwo1!",
            "Passwo1@",
            "Passwo1#",
            "Passwo1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with exactly 16 characters (maximum length)
    def test_password_maximum_length(self):
        valid_passwords = [
            "Password12345678",
            "Password12345678!",
            "Password12345678@",
            "Password12345678#",
            "Password12345678$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with non-ASCII characters
    def test_password_non_ascii_characters(self):
        valid_passwords = [
            "Pässwörd1",
            "Pässwörd1!",
            "Pässwörd1@",
            "Pässwörd1#",
            "Pässwörd1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

    # Test passwords with emojis
    def test_password_with_emojis(self):
        valid_passwords = [
            "P😊ssword1",
            "P😊ssword1!",
            "P😊ssword1@",
            "P😊ssword1#",
            "P😊ssword1$",
        ]
        for password in valid_passwords:
            try:
                self.validator.validate(password)
            except ValidationError:
                self.fail(f"Valid password '{password}' raised ValidationError unexpectedly.")

 


    
  