import os
import requests
import random
from django.core.management.base import BaseCommand
from tutorials.models.jobposting import JobPosting

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
    "Flexible dress code", "Monthly social events", "Annual health check-ups",
    "Employee recognition programs", "Innovation budget", "Quarterly team dinners",
    "Company-sponsored sports teams", "On-site library", "Study leave benefits",
    "Hybrid work environment", "Leadership training", "Sabbatical leave options",
    "Annual company trips", "Pet insurance", "Life insurance",
    "Health savings account (HSA)", "Dedicated workspace reimbursement",
    "Subscription to industry journals", "Discounts on company products/services"
]

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
    "Deadline: 10 working days from now", "Open for 3 months", "Last date to apply: 25th of next month",
    "On or before the first Friday of next month", "Closes mid-year", 
    "Submit applications by next Monday", "Hiring till 15th of next month",
    "Position expected to be filled by next month", "Last call for applications in 2 weeks",
    "Deadline extended to next month", "Final date: end of quarter",
    "Open until next fiscal quarter", "Hiring closes on last Friday of the month",
    "Deadline: First week of next month", "Application window: Open for 2 more months"
]

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
    "Work in an environment that encourages continuous learning.",
    "Join a team of highly skilled and passionate professionals.",
    "Be part of a company committed to sustainability and innovation.",
    "Take advantage of ample opportunities for upward mobility.",
    "Contribute to building innovative solutions for a better future.",
    "Be part of a close-knit, high-performing team.",
    "Enjoy perks such as free snacks, gym memberships, and team events.",
    "Grow in a role where your contributions truly matter.",
    "Work in a company with strong values and a clear vision.",
    "Join a team that thrives on collaboration and innovation.",
    "Take pride in being part of a highly respected brand.",
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
def generate_roles_and_skills():
    """Generate a broad set of roles, responsibilities, required skills, and preferred skills."""
    
    # Expanded pools of responsibilities, required skills, and preferred skills
    responsibilities_pool = [
        "Collaborate with team members to achieve project milestones.",
        "Develop and maintain technical documentation for projects.",
        "Analyze and resolve complex issues to ensure project success.",
        "Monitor and evaluate project progress to ensure timelines are met.",
        "Communicate effectively with stakeholders and clients.",
        "Participate in team meetings and provide strategic insights.",
        "Ensure compliance with company policies and industry standards.",
        "Support training and onboarding of new team members.",
        "Facilitate cross-departmental collaboration for key initiatives.",
        "Maintain up-to-date knowledge of industry trends and best practices.",
        "Conduct market research to identify opportunities for growth.",
        "Develop strategies to optimize operational efficiency.",
        "Prepare reports and presentations for senior management.",
        "Oversee quality assurance and testing processes.",
        "Identify and mitigate risks throughout the project lifecycle.",
        "Implement process improvements for enhanced productivity.",
        "Provide mentorship and guidance to junior staff members.",
        "Lead brainstorming sessions to develop innovative solutions.",
        "Coordinate with external vendors and service providers.",
        "Evaluate and manage project budgets effectively."
    ]

    required_skills_pool = [
        "Strong analytical and problem-solving skills",
        "Excellent communication and interpersonal skills",
        "Proficiency in project management tools (e.g., JIRA, Trello)",
        "Ability to work collaboratively in a team environment",
        "Expertise in data analysis and visualization tools",
        "Proficiency in programming languages like Python or Java",
        "Familiarity with cloud computing platforms (AWS, Azure, GCP)",
        "Knowledge of Agile and Scrum methodologies",
        "Strong organizational and time management abilities",
        "Proficiency in Microsoft Office Suite",
        "Ability to develop and manage budgets effectively",
        "Strong presentation and public speaking skills",
        "Familiarity with digital marketing and SEO tools",
        "Understanding of cybersecurity principles and practices",
        "Proficiency in database management systems (SQL, NoSQL)",
        "Experience with customer relationship management (CRM) tools",
        "Knowledge of machine learning and AI frameworks",
        "Ability to manage multiple priorities effectively",
        "Strong negotiation and conflict resolution skills",
        "Familiarity with supply chain and logistics management"
    ]

    preferred_skills_pool = [
        "Experience in leadership or supervisory roles",
        "Certification in project management (e.g., PMP, PRINCE2)",
        "Proficiency in additional programming languages (e.g., C++, R)",
        "Familiarity with DevOps tools (e.g., Jenkins, Docker, Kubernetes)",
        "Expertise in blockchain technologies and distributed systems",
        "Knowledge of business intelligence tools (e.g., Tableau, Power BI)",
        "Experience with big data technologies (e.g., Hadoop, Spark)",
        "Understanding of natural language processing (NLP) techniques",
        "Ability to work in fast-paced and dynamic environments",
        "Familiarity with e-commerce platforms and strategies",
        "Proficiency in designing and executing digital campaigns",
        "Expertise in automation and workflow optimization tools",
        "Experience with diversity and inclusion initiatives",
        "Knowledge of international business practices and regulations",
        "Understanding of sustainability and environmental impact practices",
        "Familiarity with hardware and embedded systems design",
        "Experience in strategic planning and roadmap development",
        "Proficiency in statistical analysis and modeling techniques",
        "Experience with financial analysis and forecasting",
        "Ability to mentor and train junior team members effectively"
    ]

    # Randomly generate roles, responsibilities, and skills
    roles_responsibilities = random.sample(responsibilities_pool, k=random.randint(5, 7))
    required_skills = random.sample(required_skills_pool, k=random.randint(4, 6))
    preferred_skills = random.sample(preferred_skills_pool, k=random.randint(3, 5))

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
                    details = generate_roles_and_skills()

                    job_list.append({
                        "job_title": job_title,
                        "company_name": job.get("company", {}).get("display_name", "Unknown Company"),
                        "location": job.get("location", {}).get("display_name", "Remote"),
                        "salary_range": f"{random.randint(30000, 100000)} GBP",
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


# Django Command
class Command(BaseCommand):
    help = "Fetches 150 job postings from Adzuna API and saves them to the database."

    def handle(self, *args, **kwargs):
        job_postings = fetch_adzuna_jobs()
        job_count = 0  # Counter for jobs successfully added

        for job in job_postings:
            try:
                JobPosting.objects.create(
                    job_title=job["job_title"],
                    company_name=job["company_name"],
                    location=job["location"],
                    salary_range=job["salary_range"],
                    contract_type="Full-time",
                    job_overview=job["job_overview"],
                    education_required=random.choice(EDUCATION_OPTIONS),
                    perks=", ".join(random.sample(PERKS_OPTIONS, k=random.randint(3, 9))),
                    application_deadline=random.choice(APPLICATION_DEADLINE_OPTIONS),
                    roles_responsibilities=job["roles_responsibilities"],
                    required_skills=job["required_skills"],
                    preferred_skills=job["preferred_skills"],
                    company_overview=job["company_overview"],
                    why_join_us=random.choice(WHY_JOIN_US_OPTIONS),
                    company_reviews=f"{random.uniform(3.5, 5.0):.1f}/5 rating",
                )
                job_count += 1
                print(f"✅ Added: {job['job_title']} at {job['company_name']}")
            except Exception as e:
                print(f"❌ Error: {e}")

        self.stdout.write(self.style.SUCCESS(f"✅ Success : {job_count}"))
