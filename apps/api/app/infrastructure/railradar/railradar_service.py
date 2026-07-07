"""RailRadarService - production service layer with caching, retry, and observability."""
from __future__ import annotations

import logging
import time
import uuid
from typing import List, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

from app.infrastructure.railradar.client import RailRadarClient
from app.infrastructure.railradar.cache import RailRadarCache
from app.infrastructure.railradar.mapper import RailRadarMapper
from app.infrastructure.railradar.exceptions import (
    RailRadarRateLimitError,
    RailRadarServerError,
    RailRadarTimeoutError,
    RailRadarConnectionError,
    RailRadarNotFoundError,
    RailRadarValidationError,
)
from app.domain.models.railradar import (
    Train,
    Journey,
    RunningStatus,
    RouteGeometry,
    StationBoardEntry,
    TrainDetails,
    StationLookupResult,
    StationSearchResponse,
)

logger = logging.getLogger(__name__)

# Retry only on these exceptions
_RETRYABLE = (RailRadarRateLimitError, RailRadarServerError, RailRadarTimeoutError)


def _before_retry(retry_state):
    if retry_state.attempt_number > 1:
        logger.warning(
            "Retrying RailRadar API (attempt %d) due to %s",
            retry_state.attempt_number,
            retry_state.outcome.exception(),
        )


class RailRadarService:
    """Service layer for RailRadar API with cache-aside, retry, and logging."""

    def __init__(self, api_key: str, cache: RailRadarCache):
        self._client = RailRadarClient(api_key=api_key)
        self._cache = cache

    async def close(self):
        await self._client.close()

    # ===================== Train Lookup =====================
    async def train_lookup(self, train_number: str) -> Train:
        """Get static schedule and info for a specific train."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_train_lookup(train_number)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=train_lookup cache_hit=true duration=%.0fms", request_id, (time.time() - start) * 1000)
            return RailRadarMapper.map_train(cached)

        response = await self._client.get_train_details(train_number)
        mapped = RailRadarMapper.map_train(response.train)
        await self._cache.set_train_lookup(train_number, response.train.model_dump(mode="json"))

        logger.info(
            "[RailRadarService] req=%s endpoint=train_lookup cache_hit=false duration=%.0fms status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
        )
        return mapped

    # ===================== Train Details =====================
    async def train_details(self, train_number: str) -> TrainDetails:
        """Get detailed train information including full schedule."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_train_details(train_number)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=train_details cache_hit=true", request_id)
            return RailRadarMapper.map_train_details(cached)

        response = await self._client.get_train_details(train_number)
        mapped = RailRadarMapper.map_train_details(response)
        await self._cache.set_train_details(train_number, response.model_dump(mode="json"))

        logger.info(
            "[RailRadarService] req=%s endpoint=train_details cache_hit=false duration=%.0fms status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
        )
        return mapped

    # ===================== Trains Between Stations =====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE),
        before_sleep=_before_retry,
        reraise=True,
    )
    async def search_trains(self, source: str, destination: str, date: str = None, live: bool = False) -> List[Journey]:
        """Search trains between two stations on a given date."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_between_stations(source, destination, date or "")
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=search_trains cache_hit=true", request_id)
            return [RailRadarMapper.map_journey(j) for j in cached]

        response = await self._client.search_trains(source, destination, date, live)
        journeys = [RailRadarMapper.map_journey(j) for j in response.trains]
        await self._cache.set_between_stations(source, destination, date or "", [j.model_dump(mode="json") for j in response.trains])

        logger.info(
            "[RailRadarService] req=%s endpoint=search_trains cache_hit=false duration=%.0fms results=%d status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
            len(journeys),
        )
        return journeys

    # ===================== Live Train Status =====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE),
        before_sleep=_before_retry,
        reraise=True,
    )
    async def get_live_status(self, train_number: str, date: str = None) -> RunningStatus:
        """Get real-time running status of a train."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_live_status(train_number, date or "")
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=live_status cache_hit=true", request_id)
            return RailRadarMapper.map_running_status(cached)

        response = await self._client.get_live_status(train_number, date)
        mapped = RailRadarMapper.map_running_status(response)
        await self._cache.set_live_status(train_number, date or "", response.model_dump(mode="json"))

        logger.info(
            "[RailRadarService] req=%s endpoint=live_status cache_hit=false duration=%.0fms status=%s",
            request_id,
            (time.time() - start) * 1000,
            mapped.status,
        )
        return mapped

    # ===================== Train Route Geometry =====================
    async def get_route(self, train_number: str, format: str = "geojson", stops: bool = False) -> RouteGeometry:
        """Get the full route with all stops for a train."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_route(train_number)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=route cache_hit=true", request_id)
            return RailRadarMapper.map_route(cached)

        response = await self._client.get_route(train_number, format, stops)
        mapped = RailRadarMapper.map_route(response)
        await self._cache.set_route(train_number, response.model_dump(mode="json"))

        logger.info(
            "[RailRadarService] req=%s endpoint=route cache_hit=false duration=%.0fms stops=%d status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
            len(mapped.stops),
        )
        return mapped

    # ===================== Station Board =====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE),
        before_sleep=_before_retry,
        reraise=True,
    )
    async def get_station_board(self, station_code: str, include_intermediate: bool = False) -> List[StationBoardEntry]:
        """Get scheduled departures/arrivals for a station."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_station_board(station_code, include_intermediate)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=station_board cache_hit=true", request_id)
            return cached

        response = await self._client.get_station_board(station_code, include_intermediate)
        mapped = RailRadarMapper.map_station_board(response)
        await self._cache.set_station_board(station_code, include_intermediate, [e.model_dump(mode="json") for e in mapped])

        logger.info(
            "[RailRadarService] req=%s endpoint=station_board cache_hit=false duration=%.0fms entries=%d status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
            len(mapped),
        )
        return mapped

    # ===================== Live Station Board =====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(_RETRYABLE),
        before_sleep=_before_retry,
        reraise=True,
    )
    async def get_live_station_board(self, station_code: str, hours: int = 4, include_intermediate: bool = False) -> List[StationBoardEntry]:
        """Get live departures/arrivals for a station."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_live_board(station_code, hours)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=live_board cache_hit=true", request_id)
            return cached

        response = await self._client.get_live_station_board(station_code, hours, include_intermediate)
        mapped = RailRadarMapper.map_station_board(response)
        await self._cache.set_live_board(station_code, hours, [e.model_dump(mode="json") for e in mapped])

        logger.info(
            "[RailRadarService] req=%s endpoint=live_board cache_hit=false duration=%.0fms entries=%d status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
            len(mapped),
        )
        return mapped

    # ===================== Station Lookup =====================
    async def station_lookup(self, station_code: str) -> StationLookupResult:
        """Get station details by code."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_station_lookup(station_code)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=station_lookup cache_hit=true", request_id)
            return RailRadarMapper.map_station_lookup(cached)

        response = await self._client.station_lookup(station_code)
        data = response.data
        if station_code in data:
            mapped = StationLookupResult(
                station_code=station_code,
                station_name=data[station_code],
            )
            await self._cache.set_station_lookup(station_code, {"code": station_code, "name": data[station_code]})
            logger.info("[RailRadarService] req=%s endpoint=station_lookup cache_hit=false status=SUCCESS", request_id)
            return mapped

        raise RailRadarNotFoundError(f"Station '{station_code}' not found")

    # ===================== Station Search =====================
    async def search_stations(self, query: str) -> StationSearchResponse:
        """Search stations by name or code."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_station_search(query)
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=station_search cache_hit=true", request_id)
            return StationSearchResponse(stations=[RailRadarMapper.map_station_lookup(s) for s in cached], total=len(cached))

        response = await self._client.search_stations(query)
        mapped = RailRadarMapper.map_station_search(response)
        await self._cache.set_station_search(query, [s.model_dump(mode="json") for s in response.stations])

        logger.info(
            "[RailRadarService] req=%s endpoint=station_search cache_hit=false duration=%.0fms results=%d status=SUCCESS",
            request_id,
            (time.time() - start) * 1000,
            mapped.total,
        )
        return mapped

    # ===================== Train Lookup (All) =====================
    async def get_all_trains_lookup(self) -> dict[str, str]:
        """Get all active train number -> name mapping."""
        start = time.time()
        request_id = str(uuid.uuid4())

        cached = await self._cache.get_all_trains_lookup()
        if cached:
            logger.info("[RailRadarService] req=%s endpoint=all_trains_lookup cache_hit=true", request_id)
            return cached

        response = await self._client.train_lookup()
        data = response.data
        await self._cache.set_all_trains_lookup(data)

        logger.info(
            "[RailRadarService] req=%s endpoint=all_trains_lookup cache_hit=false count=%d status=SUCCESS",
            request_id,
            len(data),
        )
        return data
