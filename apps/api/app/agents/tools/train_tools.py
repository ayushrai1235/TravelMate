from langchain.tools import tool
from pydantic import BaseModel, Field
from app.infrastructure.railradar.railradar_service import RailRadarService
from app.infrastructure.railradar.cache import RailRadarCache
from redis.asyncio import Redis
from app.core.config import settings
from app.domain.models.railradar import Train, Journey, RunningStatus
import logging

logger = logging.getLogger(__name__)

# Initialize RailRadar dependencies
redis_client = None
try:
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None
railradar_cache = RailRadarCache(redis_client)
railradar_service = RailRadarService(api_key=settings.RAILRADAR_API_KEY or "mock", cache=railradar_cache)


class SearchTrainsInput(BaseModel):
    source: str = Field(..., description="Source station code (e.g., NDLS)")
    destination: str = Field(..., description="Destination station code (e.g., MMCT)")
    date: str = Field(..., description="Journey date in YYYY-MM-DD format")


class TrainInfoInput(BaseModel):
    train_number: str = Field(..., description="5-digit train number")


class LiveStatusInput(BaseModel):
    train_number: str = Field(..., description="5-digit train number")
    date: str = Field(..., description="Journey date in YYYY-MM-DD format")


class StationSearchInput(BaseModel):
    query: str = Field(..., description="Station name or code to search (e.g., 'New Delhi' or 'NDLS')")


class StationLookupInput(BaseModel):
    station_code: str = Field(..., description="Station code (e.g., NDLS)")


class RouteInput(BaseModel):
    train_number: str = Field(..., description="5-digit train number")


@tool("search_trains", args_schema=SearchTrainsInput)
async def search_trains(source: str, destination: str, date: str) -> dict:
    """Find trains between two stations on a given date using RailRadar."""
    try:
        journeys = await railradar_service.search_trains(source, destination, date)
        if not journeys:
            return {"no_trains_found": True, "trains": []}
        return {
            "no_trains_found": False,
            "trains": [j.model_dump(mode="json") for j in journeys],
        }
    except Exception as e:
        logger.error("Error searching trains: %s", str(e))
        return {"error": str(e), "no_trains_found": True}


@tool("get_train_info", args_schema=TrainInfoInput)
async def get_train_info(train_number: str) -> dict:
    """Get static schedule and info for a specific train using RailRadar."""
    try:
        train = await railradar_service.train_lookup(train_number)
        return train.model_dump(mode="json")
    except Exception as e:
        logger.error("Error getting train info: %s", str(e))
        return {"error": str(e)}


@tool("get_train_running_status", args_schema=LiveStatusInput)
async def get_train_running_status(train_number: str, date: str) -> dict:
    """Get real-time running status of a specific train using RailRadar."""
    try:
        status = await railradar_service.get_live_status(train_number, date)
        return status.model_dump(mode="json")
    except Exception as e:
        logger.error("Error getting running status: %s", str(e))
        return {"error": str(e), "running_status": None}


@tool("get_train_route", args_schema=RouteInput)
async def get_train_route(train_number: str) -> dict:
    """Get the full route with all stops for a train using RailRadar."""
    try:
        route = await railradar_service.get_route(train_number)
        return route.model_dump(mode="json")
    except Exception as e:
        logger.error("Error getting train route: %s", str(e))
        return {"error": str(e)}


@tool("search_stations", args_schema=StationSearchInput)
async def search_stations(query: str) -> dict:
    """Search for Indian railway stations by name or code using RailRadar."""
    try:
        result = await railradar_service.search_stations(query)
        return result.model_dump(mode="json")
    except Exception as e:
        logger.error("Error searching stations: %s", str(e))
        return {"error": str(e), "stations": []}


@tool("get_station_info", args_schema=StationLookupInput)
async def get_station_info(station_code: str) -> dict:
    """Get station details by code using RailRadar."""
    try:
        result = await railradar_service.station_lookup(station_code)
        return result.model_dump(mode="json")
    except Exception as e:
        logger.error("Error getting station info: %s", str(e))
        return {"error": str(e)}
