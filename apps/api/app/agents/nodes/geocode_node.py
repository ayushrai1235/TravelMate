from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.cache.cache_service import CacheService
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)


async def geocode_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: Resolves text locations to coordinates via Google Maps Geocoding API."""
    logger.info("Executing geocode_node...")

    origin_text = state.get("origin", {}).get("text", "")
    dest_text = state.get("destination", {}).get("text", "")

    from redis.asyncio import Redis
    from app.core.config import settings
    
    redis_client = None
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        logger.warning("Redis unavailable, using memory-only cache for geocoding")

    cache = CacheService(redis_client)
    maps = GoogleMapsService(cache)

    errors = list(state.get("errors", []))
    geocoded_origin = None
    geocoded_destination = None

    try:
        geocoded_origin = await maps.geocode(origin_text)
        logger.info(f"Geocoded origin: {geocoded_origin}")
    except Exception as e:
        logger.error(f"Geocoding origin failed: {e}")
        errors.append({"agent": "geocode", "message": f"Failed to geocode origin '{origin_text}': {e}", "recoverable": False})

    try:
        geocoded_destination = await maps.geocode(dest_text)
        logger.info(f"Geocoded destination: {geocoded_destination}")
    except Exception as e:
        logger.error(f"Geocoding destination failed: {e}")
        errors.append({"agent": "geocode", "message": f"Failed to geocode destination '{dest_text}': {e}", "recoverable": False})

    if not geocoded_origin or not geocoded_destination:
        errors.append({"agent": "geocode", "message": "Cannot proceed without geocoded coordinates.", "recoverable": False})

    return {
        "geocoded_origin": geocoded_origin or {"lat": 0, "lng": 0, "name": origin_text, "resolved_name": origin_text},
        "geocoded_destination": geocoded_destination or {"lat": 0, "lng": 0, "name": dest_text, "resolved_name": dest_text},
        "errors": errors,
    }
