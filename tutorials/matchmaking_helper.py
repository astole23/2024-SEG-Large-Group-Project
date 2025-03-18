import os
import together
import math

# 📍 Define UK Regions
REGIONAL_MAPPING = {
    "London": ["London", "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden", "Croydon", "Ealing", 
               "Enfield", "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", 
               "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea", "Kingston upon Thames", "Lambeth", 
               "Lewisham", "Merton", "Newham", "Redbridge", "Richmond upon Thames", "Southwark", "Sutton", 
               "Tower Hamlets", "Waltham Forest", "Wandsworth", "Westminster"],

    "West Midlands": ["Birmingham", "Coventry", "Wolverhampton", "Dudley", "West Bromwich", "Solihull"],
    
    "Greater Manchester": ["Manchester", "Salford", "Stockport", "Bolton", "Rochdale", "Wigan", "Oldham"],
    
    "Merseyside": ["Liverpool", "Birkenhead", "St Helens", "Southport", "Wirral"],
    
    "South Yorkshire": ["Sheffield", "Doncaster", "Rotherham", "Barnsley"],
    
    "West Yorkshire": ["Leeds", "Bradford", "Huddersfield", "Wakefield"],
    
    "Tyne and Wear": ["Newcastle upon Tyne", "Sunderland", "Gateshead", "South Shields"],
    
    "East Midlands": ["Nottingham", "Leicester", "Derby", "Loughborough", "Northampton"],
    
    "South East": ["Reading", "Oxford", "Brighton", "Slough", "Maidstone", "Crawley", "Guildford", "Portsmouth"],
    
    "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee"],
    
    "Wales": ["Cardiff", "Swansea", "Newport", "Wrexham"],
    
    "Northern Ireland": ["Belfast", "Londonderry", "Newry"]
}

# Mapping city -> region for quick lookups
LOCATION_TO_REGION = {city: region for region, cities in REGIONAL_MAPPING.items() for city in cities}

def is_location_match(user_locations, job_location):
    """Adjust job score based on location match with user preferences."""
    if not user_locations or not job_location:
        print(f"❌ No location match: {job_location} (Penalty: -0.50)")
        return -0.50  

    # Normalize job location
    job_location_clean = clean_location(job_location)

    for user_loc in user_locations:
        user_loc_clean = clean_location(user_loc)

        # Exact match (cleaned)
        if job_location_clean == user_loc_clean:
            print(f"✅ Exact location match: {job_location} (Boost: +0.50)")
            return +0.50  

        # Regional match
        job_region = LOCATION_TO_REGION.get(job_location_clean, job_location_clean)
        user_region = LOCATION_TO_REGION.get(user_loc_clean, user_loc_clean)

        if job_region == user_region:
            print(f"🔹 Regional match: {job_location} → {user_loc} (Boost: +0.30)")
            return +0.30  

    print(f"❌ Location mismatch: {job_location} (Penalty: -0.50)")
    return -0.50    

def clean_location(job_location):
    """Normalize job location without changing case."""
    if not job_location:
        return None

    # Extract city name before the comma (if present)
    if ", " in job_location:
        job_location = job_location.split(",")[0].strip()  # Take only the first part before the comma

    # Check if this city belongs to a predefined region
    if job_location in LOCATION_TO_REGION:
        return LOCATION_TO_REGION[job_location]  # Return mapped region


    print(job_location)
    return job_location  # Return the cleaned city if no match is found


# Load API key from environment variables
api_key = os.getenv("TOGETHER_API_KEY")
together_client = together.Together(api_key=api_key)

def get_embeddings(text_list):
    """Batch request embeddings for multiple texts at once with error handling."""
    if not text_list or not all(isinstance(text, str) for text in text_list):
        print(f"❌ Invalid input for embeddings: {text_list}")
        return []

    print(f"🔍 Sending batch to Together AI: {text_list}")  # Debugging

    try:
        response = together.Embeddings.create(
            model="togethercomputer/m2-bert-80M-8k-retrieval",
            input=text_list
        )

        print(f"✅ Raw API Response: {response}")  # Log full API response

        embeddings = [item["embedding"] for item in response.get("data", [])]

        if not embeddings:
            print("❌ API returned empty embeddings. Skipping similarity calculation.")

        return embeddings

    except Exception as e:
        print(f"❌ API Request Failed: {str(e)}")
        return []


def cosine_similarity_manual(vec1, vec2):
    """Compute cosine similarity manually."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

def match_job_to_cv_together(job_title, cv_job_titles):
    """Match job title with CV job titles using Together AI embeddings in a single API call."""

    if not job_title or not cv_job_titles:
        return []

    # Step 1: Compute AI-based similarity scores
    all_texts = job_title + cv_job_titles
    embeddings = get_embeddings(all_texts)
    print(f"embeddings is: {embeddings}")

    job_embedding = embeddings[0]
    cv_embeddings = embeddings[1:]

    similarities = [cosine_similarity_manual(job_embedding, emb) for emb in cv_embeddings]

    # Step 2: Sort results by similarity
    return sorted(zip(cv_job_titles, similarities), key=lambda x: x[1], reverse=True)
