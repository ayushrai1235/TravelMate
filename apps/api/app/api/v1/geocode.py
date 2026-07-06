from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.api_errors import error_response
from app.core.dependencies import get_cache
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.external.google_maps import GoogleMapsService

router = APIRouter(prefix="/geocode", tags=["geocode"])


class GeocodeRequest(BaseModel):
    query: str = Field(min_length=2, max_length=255)


@router.post("")
async def geocode_location(
    payload: GeocodeRequest,
    request: Request,
    cache: CacheService = Depends(get_cache),
) -> dict[str, Any]:
    service = GoogleMapsService(cache)
    result = await service.geocode(payload.query)
    if result.get("not_found"):
        return error_response(
            request,
            status_code=400,
            code="INVALID_LOCATION",
            user_message="Unrecognized location name.",
            suggestion="Check the spelling or enter a nearby city or landmark.",
            details={"query": payload.query},
        )
    return result
