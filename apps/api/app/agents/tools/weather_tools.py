from __future__ import annotations

import logging
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field

from app.infrastructure.external.openweather import WeatherService
from app.infrastructure.cache.cache_service import CacheService
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherForecastInput(BaseModel):
    lat: float = Field(..., description="Latitude of the location")
    lng: float = Field(..., description="Longitude of the location")
    date: str = Field(..., description="Date for forecast (YYYY-MM-DD)")


class WeatherAlertsInput(BaseModel):
    lat: float = Field(..., description="Latitude of the location")
    lng: float = Field(..., description="Longitude of the location")


@tool("get_weather_forecast", args_schema=WeatherForecastInput)
async def get_weather_forecast(lat: float, lng: float, date: str) -> dict[str, Any]:
    """Get 7-day weather forecast for coordinates via OpenWeatherMap API."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        weather = WeatherService(cache)
        result = await weather.forecast(lat, lng, date)
        return result
    except Exception as e:
        logger.error(f"Weather forecast tool error: {e}")
        return {"error": str(e), "forecasts": [], "alerts": []}


@tool("get_weather_alerts", args_schema=WeatherAlertsInput)
async def get_weather_alerts(lat: float, lng: float) -> dict[str, Any]:
    """Get active weather alerts/advisories for a location."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        weather = WeatherService(cache)
        result = await weather.get_one_call(lat, lng)
        alerts = result.get("alerts", []) if isinstance(result, dict) else []
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Weather alerts tool error: {e}")
        return {"error": str(e), "alerts": []}
