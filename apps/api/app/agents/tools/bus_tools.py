from __future__ import annotations

import logging
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field

from app.infrastructure.external.bus_service import BusService
from app.infrastructure.cache.cache_service import CacheService
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchBusRoutesInput(BaseModel):
    origin: str = Field(..., description="Origin location or stop name")
    destination: str = Field(..., description="Destination location or stop name")
    date: str = Field(..., description="Travel date (YYYY-MM-DD)")


class FindNearestBusStopInput(BaseModel):
    location: str = Field(..., description="Location to search from")
    radius_m: int = Field(default=500, description="Search radius in meters")


@tool("search_gtfs_routes", args_schema=SearchBusRoutesInput)
async def search_gtfs_routes(origin: str, destination: str, date: str) -> dict[str, Any]:
    """Search GTFS feeds and Google Transit for bus routes between two points."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        buses = BusService(cache)
        origin_data = await buses._geocode_location(origin) if isinstance(buses._geocode_location, str) else None
        result = await buses.search_routes(origin, destination, date)
        return result
    except Exception as e:
        logger.error(f"Bus search tool error: {e}")
        return {"error": str(e), "routes": [], "ai_guidance": None, "fallback_used": True}


@tool("find_nearest_bus_stop", args_schema=FindNearestBusStopInput)
async def find_nearest_bus_stop(location: str, radius_m: int = 500) -> dict[str, Any]:
    """Find nearest bus stops to a location using Google Maps Places API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        from app.infrastructure.external.google_maps import GoogleMapsService
        maps = GoogleMapsService(cache)
        result = await maps.places_nearby(location, radius_m, "transit_station")
        bus_stops = [p for p in result.get("places", []) if "bus" in p.get("type", "").lower() or "transit" in p.get("type", "").lower()]
        return {"bus_stops": bus_stops}
    except Exception as e:
        logger.error(f"Find bus stop tool error: {e}")
        return {"error": str(e), "bus_stops": []}
