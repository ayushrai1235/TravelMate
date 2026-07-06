import json
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_cache, get_session
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.external.bus_service import BusService
from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.external.openweather import WeatherService
from app.infrastructure.external.railway_api import RailwayService
from app.repositories.temple_repository import TempleRepository
from app.services.temple_service import TempleService
from app.services.trip_planning_service import TripPlanningService

router = APIRouter(prefix="/trips", tags=["trips"])


class GroupRequest(BaseModel):
    adults: int = Field(default=1, ge=1, le=50)
    children: int = Field(default=0, ge=0, le=50)
    seniors: int = Field(default=0, ge=0, le=50)


class TripPlanRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=255)
    destination: str = Field(min_length=2, max_length=255)
    travel_date: date
    departure_preference: str = Field(default="morning", max_length=50)
    return_time_preference: str | None = Field(default=None, max_length=50)
    trip_end_time_preference: str | None = Field(default=None, max_length=50)
    group: GroupRequest = Field(default_factory=GroupRequest)

    @field_validator("travel_date")
    @classmethod
    def travel_date_must_not_be_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("travel_date must be today or in the future")
        return value


@router.post("/plan")
async def plan_trip(
    payload: TripPlanRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    cache: CacheService = Depends(get_cache),
) -> StreamingResponse:
    maps = GoogleMapsService(cache)
    planner = TripPlanningService(
        cache=cache,
        maps=maps,
        railways=RailwayService(cache),
        weather=WeatherService(cache),
        buses=BusService(cache),
        temples=TempleService(TempleRepository(db), cache),
    )

    async def event_stream():
        request_payload = payload.model_dump(mode="json")
        request_payload["user_id"] = request.headers.get("x-user-id")
        request_payload["anon_session_id"] = request.headers.get("x-anon-session-id")
        async for event in planner.stream_core_plan(request_payload):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Request-ID": request.headers.get("x-request-id", ""),
        },
    )


@router.get("")
async def list_trips() -> dict[str, Any]:
    return {"data": [], "meta": {"total_count": 0, "has_more": False}}
