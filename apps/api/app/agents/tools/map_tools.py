from __future__ import annotations

import logging
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field

from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.cache.cache_service import CacheService
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeocodeInput(BaseModel):
    location: str = Field(..., description="Location name or address to geocode")


class ReverseGeocodeInput(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")


class DistanceMatrixInput(BaseModel):
    origins: str = Field(..., description="Origin location(s), comma-separated")
    destinations: str = Field(..., description="Destination location(s), comma-separated")


class PlacesNearbyInput(BaseModel):
    location: str = Field(..., description="Center location")
    radius_m: int = Field(default=5000, description="Search radius in meters")
    type: str = Field(default="hotel", description="Place type (hotel, temple, restaurant, etc.)")


@tool("geocode_location", args_schema=GeocodeInput)
async def geocode_location(location: str) -> dict[str, Any]:
    """Geocode a location name to coordinates using Google Maps Geocoding API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        result = await maps.geocode(location)
        return result
    except Exception as e:
        logger.error(f"Geocode tool error: {e}")
        return {"error": str(e), "lat": None, "lng": None, "name": location}


@tool("reverse_geocode", args_schema=ReverseGeocodeInput)
async def reverse_geocode(lat: float, lng: float) -> dict[str, Any]:
    """Reverse geocode coordinates to a human-readable address."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        result = await maps.reverse_geocode(lat, lng)
        return result
    except Exception as e:
        logger.error(f"Reverse geocode tool error: {e}")
        return {"error": str(e), "formatted_address": None}


@tool("distance_matrix", args_schema=DistanceMatrixInput)
async def distance_matrix(origins: str, destinations: str) -> dict[str, Any]:
    """Get distance and duration between origins and destinations via Google Maps Distance Matrix API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        result = await maps.distance_matrix(origins, destinations)
        return result
    except Exception as e:
        logger.error(f"Distance matrix tool error: {e}")
        return {"error": str(e), "distance_km": None, "duration_minutes": None}


@tool("places_nearby", args_schema=PlacesNearbyInput)
async def places_nearby(location: str, radius_m: int = 5000, type: str = "hotel") -> dict[str, Any]:
    """Search for nearby places (hotels, temples, restaurants) using Google Maps Places API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        result = await maps.places_nearby(location, radius_m, type)
        return result
    except Exception as e:
        logger.error(f"Places nearby tool error: {e}")
        return {"error": str(e), "places": []}
