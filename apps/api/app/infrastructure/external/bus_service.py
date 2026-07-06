from typing import Any

from app.infrastructure.cache.cache_keys import bus_key
from app.infrastructure.cache.cache_service import CacheService


class BusService:
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def search_routes(
        self,
        origin: dict[str, Any],
        destination: dict[str, Any],
        travel_date: str,
    ) -> dict[str, Any]:
        cache_key = bus_key(origin, destination, travel_date)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        result = {
            "travel_date": travel_date,
            "routes": [
                {
                    "mode": "BUS",
                    "operator": "State transport / local bus",
                    "origin_stop": f"{origin['name']} central bus stand",
                    "destination_stop": f"{destination['name']} bus stand",
                    "departure_window": "morning",
                    "duration_minutes": None,
                    "fare_inr": {"min": 120, "max": 350},
                    "source": "mock_gtfs_google_transit",
                    "confidence": "LOW",
                    "advisory": "Bus route guidance is estimated. Confirm schedule locally before travel.",
                }
            ],
            "source": "mock_gtfs_google_transit",
        }
        await self.cache.set_json(cache_key, result, ttl_seconds=86400)
        return {**result, "cache_hit": False}
