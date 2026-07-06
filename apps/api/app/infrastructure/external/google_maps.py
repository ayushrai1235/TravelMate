from math import asin, cos, radians, sin, sqrt
from typing import Any

import httpx

from app.core.config import settings
from app.infrastructure.cache.cache_keys import distance_key, geocode_key
from app.infrastructure.cache.cache_service import CacheService

GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

MOCK_LOCATIONS: dict[str, dict[str, Any]] = {
    "navsari": {"lat": 20.9467, "lng": 72.9520, "name": "Navsari, Gujarat", "country": "India"},
    "surat": {"lat": 21.1702, "lng": 72.8311, "name": "Surat, Gujarat", "country": "India"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "name": "Mumbai, Maharashtra", "country": "India"},
    "nashik": {"lat": 19.9975, "lng": 73.7898, "name": "Nashik, Maharashtra", "country": "India"},
    "trimbakeshwar": {"lat": 19.9322, "lng": 73.5291, "name": "Trimbakeshwar, Maharashtra", "country": "India"},
    "pune": {"lat": 18.5204, "lng": 73.8567, "name": "Pune, Maharashtra", "country": "India"},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714, "name": "Ahmedabad, Gujarat", "country": "India"},
    "vadodara": {"lat": 22.3072, "lng": 73.1812, "name": "Vadodara, Gujarat", "country": "India"},
    "delhi": {"lat": 28.6139, "lng": 77.2090, "name": "Delhi, India", "country": "India"},
}


class GoogleMapsService:
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def geocode(self, query: str) -> dict[str, Any]:
        normalized = query.strip()
        cache_key = geocode_key(normalized)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        if settings.MOCK_EXTERNAL_APIS or not settings.GOOGLE_MAPS_API_KEY:
            result = self._mock_geocode(normalized)
        else:
            result = await self._google_geocode(normalized)

        await self.cache.set_json(cache_key, result, ttl_seconds=604800)
        return {**result, "cache_hit": False}

    async def distance_matrix(self, origin: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
        cache_key = distance_key(origin, destination)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        if settings.MOCK_EXTERNAL_APIS or not settings.GOOGLE_MAPS_API_KEY:
            result = self._mock_distance(origin, destination)
        else:
            result = await self._google_distance(origin, destination)

        await self.cache.set_json(cache_key, result, ttl_seconds=86400)
        return {**result, "cache_hit": False}

    async def places(self, query: str, location: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if settings.MOCK_EXTERNAL_APIS or not settings.GOOGLE_MAPS_API_KEY:
            place_name = location["name"] if location else "destination"
            return [
                {
                    "name": f"Budget stay near {place_name}",
                    "rating": 4.1,
                    "price_level": "budget",
                    "source": "mock_places",
                    "confidence": "MEDIUM",
                },
                {
                    "name": f"Comfort hotel near {place_name}",
                    "rating": 4.3,
                    "price_level": "mid",
                    "source": "mock_places",
                    "confidence": "MEDIUM",
                },
            ]

        params: dict[str, Any] = {"query": query, "key": settings.GOOGLE_MAPS_API_KEY}
        if location:
            params["location"] = f"{location['lat']},{location['lng']}"
            params["radius"] = 5000
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(PLACES_URL, params=params)
            response.raise_for_status()
        payload = response.json()
        return [
            {
                "name": item.get("name"),
                "rating": item.get("rating"),
                "price_level": item.get("price_level"),
                "source": "Google Places API",
                "confidence": "MEDIUM",
            }
            for item in payload.get("results", [])[:5]
        ]

    def _mock_geocode(self, query: str) -> dict[str, Any]:
        normalized = query.strip().lower()
        match = MOCK_LOCATIONS.get(normalized)
        if match is None:
            for key, value in MOCK_LOCATIONS.items():
                if key in normalized or normalized in key:
                    match = value
                    break

        if match is None:
            return {
                "lat": 20.5937,
                "lng": 78.9629,
                "name": f"{query}, India",
                "country": "India",
                "confidence": "LOW",
                "source": "mock_geocoder_fallback",
            }

        return {**match, "confidence": "HIGH", "source": "mock_geocoder"}

    async def _google_geocode(self, query: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(
                GEOCODING_URL,
                params={"address": query, "region": "in", "key": settings.GOOGLE_MAPS_API_KEY},
            )
            response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        if not results:
            return {"query": query, "confidence": "LOW", "source": "Google Geocoding API", "not_found": True}

        first = results[0]
        location = first["geometry"]["location"]
        return {
            "lat": location["lat"],
            "lng": location["lng"],
            "name": first.get("formatted_address", query),
            "country": "India",
            "confidence": "HIGH",
            "source": "Google Geocoding API",
        }

    def _mock_distance(self, origin: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
        km = haversine_km(origin["lat"], origin["lng"], destination["lat"], destination["lng"])
        duration_min = max(5, round(km / 45 * 60))
        return {
            "distance_meters": round(km * 1000),
            "duration_minutes": duration_min,
            "source": "mock_distance_matrix",
            "confidence": "MEDIUM",
        }

    async def _google_distance(self, origin: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(
                DISTANCE_MATRIX_URL,
                params={
                    "origins": f"{origin['lat']},{origin['lng']}",
                    "destinations": f"{destination['lat']},{destination['lng']}",
                    "mode": "driving",
                    "region": "in",
                    "key": settings.GOOGLE_MAPS_API_KEY,
                },
            )
            response.raise_for_status()
        element = response.json()["rows"][0]["elements"][0]
        return {
            "distance_meters": element["distance"]["value"],
            "duration_minutes": round(element["duration"]["value"] / 60),
            "source": "Google Distance Matrix API",
            "confidence": "MEDIUM",
        }


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(a))
