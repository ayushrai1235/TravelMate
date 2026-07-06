from collections.abc import AsyncGenerator
from datetime import date
from typing import Any

from app.infrastructure.cache.cache_keys import itinerary_key
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.external.bus_service import BusService
from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.external.openweather import WeatherService
from app.infrastructure.external.railway_api import RailwayService
from app.services.temple_service import TempleService


class TripPlanningService:
    def __init__(
        self,
        cache: CacheService,
        maps: GoogleMapsService,
        railways: RailwayService,
        weather: WeatherService,
        buses: BusService,
        temples: TempleService,
    ):
        self.cache = cache
        self.maps = maps
        self.railways = railways
        self.weather = weather
        self.buses = buses
        self.temples = temples

    async def stream_core_plan(self, request: dict[str, Any]) -> AsyncGenerator[dict[str, Any], None]:
        cache_key = itinerary_key(request)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            yield {"type": "status", "message": "Loaded cached core data.", "cache_hit": True}
            yield {"type": "complete", "itinerary": cached}
            return

        yield {"type": "status", "message": "Geocoding locations..."}
        origin = await self.maps.geocode(request["origin"])
        destination = await self.maps.geocode(request["destination"])

        yield {"type": "status", "message": "Checking distance and transport data..."}
        distance = await self.maps.distance_matrix(origin, destination)
        trains = await self.railways.search_trains(origin["name"], destination["name"], request["travel_date"])
        buses = await self.buses.search_routes(origin, destination, request["travel_date"])

        yield {"type": "status", "message": "Fetching weather and destination context..."}
        origin_weather = await self.weather.forecast(origin["lat"], origin["lng"], request["travel_date"])
        destination_weather = await self.weather.forecast(
            destination["lat"],
            destination["lng"],
            request["travel_date"],
        )
        temple_matches = await self.temples.search_temples(
            query=request["destination"],
            city=destination["name"].split(",")[0],
            limit=5,
        )

        itinerary = {
            "phase": "core_data",
            "status": "ready_for_ai_orchestration",
            "origin": origin,
            "destination": destination,
            "travel_date": request["travel_date"],
            "departure_preference": request.get("departure_preference", "morning"),
            "group": request.get("group", {"adults": 1, "children": 0, "seniors": 0}),
            "distance": distance,
            "transport_options": {
                "trains": trains,
                "buses": buses,
            },
            "context": {
                "weather": {
                    "origin": origin_weather,
                    "destination": destination_weather,
                },
                "temples": temple_matches,
            },
            "confidence": {
                "overall": "MEDIUM",
                "note": "Phase 2 returns sourced core data. Full AI itinerary synthesis begins in Phase 3.",
            },
        }
        await self.cache.set_json(cache_key, itinerary, ttl_seconds=1800)
        yield {"type": "context", "weather": itinerary["context"]["weather"]}
        yield {"type": "complete", "itinerary": itinerary}
