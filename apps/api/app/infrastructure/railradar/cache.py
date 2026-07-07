"""RailRadar cache layer using Redis."""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# TTLs per endpoint (seconds)
_TTL_TRAIN_DETAILS = 6 * 60 * 60   # 6 hours
_TTL_TRAIN_LOOKUP = 24 * 60 * 60   # 24 hours
_TTL_STATION_LOOKUP = 24 * 60 * 60 # 24 hours
_TTL_BETWEEN_STATIONS = 15 * 60    # 15 minutes
_TTL_LIVE_STATUS = 60              # 60 seconds
_TTL_STATION_BOARD = 120           # 120 seconds
_TTL_ROUTE_GEOMETRY = 24 * 60 * 60 # 24 hours


def _key(*parts: str) -> str:
    return f"railradar:{':'.join(parts)}"


class RailRadarCache:
    """Cache-aside pattern for RailRadar API responses."""

    def __init__(self, redis: Optional[Redis] = None):
        self._redis = redis

    # -- Train Details --
    async def get_train_details(self, train_number: str) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("details", train_number))
        return json.loads(raw) if raw else None

    async def set_train_details(self, train_number: str, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("details", train_number), _TTL_TRAIN_DETAILS, json.dumps(data, default=str))

    # -- Train Lookup --
    async def get_train_lookup(self, train_number: str) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("lookup", train_number))
        return json.loads(raw) if raw else None

    async def set_train_lookup(self, train_number: str, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("lookup", train_number), _TTL_TRAIN_LOOKUP, json.dumps(data, default=str))

    # -- Station Lookup --
    async def get_station_lookup(self, station_code: str) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("station", station_code))
        return json.loads(raw) if raw else None

    async def set_station_lookup(self, station_code: str, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("station", station_code), _TTL_STATION_LOOKUP, json.dumps(data, default=str))

    # -- Between Stations --
    async def get_between_stations(self, source: str, destination: str, date: str) -> Optional[list]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("between", source.upper(), destination.upper(), date))
        return json.loads(raw) if raw else None

    async def set_between_stations(self, source: str, destination: str, date: str, data: list):
        if not self._redis:
            return
        await self._redis.setex(
            _key("between", source.upper(), destination.upper(), date),
            _TTL_BETWEEN_STATIONS,
            json.dumps(data, default=str),
        )

    # -- Live Status --
    async def get_live_status(self, train_number: str, date: str) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("status", train_number, date))
        return json.loads(raw) if raw else None

    async def set_live_status(self, train_number: str, date: str, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("status", train_number, date), _TTL_LIVE_STATUS, json.dumps(data, default=str))

    # -- Route Geometry --
    async def get_route(self, train_number: str) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("route", train_number))
        return json.loads(raw) if raw else None

    async def set_route(self, train_number: str, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("route", train_number), _TTL_ROUTE_GEOMETRY, json.dumps(data, default=str))

    # -- Station Board --
    async def get_station_board(self, station_code: str, include_intermediate: bool = False) -> Optional[list]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("board", station_code.upper(), str(int(include_intermediate))))
        return json.loads(raw) if raw else None

    async def set_station_board(self, station_code: str, include_intermediate: bool = False, data: list = None):
        if not self._redis:
            return
        if data is None:
            data = []
        await self._redis.setex(
            _key("board", station_code.upper(), str(int(include_intermediate))),
            _TTL_STATION_BOARD,
            json.dumps(data, default=str),
        )

    # -- Live Station Board --
    async def get_live_board(self, station_code: str, hours: int) -> Optional[list]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("live-board", station_code.upper(), str(hours)))
        return json.loads(raw) if raw else None

    async def set_live_board(self, station_code: str, hours: int, data: list):
        if not self._redis:
            return
        await self._redis.setex(
            _key("live-board", station_code.upper(), str(hours)),
            _TTL_STATION_BOARD,
            json.dumps(data, default=str),
        )

    # -- Station Search --
    async def get_station_search(self, query: str) -> Optional[list]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("search", query.lower()))
        return json.loads(raw) if raw else None

    async def set_station_search(self, query: str, data: list):
        if not self._redis:
            return
        await self._redis.setex(_key("search", query.lower()), _TTL_STATION_LOOKUP, json.dumps(data, default=str))

    # -- All Trains Lookup --
    async def get_all_trains_lookup(self) -> Optional[dict]:
        if not self._redis:
            return None
        raw = await self._redis.get(_key("trains_lookup", "all"))
        return json.loads(raw) if raw else None

    async def set_all_trains_lookup(self, data: dict):
        if not self._redis:
            return
        await self._redis.setex(_key("trains_lookup", "all"), _TTL_TRAIN_LOOKUP, json.dumps(data, default=str))
