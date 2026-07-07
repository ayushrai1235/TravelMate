from __future__ import annotations

import logging
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field

from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.cache.cache_service import CacheService
from app.repositories.temple_repository import TempleRepository
from app.infrastructure.database.connection import get_db
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class GetTempleByNameInput(BaseModel):
    name: str = Field(..., description="Temple name to search")


class GetTempleByCoordinatesInput(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    radius_m: int = Field(default=1000, description="Search radius in meters")


class GetFestivalScheduleInput(BaseModel):
    temple_id: str = Field(..., description="Temple database ID")
    date: str = Field(..., description="Date to check (YYYY-MM-DD)")


@tool("get_temple_by_name", args_schema=GetTempleByNameInput)
async def get_temple_by_name(name: str) -> dict[str, Any]:
    """Look up temple in TravelMate temple database by name."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from app.infrastructure.database.models import Temple
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            result = await session.execute(
                Temple.__table__.select().where(
                    Temple.name.ilike(f"%{name}%")
                ).limit(5)
            )
            temples = result.fetchall()
            if temples:
                return {"temple": temples[0]._mapping, "not_found": False}
            return {"temple": None, "not_found": True, "external_links": {"google_maps": f"https://maps.google.com/?q={name}"}}
    except Exception as e:
        logger.error(f"Temple lookup tool error: {e}")
        return {"error": str(e), "temple": None, "not_found": True}


@tool("get_temple_by_coordinates", args_schema=GetTempleByCoordinatesInput)
async def get_temple_by_coordinates(lat: float, lng: float, radius_m: int = 1000) -> dict[str, Any]:
    """Find temples near given coordinates."""
    try:
        cache = CacheService(Redis.from_url(settings.REDIS_URL, decode_responses=True))
        maps = GoogleMapsService(cache)
        places = await maps.places_nearby(f"{lat},{lng}", radius_m, "hindu_temple")
        temples = places.get("places", [])
        return {"temples": temples, "count": len(temples)}
    except Exception as e:
        logger.error(f"Temple coordinates tool error: {e}")
        return {"error": str(e), "temples": []}
