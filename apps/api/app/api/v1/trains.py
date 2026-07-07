from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.domain.models.railradar import Train, Journey, RunningStatus, StationBoardEntry, StationLookupResult, StationSearchResponse, RouteGeometry
from app.infrastructure.railradar.railradar_service import RailRadarService
from app.infrastructure.railradar.cache import RailRadarCache
from app.infrastructure.railradar.exceptions import (
    RailRadarRateLimitError,
    RailRadarNotFoundError,
    RailRadarValidationError,
    RailRadarAuthError,
)
from app.core.config import settings
from redis.asyncio import Redis

router = APIRouter()


async def get_railradar_service() -> RailRadarService:
    redis_client = None
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        redis_client = None
    cache = RailRadarCache(redis_client)
    return RailRadarService(api_key=settings.RAILRADAR_API_KEY or "mock", cache=cache)


@router.get("/search", response_model=List[Journey])
async def search_trains(
    source: str = Query(..., description="Source Station Code (e.g., NDLS)"),
    destination: str = Query(..., description="Destination Station Code (e.g., MMCT)"),
    date: Optional[str] = Query(None, description="Journey Date YYYY-MM-DD"),
    live: bool = Query(False, description="Enrich with live status"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Search trains between two stations using RailRadar."""
    try:
        return await service.search_trains(source, destination, date, live)
    except RailRadarRateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except RailRadarValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="No trains found for the given route/date.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/between/{source}/{destination}", response_model=List[Journey])
async def search_trains_between(
    source: str,
    destination: str,
    date: Optional[str] = Query(None, description="Journey Date YYYY-MM-DD"),
    live: bool = Query(False, description="Enrich with live status"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Search trains between two stations (between stations endpoint)."""
    try:
        return await service.search_trains(source, destination, date, live)
    except RailRadarRateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except RailRadarValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="No trains found for the given route/date.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_number}/info", response_model=Train)
async def get_train_info(
    train_number: str,
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get static train information using RailRadar."""
    try:
        return await service.train_lookup(train_number)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="Train not found.")
    except RailRadarAuthError:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_number}/details", response_model=Train)
async def get_train_details(
    train_number: str,
    halts_only: bool = Query(False, description="Return only halting stops"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get detailed train information including full schedule."""
    try:
        return await service.train_details(train_number)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="Train not found.")
    except RailRadarAuthError:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_number}/status", response_model=RunningStatus)
async def get_live_status(
    train_number: str,
    date: Optional[str] = Query(None, description="Journey Date YYYY-MM-DD (omit to auto-detect)"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get live running status for a train using RailRadar."""
    try:
        return await service.get_live_status(train_number, date)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="Train not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_number}/route", response_model=RouteGeometry)
async def get_train_route(
    train_number: str,
    format: str = Query("geojson", description="Response format: geojson, polyline, or coordinates"),
    stops: bool = Query(False, description="Include station stops alongside geometry"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get the full route with all stops for a train using RailRadar."""
    try:
        return await service.get_route(train_number, format, stops)
    except RailRadarNotFoundError:
        raise HTTPException(status_code=404, detail="Train not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stations/search", response_model=StationSearchResponse)
async def search_stations(
    query: str = Query(..., description="Station name or code to search"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Search stations by name or code using RailRadar."""
    try:
        return await service.search_stations(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stations/lookup", response_model=StationSearchResponse)
async def station_lookup_all(
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get all stations (flat code->name map) using RailRadar."""
    try:
        data = await service.station_lookup("")
        return StationSearchResponse(stations=[data], total=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trains/lookup", response_model=dict[str, str])
async def trains_lookup_all(
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get all active trains (flat number->name map) using RailRadar."""
    try:
        return await service.get_all_trains_lookup()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stations/{code}/board", response_model=List[StationBoardEntry])
async def get_station_board(
    code: str,
    include_intermediate: bool = Query(False, description="Include pass-through (non-halting) trains"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get scheduled station board for a station using RailRadar."""
    try:
        return await service.get_station_board(code, include_intermediate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stations/{code}/live-board", response_model=List[StationBoardEntry])
async def get_live_station_board(
    code: str,
    hours: int = Query(4, description="Hours ahead to look for trains (allowed: 2, 4, 6, 8)"),
    include_intermediate: bool = Query(False, description="Include pass-through (non-halting) trains"),
    service: RailRadarService = Depends(get_railradar_service),
):
    """Get live station board for a station using RailRadar."""
    try:
        return await service.get_live_station_board(code, hours, include_intermediate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
