import os
import re
import requests
import random
import string
from django.core.management.base import BaseCommand
from tutorials.models.jobposting import JobPosting
import faker
from tutorials.models.accounts import CustomUser as User, CompanyUser as Company, CustomUser
from tutorials.models.standard_cv import UserCV
from phonenumbers import parse, is_possible_number, is_valid_number, PhoneNumberFormat, format_number


#Already generated list of users
user_fixtures = [
    {
        'username': 'JohnLTD',
        'company_name': 'JohnLTD',
        'email': 'johnltd@example.org',
        'industry': 'Construction',
        'phone': '+447652567298',
        'is_company': True,  # Ensures the unique_id is auto-generated in save()
        'user_type': 'company',
        'password': 'password'
    },
    {
        'username': 'janedoe',
        'email': 'jane.doe@example.org',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'phone': '+447866352809',
        # For normal users, we don't set is_company or company-specific fields.
        'user_type': 'user',
        'password': 'password'
    },
    {
        'username': 'admin',
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
    "business", "management", "sales", "marketing", "technology", "software-development",
    "engineering", "design", "finance", "accounting", "healthcare",
    "education", "legal", "customer-service", "retail", "hospitality", "construction",
    "media", "logistics", "human-resources", "writing", "consulting",  "data-science",
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

    # Define pools for each category
def generate_roles_and_skills(category):
    # Generate roles, responsibilities, required skills, and preferred skills based on the category

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
        "management": {
            "responsibilities": [
                "Lead and motivate a team to achieve company objectives.",
                "Develop and implement management strategies to improve performance.",
                "Monitor and assess team performance, providing feedback as needed.",
                "Manage budgets and allocate resources effectively.",
                "Communicate company goals to all team members.",
            ],
            "required_skills": [
                "Strong leadership and decision-making abilities",
                "Excellent interpersonal and communication skills",
                "Experience in project management",
                "Ability to work under pressure and meet deadlines",
                "Proficiency in management software (e.g., Asana, Trello)",
            ],
            "preferred_skills": [
                "Master's degree in management or related field",
                "Experience with Agile or Scrum methodologies",
                "Familiarity with performance management tools",
                "Knowledge of financial management and budgeting",
                "Experience in conflict resolution and team building",
            ],
        },
        "sales": {
            "responsibilities": [
                "Generate leads and build relationships with clients.",
                "Identify and pursue new sales opportunities.",
                "Present products and services to potential clients.",
                "Negotiate and close sales contracts.",
                "Provide post-sales support and maintain client relationships.",
            ],
            "required_skills": [
                "Strong negotiation and communication skills",
                "Ability to meet and exceed sales targets",
                "Customer-focused approach",
                "Proficiency in CRM software",
                "Experience in B2B or B2C sales",
            ],
            "preferred_skills": [
                "Experience in digital marketing and sales funnels",
                "Knowledge of sales analytics tools",
                "Familiarity with the product lifecycle",
                "Experience in the relevant industry",
                "Fluency in multiple languages",
            ],
        },
        "marketing": {
            "responsibilities": [
                "Develop and implement marketing campaigns.",
                "Analyze market trends and identify opportunities.",
                "Manage digital marketing efforts across multiple channels.",
                "Create and distribute marketing content.",
                "Monitor and report on marketing performance metrics.",
            ],
            "required_skills": [
                "Strong written and verbal communication skills",
                "Proficiency in digital marketing tools (e.g., Google Analytics, SEMrush)",
                "Knowledge of SEO and SEM strategies",
                "Experience with social media platforms and advertising",
                "Ability to analyze and interpret marketing data",
            ],
            "preferred_skills": [
                "Experience with email marketing and automation",
                "Creative skills for content creation (e.g., graphic design)",
                "Experience in branding and product positioning",
                "Knowledge of A/B testing and market research methods",
                "Familiarity with content management systems (e.g., WordPress)",
            ],
        },
        "technology": {
            "responsibilities": [
                "Develop, test, and maintain software applications.",
                "Collaborate with cross-functional teams to design solutions.",
                "Write clean, efficient, and scalable code.",
                "Troubleshoot technical issues and provide solutions.",
                "Keep up to date with the latest technology trends.",
            ],
            "required_skills": [
                "Proficiency in programming languages (e.g., Python, Java, JavaScript)",
                "Experience with databases and data management",
                "Strong problem-solving and analytical skills",
                "Knowledge of web development frameworks",
                "Familiarity with version control systems (e.g., Git)",
            ],
            "preferred_skills": [
                "Experience with cloud computing platforms (e.g., AWS, Azure)",
                "Knowledge of DevOps and automation tools",
                "Familiarity with machine learning and AI technologies",
                "Experience with cybersecurity principles",
                "Experience with mobile application development",
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
        "engineering": {
            "responsibilities": [
                "Design and develop engineering systems and processes.",
                "Analyze and test prototypes to ensure reliability and efficiency.",
                "Collaborate with cross-functional teams on product design.",
                "Monitor project timelines and ensure deadlines are met.",
                "Provide engineering support for troubleshooting and maintenance.",
            ],
            "required_skills": [
                "Proficiency in engineering design tools and CAD software",
                "Strong mathematical and analytical skills",
                "Experience in materials selection and testing",
                "Knowledge of engineering standards and regulations",
                "Excellent problem-solving abilities",
            ],
            "preferred_skills": [
                "Experience with industrial automation",
                "Familiarity with manufacturing processes",
                "Experience with systems engineering",
                "Knowledge of environmental regulations",
                "Strong project management skills",
            ],
        },
        "finance": {
            "responsibilities": [
                "Prepare financial reports and budgets.",
                "Analyze financial data and provide insights for decision-making.",
                "Monitor and manage cash flow.",
                "Ensure compliance with financial regulations.",
                "Advise senior management on financial strategy.",
            ],
            "required_skills": [
                "Strong analytical and mathematical skills",
                "Proficiency in financial software (e.g., QuickBooks, Excel)",
                "Knowledge of financial modeling and forecasting",
                "Experience with tax regulations and filings",
                "Ability to interpret financial statements",
            ],
            "preferred_skills": [
                "CPA or CFA certification",
                "Experience with mergers and acquisitions",
                "Knowledge of international finance",
                "Fluency in multiple languages",
                "Strong communication and negotiation skills",
            ],
        },
        "accounting": {
            "responsibilities": [
                "Prepare and maintain financial records.",
                "Ensure accuracy in financial statements and reports.",
                "Reconcile accounts and resolve discrepancies.",
                "Assist with budgeting and forecasting.",
                "Ensure compliance with accounting regulations and standards.",
            ],
            "required_skills": [
                "Proficiency in accounting software (e.g., QuickBooks, Xero)",
                "Strong attention to detail and accuracy",
                "Ability to manage multiple tasks and deadlines",
                "Knowledge of accounting principles and practices",
                "Experience with tax preparation and filings",
            ],
            "preferred_skills": [
                "CPA certification",
                "Experience with auditing and financial reviews",
                "Knowledge of IFRS standards",
                "Ability to work in a fast-paced environment",
                "Familiarity with financial planning and analysis",
            ],
        },
        "healthcare": {
            "responsibilities": [
                "Provide patient care and monitor health conditions.",
                "Diagnose and treat illnesses or injuries.",
                "Educate patients on health and wellness topics.",
                "Collaborate with medical teams for patient care plans.",
                "Maintain accurate medical records.",
            ],
            "required_skills": [
                "Strong medical knowledge and clinical skills",
                "Ability to work under pressure",
                "Excellent communication skills",
                "Attention to detail and strong organizational skills",
                "Empathy and compassion for patients",
            ],
            "preferred_skills": [
                "Experience with electronic health records (EHR) systems",
                "Knowledge of healthcare regulations and compliance",
                "Specialized certifications (e.g., CPR, ACLS)",
                "Experience in a healthcare leadership role",
                "Fluency in multiple languages",
            ],
        },
        "education": {
            "responsibilities": [
                "Develop and implement lesson plans.",
                "Teach students in a classroom setting.",
                "Evaluate student performance and provide feedback.",
                "Collaborate with colleagues and parents.",
                "Support students' personal and academic growth.",
            ],
            "required_skills": [
                "Strong communication and teaching skills",
                "Ability to adapt teaching methods to individual needs",
                "Classroom management skills",
                "Knowledge of educational technologies",
                "Ability to assess and evaluate student progress",
            ],
            "preferred_skills": [
                "Teaching certification",
                "Experience with special needs education",
                "Familiarity with online teaching platforms",
                "Knowledge of curriculum development",
                "Fluency in multiple languages",
            ],
        },
        "legal": {
            "responsibilities": [
                "Provide legal advice and counsel to clients.",
                "Draft and review contracts and legal documents.",
                "Represent clients in court or legal proceedings.",
                "Research legal issues and stay updated on laws.",
                "Negotiate settlements and dispute resolutions.",
            ],
            "required_skills": [
                "Strong knowledge of law and legal procedures",
                "Excellent verbal and written communication skills",
                "Attention to detail and analytical skills",
                "Ability to work under pressure and meet deadlines",
                "Negotiation and conflict resolution skills",
            ],
            "preferred_skills": [
                "Law degree and relevant legal certifications",
                "Experience in corporate or criminal law",
                "Knowledge of international law",
                "Experience in litigation and trial preparation",
                "Fluency in multiple languages",
            ],
        },
        "customer-service": {
            "responsibilities": [
                "Provide assistance to customers and resolve inquiries.",
                "Handle complaints and provide effective solutions.",
                "Ensure customer satisfaction and maintain relationships.",
                "Process orders, returns, and exchanges.",
                "Provide product and service information to customers.",
            ],
            "required_skills": [
                "Excellent communication and problem-solving skills",
                "Ability to handle challenging situations calmly",
                "Strong interpersonal and active listening skills",
                "Experience with customer service software (e.g., Zendesk)",
                "Patience and empathy towards customers",
            ],
            "preferred_skills": [
                "Experience in customer support or call center roles",
                "Knowledge of CRM tools and systems",
                "Fluency in multiple languages",
                "Experience with conflict resolution",
                "Ability to work in a fast-paced environment",
            ],
        },
        "retail": {
            "responsibilities": [
                "Assist customers with product selection and purchases.",
                "Manage stock and inventory levels.",
                "Process transactions and handle cash.",
                "Maintain a clean and organized store environment.",
                "Provide excellent customer service and handle complaints.",
            ],
            "required_skills": [
                "Strong customer service skills",
                "Basic math skills for handling transactions",
                "Knowledge of product features and benefits",
                "Ability to work in a fast-paced environment",
                "Experience in point-of-sale (POS) systems",
            ],
            "preferred_skills": [
                "Experience in retail management",
                "Knowledge of merchandising and inventory management",
                "Fluency in multiple languages",
                "Experience with e-commerce platforms",
                "Knowledge of store safety and security procedures",
            ],
        },
        "hospitality": {
            "responsibilities": [
                "Provide excellent customer service to guests.",
                "Ensure that facilities and services meet guest expectations.",
                "Handle guest inquiries, complaints, and special requests.",
                "Coordinate events and services for guests.",
                "Maintain cleanliness and organization of the property.",
            ],
            "required_skills": [
                "Strong communication and customer service skills",
                "Ability to work under pressure and handle multiple tasks",
                "Attention to detail and problem-solving abilities",
                "Knowledge of hospitality industry standards",
                "Experience in event planning or coordination",
            ],
            "preferred_skills": [
                "Experience in hospitality management",
                "Knowledge of hotel booking systems",
                "Fluency in multiple languages",
                "Experience with food and beverage management",
                "Ability to work flexible hours, including weekends",
            ],
        },
        "construction": {
            "responsibilities": [
                "Plan and supervise construction projects from start to finish.",
                "Ensure compliance with safety regulations and building codes.",
                "Manage construction crews and subcontractors.",
                "Monitor project progress and budgets.",
                "Ensure quality control throughout the project.",
            ],
            "required_skills": [
                "Knowledge of construction methods and techniques",
                "Strong project management skills",
                "Experience with construction tools and equipment",
                "Ability to read and interpret blueprints and drawings",
                "Familiarity with safety standards and regulations",
            ],
            "preferred_skills": [
                "Construction management degree",
                "Experience with project management software",
                "Ability to lead teams effectively",
                "Knowledge of sustainable building practices",
                "Experience in commercial or residential construction",
            ],
        },
        "media": {
            "responsibilities": [
                "Create and manage media content for various platforms.",
                "Develop and implement media campaigns.",
                "Analyze media trends and audience insights.",
                "Collaborate with creative teams to produce content.",
                "Manage relationships with media outlets and partners.",
            ],
            "required_skills": [
                "Strong communication and writing skills",
                "Experience with media production tools (e.g., Adobe Creative Suite)",
                "Knowledge of social media platforms and trends",
                "Ability to analyze and interpret media metrics",
                "Experience with content marketing and distribution",
            ],
            "preferred_skills": [
                "Experience in broadcast or print journalism",
                "Knowledge of digital media strategies",
                "Familiarity with SEO and SEM",
                "Creative skills for video and audio production",
                "Experience in public relations and media outreach",
            ],
        },
        "logistics": {
            "responsibilities": [
                "Manage the movement of goods and materials.",
                "Coordinate shipments and deliveries to ensure timely arrival.",
                "Track inventory levels and manage stock.",
                "Optimize supply chain processes for efficiency.",
                "Negotiate with suppliers and third-party vendors.",
            ],
            "required_skills": [
                "Strong organizational and multitasking abilities",
                "Knowledge of logistics management software",
                "Excellent communication and negotiation skills",
                "Ability to work under pressure and meet deadlines",
                "Experience with inventory control and supply chain management",
            ],
            "preferred_skills": [
                "Experience with warehouse management systems (WMS)",
                "Fluency in multiple languages",
                "Experience with freight and shipping regulations",
                "Knowledge of international logistics",
                "Ability to manage large-scale distribution networks",
            ],
        },
        "human-resources": {
            "responsibilities": [
                "Manage recruitment and hiring processes.",
                "Develop and implement employee training programs.",
                "Handle employee relations and resolve conflicts.",
                "Ensure compliance with labor laws and company policies.",
                "Support employee development and performance management.",
            ],
            "required_skills": [
                "Strong interpersonal and communication skills",
                "Knowledge of HR policies and labor laws",
                "Experience with recruitment and onboarding",
                "Strong problem-solving and conflict resolution skills",
                "Ability to handle sensitive information with discretion",
            ],
            "preferred_skills": [
                "Experience with HR software (e.g., Workday, BambooHR)",
                "Certifications in HR management (e.g., SHRM-CP)",
                "Experience in employee engagement and retention strategies",
                "Fluency in multiple languages",
                "Experience in performance management and coaching",
            ],
        },
        "writing": {
            "responsibilities": [
                "Create content for blogs, websites, and other publications.",
                "Research and write articles on various topics.",
                "Edit and proofread content to ensure clarity and accuracy.",
                "Collaborate with editors and designers on content production.",
                "Meet deadlines for content delivery.",
            ],
            "required_skills": [
                "Strong writing and editing skills",
                "Ability to research and create compelling content",
                "Attention to detail and accuracy",
                "Experience with content management systems (e.g., WordPress)",
                "Ability to write for various audiences and formats",
            ],
            "preferred_skills": [
                "Experience with SEO and keyword research",
                "Knowledge of content marketing strategies",
                "Fluency in multiple languages",
                "Experience with multimedia content (e.g., video, audio)",
                "Ability to write in different writing styles (e.g., technical, creative)",
            ],
        },
        "consulting": {
            "responsibilities": [
                "Provide expert advice to organizations on business issues.",
                "Analyze client needs and develop tailored strategies.",
                "Conduct market research and competitor analysis.",
                "Develop and present reports and recommendations to clients.",
                "Assist in implementing solutions and strategies.",
            ],
            "required_skills": [
                "Strong analytical and problem-solving skills",
                "Excellent communication and presentation abilities",
                "Ability to manage client relationships",
                "Knowledge of business operations and strategy",
                "Experience with data analysis and market research",
            ],
            "preferred_skills": [
                "Consulting certification or relevant experience",
                "Experience in a specific industry (e.g., finance, healthcare)",
                "Fluency in multiple languages",
                "Experience with project management tools",
                "Ability to manage multiple clients and projects",
            ],
        },
        "data-science": {
            "responsibilities": [
                "Analyze large datasets to identify trends and insights.",
                "Develop machine learning models for data-driven decision-making.",
                "Create data visualizations to communicate findings.",
                "Collaborate with cross-functional teams to define data needs.",
                "Clean and preprocess data for analysis.",
            ],
            "required_skills": [
                "Proficiency in programming languages (e.g., Python, R)",
                "Experience with data analysis and visualization tools",
                "Knowledge of machine learning algorithms and frameworks",
                "Strong statistical and analytical skills",
                "Experience with data wrangling and preprocessing",
            ],
            "preferred_skills": [
                "Experience with big data tools (e.g., Hadoop, Spark)",
                "Knowledge of deep learning frameworks (e.g., TensorFlow, PyTorch)",
                "Familiarity with cloud platforms (e.g., AWS, GCP)",
                "Experience with SQL and NoSQL databases",
                "Fluency in multiple languages",
            ],
        },
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
        while len(job_list) < 150:
            category = random.choice(CATEGORIES)
            
            for page in range(1, 6):
                url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
                params = {
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY,
                    "results_per_page": 50,
                    "what": category,
                    "content-type": "application/json"
                }

                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                except Exception as e:
                    print(f"Error fetching from Adzuna for category {category}, page {page}: {e}")
                    break

                for job in data.get("results", []):
                    job_title = job.get("title", "Unknown Job")
                    company_name = job.get("company", {}).get("display_name", "Unknown Company")
                    location = job.get("location", {}).get("display_name", "Remote")
                    details = generate_roles_and_skills(category)

                    # Look up any companies with this name
                    companies = Company.objects.filter(company_name=company_name)
                    if companies.exists():
                        company = companies.first()  # Use existing company
                        created = False
                    else:
                        company = Company.objects.create(
                            username=generate_unique_company_username(company_name),
                            company_name = company_name,
                            email=generate_unique_email(company_name),
                            password=fake.password(),
                            industry=category.capitalize(),
                            phone=job.get("phone_number", fake.phone_number()),
                            unique_id=generate_unique_company_id(),
                            is_company = True
                        )
                        created = True
                        print(f"✅ Created new company: {company.company_name}, Industry: {company.industry}, Email: {company.email}")

                    

                        job_list.append({
                            "job_title": job_title,
                            "company_name": company_name,
                            "location": location,
                            "salary_range": random.randint(23000 // 1000, 100000 // 1000) * 1000,
                            "job_overview": job.get("description", "No description available."),
                            "roles_responsibilities": details["roles_responsibilities"],
                            "required_skills": details["required_skills"],
                            "preferred_skills": details["preferred_skills"],
                            "company_overview": random.choice(WHY_JOIN_US_OPTIONS),
                        })

                        if len(job_list) >= 150:
                            break  # Exit early from job loop

                if len(job_list) >= 150:
                    break  # Exit early from page loop if needed
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
        # Generate a random 8-character code (letters and digits)
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Ensure it's unique by checking the database
        if not Company.objects.filter(unique_id=id).exists():
            return id

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

def generate_unique_company_username(company_name):
    base_username = company_name.replace(" ", "").lower()
    username = base_username
    counter = 1
    while Company.objects.filter(username=username).exists():
         username = f"{base_username}{counter}"
         counter += 1
    return username



# Django Command
class Command(BaseCommand):
    help = "Fetches 150 job postings from Adzuna API and saves them to the database."

    def handle(self, *args, **kwargs):
        self.seed_users(100)  # Seed 100 users
        self.seed_jobs()      # Seed job postings
        self.create_known_users(user_fixtures)  # Create known users

    
    def create_known_users(self, data):
        for fixture in user_fixtures:
            user_type = fixture.pop('user_type', 'user')
            raw_password = fixture.pop('password')
            # Pop is_company if provided, defaulting to False for non-company accounts.
            is_company = fixture.pop('is_company', False)

            username = fixture.get('username')

            # Create users based on their type.
            if user_type == 'company':
                # For company accounts, ensure the flag is set.
                fixture['is_company'] = True
                user, created = Company.objects.get_or_create(username=username, defaults=fixture)
            elif user_type == 'admin':
                # Admin accounts are created as CustomUser with superuser and staff flags.
                fixture['is_company'] = False
                user, created = CustomUser.objects.get_or_create(username=username, defaults=fixture)
                if created:
                    user.is_staff = True
                    user.is_superuser = True
            else:
                # For normal users, ensure is_company remains False.
                fixture['is_company'] = False
                user, created = User.objects.get_or_create(username=username, defaults=fixture)
                if user_type == "user":
                    UserCV.objects.update_or_create(
                        user=user,
                        defaults={
                            "personal_info": {
                                "fullName": f"{user.first_name} {user.last_name}",
                                "email": user.email,
                                "phone": user.phone,
                                "address": "123 University St, London, UK"
                            },
                            "key_skills": "Problem Solving, Teamwork, Time Management",
                            "technical_skills": "Python, Django, PostgreSQL, HTML, CSS",
                            "languages": "English, French",
                            "education": [
                                {
                                    "university": "University of Oxford",
                                    "degreeType": "Bachelor's",
                                    "fieldOfStudy": "Computer Science",
                                    "grade": "1st Class Honours",
                                    "dates": "2018 - 2021",
                                    "modules": "Algorithms, Data Structures, AI"
                                },
                                {
                                    "university": "University of Cambridge",
                                    "degreeType": "Master's",
                                    "fieldOfStudy": "Artificial Intelligence",
                                    "grade": "Distinction",
                                    "dates": "2021 - 2022",
                                    "modules": "Machine Learning, NLP, Deep Learning"
                                }
                            ],
                            "work_experience": [
                                {
                                    "employer": "Google",
                                    "jobTitle": "Software Engineering Intern",
                                    "dates": "Summer 2021",
                                    "responsibilities": "Built internal tools using Python and Flask."
                                },
                                {
                                    "employer": "Meta",
                                    "jobTitle": "Backend Developer",
                                    "dates": "2022 - 2023",
                                    "responsibilities": "Worked on REST APIs and database optimization."
                                }
                            ]
                        }
                    )

            if created:
                user.set_password(raw_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            else:
                self.stdout.write(self.style.WARNING(f"User already exists: {username}"))

    def seed_users(self, count):
        """Seed the User model with dummy data."""
        for _ in range(count):  # ✅ This should loop correctly
            email = fake.unique.email()  # Ensure unique email
            username = generate_unique_company_username(email)
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "phone": fake.phone_number(),
                    "password": fake.password(length=10),
                    "username": username,
                }

                
            )
            if created:
                print(f"✅ Created User: {user.first_name} {user.last_name} - {user.email}")
            else:
                print(f"⚠️ User {user.email} already exists, skipping...")


    def seed_jobs(self):

        job_count = 0

        job_postings = fetch_adzuna_jobs()
      
        existing_companies = User.objects.filter(is_company=True)

# Check if there are any existing companies
        if existing_companies.exists():
            existing_companies_list = list(existing_companies)  # Convert queryset to list
            for job in job_postings:
                try:
                    company = random.choice(existing_companies_list)  # Choose a random company
                    
                    JobPosting.objects.create(
                        job_title=job["job_title"],
                        company=company,  
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
                        company_overview=random.choice(WHY_JOIN_US_OPTIONS),
                        why_join_us=random.choice(WHY_JOIN_US_OPTIONS),
                        company_reviews=round(random.uniform(3.5, 5.0), 1),
                        required_documents="Updated CV",
                    )
                    job_count += 1
                    print(f"✅ Added: {job['job_title']} at {company.company_name}")
                except Exception as e:
                    print(f"❌ Error: {e}")
        else:
            print("no companies")
