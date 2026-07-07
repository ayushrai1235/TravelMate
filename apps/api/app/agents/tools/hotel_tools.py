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


class SearchHotelsInput(BaseModel):
    location: str = Field(..., description="Location to search hotels near")
    budget_tier: str = Field(default="mid", description="Budget tier: budget, mid, premium")
    amenities: list[str] = Field(default_factory=list, description="Desired amenities")


@tool("search_hotels", args_schema=SearchHotelsInput)
async def search_hotels(location: str, budget_tier: str = "mid", amenities: list[str] = []) -> dict[str, Any]:
    """Search for hotels near a location via Google Maps Places API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        places = await maps.places_nearby(location, 5000, "lodging")
        hotels = []
        for p in places.get("places", []):
            hotels.append({
                "name": p.get("name", ""),
                "rating": p.get("rating", 0),
                "price_level": p.get("price_level", 0),
                "vicinity": p.get("vicinity", ""),
                "types": p.get("types", []),
                "confidence": "MEDIUM",
                "data_source": "Google Maps Places API",
            })
        return {"hotels": hotels, "dharamshalas": []}
    except Exception as e:
        logger.error(f"Hotel search tool error: {e}")
        return {"error": str(e), "hotels": [], "dharamshalas": []}
