"""RailRadar async HTTP client using httpx."""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx
from httpx import AsyncClient, Timeout, HTTPStatusError, RequestError

from app.infrastructure.railradar.exceptions import (
    RailRadarAuthError,
    RailRadarForbiddenError,
    RailRadarNotFoundError,
    RailRadarRateLimitError,
    RailRadarServerError,
    RailRadarConnectionError,
    RailRadarTimeoutError,
    RailRadarValidationError,
    RailRadarServiceException,
)
from app.infrastructure.railradar.schemas import (
    RailRadarSearchResponse,
    RailRadarStatusResponse,
    RailRadarRouteResponse,
    RailRadarStationBoardResponse,
    RailRadarTrainDetailsResponse,
    RailRadarStationSearchResponse,
    RailRadarTrainLookupResponse,
    RailRadarStationLookupResponse,
)

logger = logging.getLogger(__name__)


class RailRadarClient:
    """Async HTTP client for RailRadar API."""

    BASE_URL = "https://api.railradar.in/v1"

    def __init__(self, api_key: str, timeout: float = 8.0):
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[AsyncClient] = None

    async def _get_client(self) -> AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = AsyncClient(
                base_url=self.BASE_URL,
                timeout=Timeout(self.timeout, connect=5.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _translate_error(self, exc: Exception, response: Optional[httpx.Response] = None) -> RailRadarServiceException:
        if isinstance(exc, httpx.TimeoutException):
            return RailRadarTimeoutError()
        if isinstance(exc, httpx.ConnectError):
            return RailRadarConnectionError()
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status == 400:
                return RailRadarValidationError(exc.response.text)
            if status == 401:
                return RailRadarAuthError(exc.response.text)
            if status == 403:
                return RailRadarForbiddenError(exc.response.text)
            if status == 404:
                return RailRadarNotFoundError(exc.response.text)
            if status == 429:
                return RailRadarRateLimitError(exc.response.text)
            if status == 503:
                return RailRadarServerError("Service unavailable: upstream data source temporarily down")
            if 500 <= status < 600:
                return RailRadarServerError(exc.response.text)
        return RailRadarServiceException(str(exc))

    async def search_trains(self, source: str, destination: str, date: str = None, live: bool = False, by_city: bool = False, train_type: str = None, category: str = None) -> RailRadarSearchResponse:
        try:
            client = await self._get_client()
            params = {}
            if date:
                params["date"] = date
            params["live"] = live
            params["byCity"] = by_city
            if train_type:
                params["type"] = train_type
            if category:
                params["category"] = category
            response = await client.get(
                f"/trains/between/{source.upper()}/{destination.upper()}",
                params=params,
            )
            response.raise_for_status()
            return RailRadarSearchResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def get_train_details(self, train_number: str, halts_only: bool = False) -> RailRadarTrainDetailsResponse:
        try:
            client = await self._get_client()
            params = {"haltsOnly": halts_only}
            response = await client.get(f"/trains/{train_number}", params=params)
            response.raise_for_status()
            return RailRadarTrainDetailsResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def get_live_status(self, train_number: str, date: str = None, halts_only: bool = False, geometry: bool = False, format: str = None, include_coordinates: bool = False) -> RailRadarStatusResponse:
        try:
            client = await self._get_client()
            params = {}
            if date:
                params["date"] = date
            params["haltsOnly"] = halts_only
            params["geometry"] = geometry
            if format:
                params["format"] = format
            params["includeCoordinates"] = include_coordinates
            response = await client.get(
                f"/trains/{train_number}/live",
                params=params,
            )
            response.raise_for_status()
            return RailRadarStatusResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def get_route(self, train_number: str, format: str = "geojson", stops: bool = False) -> RailRadarRouteResponse:
        try:
            client = await self._get_client()
            params = {"format": format, "stops": stops}
            response = await client.get(f"/trains/{train_number}/route", params=params)
            response.raise_for_status()
            return RailRadarRouteResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def get_station_board(self, station_code: str, include_intermediate: bool = False) -> RailRadarStationBoardResponse:
        try:
            client = await self._get_client()
            params = {"includeIntermediate": include_intermediate}
            response = await client.get(
                f"/stations/{station_code.upper()}/trains",
                params=params,
            )
            response.raise_for_status()
            return RailRadarStationBoardResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def get_live_station_board(self, station_code: str, hours: int = 4, include_intermediate: bool = False) -> RailRadarStationBoardResponse:
        try:
            client = await self._get_client()
            params = {"hours": hours, "includeIntermediate": include_intermediate}
            response = await client.get(
                f"/stations/{station_code.upper()}/live",
                params=params,
            )
            response.raise_for_status()
            return RailRadarStationBoardResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def search_stations(self, query: str) -> RailRadarStationSearchResponse:
        try:
            client = await self._get_client()
            response = await client.get(
                "/lookup/stations",
                params={"query": query},
            )
            response.raise_for_status()
            return RailRadarStationSearchResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def train_lookup(self) -> RailRadarTrainLookupResponse:
        try:
            client = await self._get_client()
            response = await client.get("/lookup/trains")
            response.raise_for_status()
            return RailRadarTrainLookupResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)

    async def station_lookup(self, station_code: str) -> RailRadarStationLookupResponse:
        try:
            client = await self._get_client()
            response = await client.get("/lookup/stations")
            response.raise_for_status()
            return RailRadarStationLookupResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise await self._translate_error(e, e.response)
        except (RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            raise await self._translate_error(e)
