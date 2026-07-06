from typing import Any

import httpx

from app.core.config import settings
from app.infrastructure.cache.cache_keys import trains_key
from app.infrastructure.cache.cache_service import CacheService

RAILWAY_SEARCH_URL = "https://railwayapi.p.rapidapi.com/searchTrain"

MOCK_STATIONS = {
    "navsari": "NVS",
    "surat": "ST",
    "mumbai": "MMCT",
    "nashik": "NK",
    "trimbakeshwar": "NK",
    "pune": "PUNE",
    "ahmedabad": "ADI",
    "vadodara": "BRC",
    "delhi": "NDLS",
}


class RailwayService:
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def search_trains(self, origin_name: str, destination_name: str, travel_date: str) -> dict[str, Any]:
        origin = self.nearest_station_code(origin_name)
        destination = self.nearest_station_code(destination_name)
        cache_key = trains_key(origin, destination, travel_date)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        if settings.MOCK_EXTERNAL_APIS or not settings.RAILWAY_API_KEY:
            result = self._mock_trains(origin, destination, travel_date)
        else:
            result = await self._rapidapi_trains(origin, destination, travel_date)

        await self.cache.set_json(cache_key, result, ttl_seconds=1800)
        return {**result, "cache_hit": False}

    def nearest_station_code(self, location_name: str) -> str:
        normalized = location_name.strip().lower()
        if normalized in MOCK_STATIONS:
            return MOCK_STATIONS[normalized]
        for key, value in MOCK_STATIONS.items():
            if key in normalized or normalized in key:
                return value
        return normalized[:4].upper()

    def _mock_trains(self, origin: str, destination: str, travel_date: str) -> dict[str, Any]:
        if origin == destination:
            trains: list[dict[str, Any]] = []
        else:
            trains = [
                {
                    "train_number": "19004",
                    "train_name": "Khandesh Express",
                    "origin_station": origin,
                    "destination_station": destination,
                    "departure_time": "06:15",
                    "arrival_time": "12:35",
                    "duration_minutes": 380,
                    "classes": ["SL", "3A", "2A"],
                    "fare_inr": {"SL": 180, "3A": 520, "2A": 760},
                    "running_status": None,
                    "source": "mock_railway_api",
                    "confidence": "MEDIUM",
                },
                {
                    "train_number": "12934",
                    "train_name": "Karnavati Express",
                    "origin_station": origin,
                    "destination_station": destination,
                    "departure_time": "09:40",
                    "arrival_time": "15:55",
                    "duration_minutes": 375,
                    "classes": ["2S", "CC"],
                    "fare_inr": {"2S": 160, "CC": 640},
                    "running_status": None,
                    "source": "mock_railway_api",
                    "confidence": "MEDIUM",
                },
            ]

        return {
            "origin_station": origin,
            "destination_station": destination,
            "travel_date": travel_date,
            "trains": trains,
            "source": "mock_railway_api",
        }

    async def _rapidapi_trains(self, origin: str, destination: str, travel_date: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(
                RAILWAY_SEARCH_URL,
                params={"from": origin, "to": destination, "date": travel_date},
                headers={
                    "X-RapidAPI-Key": settings.RAILWAY_API_KEY,
                    "X-RapidAPI-Host": settings.RAILWAY_API_HOST,
                },
            )
            response.raise_for_status()

        return {
            "origin_station": origin,
            "destination_station": destination,
            "travel_date": travel_date,
            "trains": response.json().get("trains", []),
            "source": "RailwayAPI.in/RapidAPI",
        }
