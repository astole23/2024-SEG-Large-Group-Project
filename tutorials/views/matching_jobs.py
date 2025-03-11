from django.shortcuts import render
from tutorials.models.jobposting import JobPosting
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


@login_required
def job_search(request):
    geolocator = Nominatim(user_agent="my_app", timeout=10)

    # Geocode a location (e.g., London)
    location = geolocator.geocode()

    # Check if location was found
    if location:
        print(f"Coordinates of London: {location.latitude}, {location.longitude}")
    else:
        print("Location not found")

    return render(request, 'job_search.html', {})