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

LOCATION_TO_REGION = {city: region for region, cities in REGIONAL_MAPPING.items() for city in cities}

def clean_location(job_location):
    """Normalize job location."""
    if not job_location:
        return None
    if ", " in job_location:
        job_location = job_location.split(",")[0].strip()
    return LOCATION_TO_REGION.get(job_location, job_location)

def is_location_match(user_locations, job_location):
    """Compute location match score."""
    if not user_locations or not job_location:
        return -0.50  
    job_location_clean = clean_location(job_location)
    for user_loc in user_locations:
        if job_location_clean == clean_location(user_loc):
            return 0.50
        if LOCATION_TO_REGION.get(job_location_clean) == LOCATION_TO_REGION.get(user_loc):
            return 0.30
    return -0.50
