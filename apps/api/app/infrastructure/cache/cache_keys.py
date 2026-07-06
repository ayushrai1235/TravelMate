import hashlib
import json
from collections.abc import Mapping
from typing import Any


def stable_hash(value: Mapping[str, Any] | str) -> str:
    if isinstance(value, str):
        payload = value.strip().lower()
    else:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def geocode_key(query: str) -> str:
    return f"cache:api:geocode:{stable_hash(query)}"


def distance_key(origin: Mapping[str, Any], destination: Mapping[str, Any]) -> str:
    return f"cache:api:distance:{stable_hash({'origin': origin, 'destination': destination})}"


def trains_key(origin: str, destination: str, travel_date: str) -> str:
    return f"cache:api:trains:{stable_hash({'origin': origin, 'destination': destination, 'date': travel_date})}"


def weather_key(lat: float, lng: float, travel_date: str) -> str:
    return f"cache:api:weather:{stable_hash({'lat': lat, 'lng': lng, 'date': travel_date})}"


def bus_key(origin: Mapping[str, Any], destination: Mapping[str, Any], travel_date: str) -> str:
    return f"cache:api:bus_gtfs:{stable_hash({'origin': origin, 'destination': destination, 'date': travel_date})}"


def temple_key(temple_id: str) -> str:
    return f"cache:temple:{temple_id}"


def temple_search_key(query: Mapping[str, Any]) -> str:
    return f"cache:temple:search:{stable_hash(query)}"


def itinerary_key(payload: Mapping[str, Any]) -> str:
    return f"cache:app:trip:{stable_hash(payload)}"
