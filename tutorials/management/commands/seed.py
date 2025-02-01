import os
import time
import requests
import random
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from google.cloud import language_v1
from tutorials.models.jobposting import JobPosting  
from tutorials.models.accounts import Company, User

# Set up Google Cloud API authentication (ensure you set up your credentials file)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your_google_api_key.json"

# Function to scrape job postings from Indeed

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.5",
}

CATEGORIES = [
    # Business & Management
    "business", "management", "operations", "project-management", "product-management",
    "strategy", "consulting", "administration", "supply-chain", "logistics",

    # Sales & Marketing
    "sales", "marketing", "digital-marketing", "content-marketing", "growth-marketing",
    "seo", "advertising", "affiliate-marketing", "public-relations", "branding",

    # Technology & IT
    "technology", "it", "software-development", "web-development", "frontend",
    "backend", "fullstack", "data-science", "artificial-intelligence", "machine-learning",
    "cybersecurity", "blockchain", "cloud-computing", "devops", "networking",

    # Design & Creative
    "design", "graphic-design", "ux", "ui", "product-design", 
    "animation", "illustration", "photography", "video-editing", "creative-writing",

    # Finance & Accounting
    "finance", "accounting", "financial-analyst", "investment-banking", "auditing",
    "risk-management", "taxation", "bookkeeping", "economics", "insurance",

    # Healthcare & Medical
    "healthcare", "medical", "nursing", "pharmacy", "psychology",
    "physiotherapy", "dentistry", "radiology", "veterinary", "mental-health",

    # Education & Training
    "education", "teaching", "training", "e-learning", "curriculum-development",
    "tutoring", "academic-research", "special-education", "language-teaching", "library-sciences",

    # Legal & Compliance
    "legal", "law", "paralegal", "compliance", "corporate-law",
    "intellectual-property", "contract-management", "regulatory-affairs", "tax-law", "litigation",

    # Science & Engineering
    "engineering", "mechanical-engineering", "electrical-engineering", "civil-engineering",
    "chemical-engineering", "aerospace", "biotechnology", "physics", "chemistry", "environmental-science",

    # Environmental & Sustainability
    "sustainability", "environmental", "climate-change", "renewable-energy",
    "conservation", "wildlife", "ecology", "agriculture", "urban-planning", "geography",

    # Customer Support & Services
    "customer-support", "customer-service", "technical-support", "call-center",
    "help-desk", "client-success", "account-management", "community-management",

    # Retail & Hospitality
    "retail", "hospitality", "food-service", "travel", "tourism",
    "event-management", "real-estate", "property-management", "logistics", "wholesale",

    # Startups & Entrepreneurship
    "startup", "entrepreneurship", "venture-capital", "innovation", "growth-hacking",

    # Human Resources & Recruiting
    "human-resources", "recruitment", "talent-acquisition", "employee-relations",
    "organizational-development", "payroll", "training-and-development",

    # Writing & Content Creation
    "writing", "content-creation", "copywriting", "editing", "technical-writing",
    "journalism", "blogging", "publishing", "transcription", "translation",

    # Trades & Technical Jobs
    "construction", "plumbing", "carpentry", "mechanics", "electrician",
    "welding", "automotive", "manufacturing", "maintenance", "heavy-machinery",

    # Non-Profit & NGO
    "non-profit", "ngo", "charity", "fundraising", "volunteering",
    "international-development", "social-work", "community-outreach",

    # Media & Communication
    "media", "communications", "broadcasting", "film", "radio",
    "podcasting", "public-speaking", "social-media", "influencer-marketing", "advertising",

    # Logistics & Transportation
    "transportation", "logistics", "shipping", "fleet-management", "supply-chain-management",
    "import-export", "aviation", "rail", "maritime", "warehousing"
]

def scrape_remote_ok_jobs():
    """Scrapes 100+ job postings from Remote OK across multiple categories."""
    job_list = []
    print("🔍 Starting to scrape jobs from Remote OK...")

    # Loop through categories to scrape different industries
    for category in CATEGORIES:
        url = f"https://remoteok.io/remote-{category}-jobs"
        print(f"📂 Scraping category: {category} - {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Error fetching jobs for {category}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Loop through job cards
        for job_card in soup.find_all("tr", class_="job"):
            try:
                job_title = job_card.find("h2").get_text(strip=True)
                company_name = job_card.find("h3").get_text(strip=True)
                location = job_card.find("div", class_="location").get_text(strip=True) if job_card.find("div", class_="location") else "Remote"

                job_list.append({
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "salary_range": "Not Disclosed",
                    "job_overview": f"Job details for {job_title} at {company_name}.",
                })

                
                # Stop after collecting 1000 jobs
                if len(job_list) >= 500:
                    print("✅ Collected 1000 jobs!")
                    return job_list

            except Exception as e:
                print(f"⚠️ Error processing a job card: {e}")
                continue

        # Add a delay between requests to avoid rate-limiting
        time.sleep(random.uniform(1, 3))

    print(f"✅ Successfully scraped {len(job_list)} jobs from Remote OK.")
    return job_list



# Function to extract skills and responsibilities using Google NLP API
def extract_skills_from_description(text):
    """Uses Google NLP API to extract job-related skills and responsibilities."""
    if not text:
        print("⚠️ Skipping NLP extraction: No job description provided.")
        return {"skills": [], "responsibilities": []}

    try:
        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = client.analyze_entities(document=document)
    except Exception as e:
        print(f"❌ Google NLP API Error: {e}")
        return {"skills": [], "responsibilities": []}

    skills = []
    responsibilities = []

    for entity in response.entities:
        if entity.type_ in [language_v1.Entity.Type.WORK_OF_ART, language_v1.Entity.Type.EVENT, language_v1.Entity.Type.SKILL, language_v1.Entity.Type.OTHER]:
            skills.append(entity.name)
        if entity.type_ in [language_v1.Entity.Type.JOB_TITLE, language_v1.Entity.Type.ORGANIZATION]:
            responsibilities.append(entity.name)

    return {
        "skills": list(set(skills)),  # Remove duplicates
        "responsibilities": list(set(responsibilities))
    }


# Function to fetch company details from Google Knowledge Graph API
def get_company_info(company_name):
    """Fetches company data from Google Knowledge Graph API."""
    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        "query": company_name,
        "key": "YOUR_GOOGLE_API_KEY",
        "limit": 1,
        "indent": True
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "itemListElement" in data and data["itemListElement"]:
            entity = data["itemListElement"][0]["result"]
            return {
                "name": entity.get("name"),
                "description": entity.get("description", "No description available"),
                "website": entity.get("url", "No website available")
            }
    except requests.RequestException as e:
        print(f"❌ Google Knowledge Graph API Error: {e}")
    return None


# Function to predict contract type based on job overview
def predict_contract_type(job_description):
    """Uses heuristics to determine contract type (Full-time, Part-time, Contract, etc.)."""
    keywords = ["full-time", "part-time", "contract", "freelance", "internship"]
    for keyword in keywords:
        if keyword.lower() in job_description.lower():
            return keyword.capitalize()
    return "Full-time"  # Default assumption


# Django Command to Seed Database
class Command(BaseCommand):
    help = "Fetches 100+ job postings from Remote OK and saves them in the database."

    def handle(self, *args, **kwargs):
        job_postings = scrape_remote_ok_jobs()

        for job in job_postings:
            try:
                JobPosting.objects.create(
                    job_title=job["job_title"],
                    company_name=job["company_name"],
                    location=job["location"],
                    salary_range=job.get("salary_range", "Not Disclosed"),
                    contract_type="Full-time",
                    job_overview=job.get("job_overview", "No overview available."),
                    education_required="Bachelor's Degree",
                    perks="Flexible working hours, Health insurance",
                    application_deadline="30 days from now",
                    company_overview=f"{job['company_name']} is a leading employer.",
                    why_join_us="Exciting career growth and benefits.",
                    company_reviews="4.5/5 rating"
                )
                print(f"✅ Added: {job['job_title']} at {job['company_name']}")
            except Exception as e:
                print(f"❌ Error inserting job into DB: {e}")

        self.stdout.write(self.style.SUCCESS("✅ Job fetching and seeding complete!"))