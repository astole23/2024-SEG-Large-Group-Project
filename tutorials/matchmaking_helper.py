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
        return -0.50  

    # Normalize job location
    job_location_clean = clean_location(job_location)

    for user_loc in user_locations:
        user_loc_clean = clean_location(user_loc)

        # Exact match (cleaned)
        if job_location_clean == user_loc_clean:
            return +0.50  

        # Regional match
        job_region = LOCATION_TO_REGION.get(job_location_clean, job_location_clean)
        user_region = LOCATION_TO_REGION.get(user_loc_clean, user_loc_clean)

        if job_region == user_region:
            return +0.30  
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


    return job_location  # Return the cleaned city if no match is found


# Load API key from environment variables
api_key = os.getenv("TOGETHER_API_KEY")
together_client = together.Together(api_key=api_key)

def get_embeddings(text_list):
    """Batch request embeddings for multiple texts at once with error handling."""
    if not text_list or not all(isinstance(text, str) for text in text_list):
        return []


    try:
        response = together.Embeddings.create(
            model="togethercomputer/m2-bert-80M-8k-retrieval",
            input=text_list
        )


        embeddings = [item["embedding"] for item in response.get("data", [])]

        return embeddings

    except Exception as e:
        return []


def cosine_similarity_manual(vec1, vec2):
    """Compute cosine similarity manually."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

def match_job_to_cv_together(cv_items, job_titles):
    """Match job titles using Together AI embeddings (CV → Job Titles)."""
    if not cv_items or not job_titles:
        print("⚠️ match_job_to_cv_together: Missing input data.")
        return []

    # Combine CV info into a single search string
    cv_query = " ".join(item.strip() for item in cv_items if item)
    if not cv_query:
        print("⚠️ match_job_to_cv_together: Empty CV query.")
        return []

    # Send CV query + job titles as input to get embeddings
    all_texts = [cv_query] + job_titles
    embeddings = get_embeddings(all_texts)

    if not embeddings or len(embeddings) < 2:
        print("❌ match_job_to_cv_together: Failed to get valid embeddings.")
        return []

    try:
        job_embedding = embeddings[0]
        job_title_embeddings = embeddings[1:]

        similarities = [
            cosine_similarity_manual(job_embedding, emb)
            for emb in job_title_embeddings
        ]

        # Pair job titles with their scores
        return sorted(zip(job_titles, similarities), key=lambda x: x[1], reverse=True)

    except Exception as e:
        print(f"❌ Error in similarity computation: {e}")
        return []
