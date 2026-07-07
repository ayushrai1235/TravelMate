import json
from datetime import date
from typing import Any, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_cache, get_session
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.external.bus_service import BusService
from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.external.openweather import WeatherService
from app.repositories.temple_repository import TempleRepository
from app.services.temple_service import TempleService
from app.agents.orchestrator import create_trip_planning_graph, get_initial_state
from app.agents.memory import ChatMemoryService

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
    preferences: Any = None

    @field_validator("travel_date")
    @classmethod
    def travel_date_must_not_be_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("travel_date must be today or in the future")
        return value

    @model_validator(mode="before")
    @classmethod
    def normalize_preferences(cls, data: Any) -> Any:
        if isinstance(data, dict) and "preferences" in data:
            prefs = data["preferences"]
            if isinstance(prefs, list):
                data = {**data, "preferences": {"budget_tier": "mid", "accessibility": False, "interests": prefs}}
        return data


@router.post("/plan")
async def plan_trip(
    payload: TripPlanRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    cache: CacheService = Depends(get_cache),
) -> StreamingResponse:
    # Build the LangGraph orchestrator graph
    graph = create_trip_planning_graph()

    # Convert request to initial state
    initial_state = get_initial_state(payload.model_dump(mode="json"))

    async def event_stream():
        try:
            # Stream the graph execution
            async for event in graph.astream(initial_state, config={"configurable": {"thread_id": f"trip_{payload.origin[:10]}_{payload.destination[:10]}_{payload.travel_date}"}}, stream_mode="updates"):
                for event_name, event_state in event.items():
                    yield f"data: {json.dumps({
                        "type": "status",
                        "message": f"Processing: {event_name}",
                        "node": event_name,
                    }, default=str)}\n\n"

            # Get final state
            final_state = await graph.aget_state(config={"configurable": {"thread_id": f"trip_{payload.origin[:10]}_{payload.destination[:10]}_{payload.travel_date}"}})
            
            if final_state and final_state.values.get("itinerary"):
                yield f"data: {json.dumps({
                    "type": "complete",
                    "itinerary": final_state.values["itinerary"],
                }, default=str)}\n\n"
            else:
                yield f"data: {json.dumps({
                    "type": "error",
                    "message": "Trip planning failed. Please try again.",
                }, default=str)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({
                "type": "error",
                "message": str(e),
            }, default=str)}\n\n"

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
