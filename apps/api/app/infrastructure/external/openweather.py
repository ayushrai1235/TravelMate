from typing import Any

import httpx

from app.core.config import settings
from app.infrastructure.cache.cache_keys import weather_key
from app.infrastructure.cache.cache_service import CacheService

ONE_CALL_URL = "https://api.openweathermap.org/data/3.0/onecall"


class WeatherService:
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def forecast(self, lat: float, lng: float, travel_date: str) -> dict[str, Any]:
        cache_key = weather_key(lat, lng, travel_date)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        api_key = settings.OPENWEATHER_API_KEY or settings.OPENWEATHERMAP_API_KEY
        if settings.MOCK_EXTERNAL_APIS or not api_key:
            result = self._mock_weather(travel_date)
        else:
            result = await self._openweather(lat, lng, api_key)

        await self.cache.set_json(cache_key, result, ttl_seconds=3600)
        return {**result, "cache_hit": False}

    def _mock_weather(self, travel_date: str) -> dict[str, Any]:
        return {
            "travel_date": travel_date,
            "summary": "Partly cloudy with a chance of afternoon showers",
            "temperature_c": {"min": 24, "max": 31},
            "rain_probability": 0.35,
            "uv_index": 6,
            "alerts": [],
            "source": "mock_openweather",
            "confidence": "MEDIUM",
        }

    async def _openweather(self, lat: float, lng: float, api_key: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(
                ONE_CALL_URL,
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": api_key,
                    "units": "metric",
                    "exclude": "minutely,hourly",
                },
            )
            response.raise_for_status()
        payload = response.json()
        first_day = payload.get("daily", [{}])[0]
        temp = first_day.get("temp", {})
        return {
            "summary": first_day.get("summary") or first_day.get("weather", [{}])[0].get("description"),
            "temperature_c": {"min": temp.get("min"), "max": temp.get("max")},
            "rain_probability": first_day.get("pop"),
            "uv_index": first_day.get("uvi"),
            "alerts": payload.get("alerts", []),
            "source": "OpenWeatherMap One Call API",
            "confidence": "HIGH",
        }
