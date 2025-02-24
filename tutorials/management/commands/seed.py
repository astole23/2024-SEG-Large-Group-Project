import os
import re
import requests
import random
import string
from django.core.management.base import BaseCommand
from tutorials.models.jobposting import JobPosting
import faker
from tutorials.models.accounts import User,Company
from phonenumbers import parse, is_possible_number, is_valid_number, PhoneNumberFormat, format_number


#Already generated list of users
user_fixtures = [
    {
        'company_name': '@JohnLTD',
        'email': 'johnLTD@example.org',
        'industry': 'construction',
        'phone': '+447652567298',
        'user_type': 'company',
        'password': 'password',
        'unique_id' : '*****'
    },
    {
        'username': '@janedoe',
        'email': 'jane.doe@example.org',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'phone': '+447866352809',
        'user_type': 'user',
        'password': 'password'
    },
    {
        'username': '@admin',
        'email': 'admin@example.org',
        'user_type': 'admin',
        'password': 'password'
    },
]




fake = faker.Faker()
# Adzuna API credentials
ADZUNA_APP_ID = "dac9af71"
ADZUNA_APP_KEY = "0d149e6c79fe0dbc54e9bece78c8ff87"

# Categories for diversified job fetching
CATEGORIES = [
    "business", "management", "sales", "marketing", "technology", "internship", "software-development",
    "engineering", "design", "industry", "finance", "accounting", "healthcare",
    "education", "legal", "customer-service", "retail", "hospitality", "construction",
    "media", "logistics", "human-resources", "writing", "consulting", "ngo", "data-science",
]

# Randomized options for fields
EDUCATION_OPTIONS = [
    "High School Diploma", "Bachelor's Degree", "Master's Degree", "PhD",
    "Diploma in Related Field", "Certification in Relevant Skill",
    "No Formal Education Required", "Relevant Work Experience",
]

# Randomized options for perks, application deadlines,  and why join us
PERKS_OPTIONS = [
    "Flexible working hours", "Health insurance", "Remote work opportunities",
    "On-site gym", "Free lunch/snacks", "Childcare facilities", "Pet-friendly office",
    "Stock options", "Paid time off (PTO)", "Annual performance bonus",
    "Professional development budget", "Free training and certifications",
    "Travel opportunities", "Company laptop", "Work-from-home stipend",
    "Retirement savings plan", "Parental leave", "Diversity and inclusion initiatives",
    "Team-building retreats", "Mental health support", "Referral bonus program",
    "Discounted gym memberships", "Free parking", "Office game room",
    "Tuition reimbursement", "Equity in the company", "Employee discount programs",
    "Unlimited vacation days", "Free access to learning platforms",
    "Relocation assistance", "Commuter benefits", "Wellness programs",
    "Corporate social responsibility opportunities", "Paid volunteering days",
    "Flexible dress id", "Monthly social events", "Annual health check-ups",
    "Employee recognition programs", "Innovation budget", "Quarterly team dinners",
    "Company-sponsored sports teams", "On-site library", "Study leave benefits",
    "Hybrid work environment", "Leadership training", "Sabbatical leave options",
    "Annual company trips", "Pet insurance", "Life insurance",
    "Health savings account (HSA)", "Dedicated workspace reimbursement",
    "Subscription to industry journals", "Discounts on company products/services"
]

# Randomized options for application deadlines
APPLICATION_DEADLINE_OPTIONS = [
    "7 days from now", "10 days from now", "14 days from now", "30 days from now",
    "60 days from now", "Rolling applications", "Applications close when position is filled",
    "Immediate hiring", "End of the month", "End of the financial quarter",
    "Until further notice", "Application window open all year",
    "Applications reviewed weekly", "Deadline extended by employer",
    "Last date: 15th of next month", "First come, first served", "End of fiscal year",
    "Recruitment ends in 90 days", "Position filled on a rolling basis",
    "Interviews begin next week", "Applications processed daily",
    "Open until all positions are filled", "30 days from today",
    "Open-ended application process", "Hiring within 2 months", "Hiring within 6 weeks",
    "10 working days from now", "Open for 3 months", "Last date to apply: 25th of next month",
    "On or before the first Friday of next month", "Closes mid-year", 
    "Submit applications by next Monday", "Hiring till 15th of next month",
    "Position expected to be filled by next month", "Last call for applications in 2 weeks",
    "Deadline extended to next month", "Final date: end of quarter",
    "Open until next fiscal quarter", "Hiring closes on last Friday of the month",
    "First week of next month", "Application window: Open for 2 more months"
]

# Randomized options for why join us section
WHY_JOIN_US_OPTIONS = [
    "Join a dynamic team passionate about innovation and excellence.",
    "Be part of a company that values creativity and individuality.",
    "Work with cutting-edge technologies and industry leaders.",
    "Grow your career in a supportive and collaborative environment.",
    "Enjoy flexible work arrangements and a healthy work-life balance.",
    "Contribute to meaningful projects that make a difference.",
    "Experience exciting career advancement opportunities.",
    "Join a company that values diversity, equity, and inclusion.",
    "Work for a global leader with opportunities to travel.",
    "Be part of a fast-growing and high-energy organization.",
    "Enjoy competitive compensation and comprehensive benefits.",
    "Join a workplace that fosters innovation and teamwork.",
    "Shape the future with a forward-thinking and ambitious company.",
    "Be empowered to make a real impact in your role.",
    "Enjoy opportunities for personal and professional development.",
    "Be recognized and rewarded for your hard work and achievements.",
    "Collaborate with top-tier talent in the industry.",
    "Work on exciting projects in a thriving industry.",
    "Benefit from a transparent and inclusive work culture.",
    "Contribute to solutions that address real-world challenges.",
    "Be part of a team that values open communication and respect.",
    "Take advantage of comprehensive training and mentorship programs.",
    "Enjoy working in a fun and engaging office environment.",
    "Participate in cutting-edge projects with top-tier clients.",
    "Shape your career in an organization with a clear mission.",
    "Experience a culture that celebrates success and creativity.",
    "Enjoy a culture of recognition and employee appreciation.",
    "Work in a role that challenges and excites you every day.",
    "Be supported by leadership that genuinely cares about employees.",
    "Join a company at the forefront of technological advancements.",
    "Experience a positive and uplifting company culture.",
    "Be inspired by a leadership team with a proven track record.",
    "Enjoy generous vacation time and flexible work policies.",
    "Make your mark in an environment that nurtures talent.",
    "Be part of an organization that invests in your future.",
    "Work in a role that aligns with your values and aspirations.",
    "Be part of a socially responsible company committed to impact.",
    "Enjoy working in a collaborative, high-energy atmosphere.",
    "Help build a brighter future with a company that cares."
]

# Function to generate roles, responsibilities, and skills based on job title
def generate_roles_and_skills(category):
    #Generate roles, responsibilities, required skills, and preferred skills based on the category

    # Define pools for each category
    category_specific_data = {
        "business": {
            "responsibilities": [
                "Analyze business operations and identify opportunities for improvement.",
                "Develop and execute business strategies to meet goals.",
                "Monitor market trends and adapt business plans accordingly.",
                "Collaborate with stakeholders to align objectives.",
                "Prepare and present business performance reports.",
            ],
            "required_skills": [
                "Strong analytical and problem-solving skills",
                "Excellent communication and presentation skills",
                "Knowledge of business operations and financial planning",
                "Ability to manage cross-functional teams",
                "Proficiency in business analytics tools (e.g., Power BI, Tableau)",
            ],
            "preferred_skills": [
                "MBA or equivalent degree",
                "Experience in strategic consulting",
                "Familiarity with CRM tools like Salesforce",
                "Knowledge of international business practices",
                "Expertise in competitive market analysis",
            ],
        },
        "software-development": {
            "responsibilities": [
                "Write clean, efficient, and maintainable code.",
                "Collaborate with design and product teams to define requirements.",
                "Test and debug applications to ensure reliability.",
                "Optimize software performance for scalability.",
                "Research and integrate new technologies.",
            ],
            "required_skills": [
                "Proficiency in programming languages (e.g., Python, Java, C++)",
                "Experience with RESTful APIs and microservices",
                "Strong understanding of version control systems (e.g., Git)",
                "Knowledge of software development life cycles",
                "Familiarity with cloud platforms (e.g., AWS, Azure)",
            ],
            "preferred_skills": [
                "Experience with DevOps tools like Docker and Kubernetes",
                "Knowledge of machine learning frameworks",
                "Familiarity with front-end frameworks like React or Angular",
                "Strong problem-solving skills and algorithm design expertise",
                "Experience with blockchain technologies",
            ],
        },
        "healthcare": {
            "responsibilities": [
                "Provide high-quality patient care and medical services.",
                "Collaborate with healthcare teams to ensure comprehensive care.",
                "Maintain accurate and up-to-date patient records.",
                "Educate patients about health management and prevention.",
                "Participate in ongoing medical training and certifications.",
            ],
            "required_skills": [
                "Strong understanding of medical terminology and procedures",
                "Excellent interpersonal and communication skills",
                "Knowledge of patient care protocols",
                "Proficiency in using electronic medical records systems",
                "Ability to work in high-pressure environments",
            ],
            "preferred_skills": [
                "Specialization in a specific field (e.g., cardiology, pediatrics)",
                "Experience in emergency medicine",
                "Knowledge of public health policies",
                "Certification in advanced medical techniques",
                "Familiarity with telemedicine platforms",
            ],
        },
        "marketing": {
            "responsibilities": [
                "Develop and execute marketing campaigns.",
                "Analyze market trends and competitor strategies.",
                "Collaborate with sales teams to align marketing objectives.",
                "Manage social media platforms and digital content.",
                "Measure campaign performance and generate reports.",
            ],
            "required_skills": [
                "Strong knowledge of digital marketing strategies",
                "Proficiency in SEO and SEM tools",
                "Excellent copywriting and content creation skills",
                "Experience with social media management tools",
                "Ability to analyze and interpret marketing data",
            ],
            "preferred_skills": [
                "Experience in graphic design and video editing",
                "Familiarity with influencer marketing strategies",
                "Knowledge of CRM and email marketing tools",
                "Experience in managing marketing budgets",
                "Strong public speaking and presentation skills",
            ],
        },
        # Add other categories similarly...
    }

    # Fallback to generic skills and responsibilities if the category is not mapped
    generic_data = {
        "responsibilities": [
            "Collaborate with team members to achieve project goals.",
            "Develop and maintain key deliverables in alignment with project timelines.",
            "Ensure compliance with company policies and industry standards.",
            "Participate in meetings and provide insights and updates.",
            "Monitor and evaluate project progress and implement necessary changes.",
        ],
        "required_skills": [
            "Strong analytical skills",
            "Excellent communication skills",
            "Proficiency in Microsoft Office Suite",
            "Project management expertise",
            "Ability to work independently",
        ],
        "preferred_skills": [
            "Experience with data visualization tools",
            "Familiarity with Agile methodologies",
            "Knowledge of cloud computing platforms",
            "Previous experience in leadership roles",
            "Proficiency in a second language",
        ],
    }

    # Fetch category-specific data or default to generic
    data = category_specific_data.get(category, generic_data)

    # Randomly select items from the pools
    roles_responsibilities = random.sample(data["responsibilities"], k=random.randint(2, 5))
    required_skills = random.sample(data["required_skills"], k=random.randint(2, 5))
    preferred_skills = random.sample(data["preferred_skills"], k=random.randint(2, 4))

    return {
        "roles_responsibilities": ", ".join(roles_responsibilities),
        "required_skills": ", ".join(required_skills),
        "preferred_skills": ", ".join(preferred_skills),
    }

# Function to fetch jobs from Adzuna API
def fetch_adzuna_jobs():
    """Fetch up to 1000 jobs from Adzuna API."""
    job_list = []
    print("🔍 Fetching jobs from Adzuna API...")

    try:
        for category in CATEGORIES:
            for page in range(1, 6):
                url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
                params = {
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY,
                    "results_per_page": 50,
                    "what": category,
                    "content-type": "application/json"
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                for job in data.get("results", []):
                    job_title = job.get("title", "Unknown Job")
                    company_name = job.get("company", {}).get("display_name", "Unknown Company")
                    location = job.get("location", {}).get("display_name", "Remote")
                    details = generate_roles_and_skills(category)
           

                    # Ensure company account exists or create one
                    company, created = Company.objects.get_or_create(
                        company_name=company_name,
                        defaults={
                            "email": generate_unique_email(company_name),
                            "password": fake.password(),
                            "industry": category.capitalize(),
                            "phone": job.get("phone_number", fake.phone_number()),
                            "unique_id":generate_unique_company_id()  # Assigning the generated unique code
    
                        }
                    )
                    

                    job_list.append({
                        "job_title": job_title,
                        "company_name": job.get("company", {}).get("display_name", "Unknown Company"),
                        "location": job.get("location", {}).get("display_name", "Remote"),
                        "salary_range": f"{random.randint(23000 // 1000, 100000 // 1000) * 1000} GBP",
                        "job_overview": job.get("description", "No description available."),
                        "roles_responsibilities": details["roles_responsibilities"],
                        "required_skills": details["required_skills"],
                        "preferred_skills": details["preferred_skills"],
                        "company_overview": random.choice(WHY_JOIN_US_OPTIONS),
                    })

                if len(job_list) >= 150:
                    return job_list
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
    return job_list

def generate_clean_phone_number():
    """
    Generate a valid and clean phone number without extensions or invalid characters.

    Returns:
        str: A valid phone number in E.164 format or a fallback number.
    """
    while True:
        try:
            # Generate a random phone number
            raw_phone_number = fake.phone_number()

            # Remove any extensions or letters
            raw_phone_number = re.sub(r"[a-zA-ZxX]", "", raw_phone_number)

            # Parse the phone number using the phonenumbers library
            parsed_number = parse(raw_phone_number, None)  # None allows parsing in any international format

            # Validate the parsed phone number
            if is_possible_number(parsed_number) and is_valid_number(parsed_number):
                return format_number(parsed_number, PhoneNumberFormat.E164)

        except Exception:
            # If invalid, regenerate a new number
            continue

# Fallback number in case generation consistently fails
    return "+1234567890"

def generate_unique_company_id():
    """Generate a unique 5-character alphanumeric code for a company."""
    while True:
        # Generate a random 5-character code (letters and digits)
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Ensure it's unique by checking the database
<<<<<<< HEAD
        if not Company.objects.filter(unique_id=id).exists():
            return id
=======
        if not Company.objects.filter(unique_id=code).exists():
            return code
>>>>>>> 679a10d18f973b48e204d4b25ee73907734c3492

def generate_unique_email(company_name):
    """
    Generate a unique email for a company based on the company name.
    """
    base_email = f"{company_name.replace(' ', '').lower()}@example.com"
    counter = 1
    unique_email = base_email

    # Check if the email already exists in the database
    while Company.objects.filter(email=unique_email).exists():
        unique_email = f"{company_name.replace(' ', '').lower()}{counter}@example.com"
        counter += 1

    return unique_email
# Django Command
class Command(BaseCommand):
    help = "Fetches 150 job postings from Adzuna API and saves them to the database."

    def handle(self, *args, **kwargs):
        self.seed_users(100)  # Seed 100 users
        self.seed_jobs()      # Seed job postings
        '''
        for user_data in user_fixtures:
            self.create_known_users(user_data)
        self.stdout.write(self.style.SUCCESS("✅ Database seeding complete!"))
        '''

    '''
    def create_known_users(self, data):
        """Attempt to create a user and handle any exceptions."""
        try:
            if data['user_type'] == 'admin':
                # Create a superuser if the user_type is admin
                User.objects.create_superuser(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    user_type=data['user_type']  
                )
                print(f"Superuser created: {data['username']}")
            elif data['user_type'] == 'company':
                # Create a company user
                User.objects.create_user(
                    company_name=data['company_name'],
                    email=data['email'],
                    industry=data['industry'],
                    phone=data['phone'],
                    password=data['password'],
                    user_type=data['user_type'],
                    unique_id=data['unique_id']
<<<<<<< HEAD
=======
                  
>>>>>>> 679a10d18f973b48e204d4b25ee73907734c3492
                )
                print(f"Company created: {data['username']}")
            elif data['user_type'] == 'user':
                # Create a regular user
                User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone=data['phone'],
                    password=data['password'],
                    user_type=data['user_type']
                )
                print(f"User created: {data['username']}")
            else:
                print(f"Invalid user type: {data['user_type']}")
        except Exception as e:
            print(f"Error creating user {data['username']}: {e}")
            raise e  # Re-raise the error to prevent silent failures


    '''
    def seed_users(self, count):
        """Seed the User model with dummy data."""
        for _ in range(count):  # ✅ This should loop correctly
            email = fake.unique.email()  # Ensure unique email
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "phone": fake.phone_number(),
                    "password": fake.password(length=10),
                }
            )
            if created:
                print(f"✅ Created User: {user.first_name} {user.last_name} - {user.email}")
            else:
                print(f"⚠️ User {user.email} already exists, skipping...")


    def seed_jobs(self):

        job_count = 0

        job_postings = fetch_adzuna_jobs()
        for job in job_postings:
            try:
                JobPosting.objects.create(
                    job_title=job["job_title"],
                    company_name=job["company_name"],
                    location=job["location"],
                    salary_range=job["salary_range"],
                    contract_type=random.choice(["Full-time", "Part-time", "Apprenticeship", "Internship"]),
                    work_type=random.choice(["Remote", "Hybrid", "On-site"]),
                    job_overview=job["job_overview"],
                    education_required=random.choice(EDUCATION_OPTIONS),
                    perks=", ".join(random.sample(PERKS_OPTIONS, k=random.randint(3, 9))),
                    application_deadline=random.choice(APPLICATION_DEADLINE_OPTIONS),
                    roles_responsibilities=job["roles_responsibilities"],
                    required_skills=job["required_skills"],
                    preferred_skills=job["preferred_skills"],
                    company_overview=job["company_overview"],
                    why_join_us=random.choice(WHY_JOIN_US_OPTIONS),
                    company_reviews=round(random.uniform(3.5, 5.0), 1),
<<<<<<< HEAD
=======
                    child_company_name="",
                    required_documents="Updated CV",
                    

>>>>>>> 679a10d18f973b48e204d4b25ee73907734c3492
                )
                job_count += 1
                print(f"✅ Added: {job['job_title']} at {job['company_name']}")
            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                pass

        self.stdout.write(self.style.SUCCESS(f"✅ Success : {job_count}"))
    
