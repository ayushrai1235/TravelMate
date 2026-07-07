from __future__ import annotations

from typing import Any, Optional
from typing_extensions import TypedDict

from app.domain.models.train import Journey


class LocationInput(TypedDict, total=False):
    text: str
    coordinates: dict[str, float]
    resolved_name: str


class GeocodedLocation(TypedDict, total=False):
    lat: float
    lng: float
    name: str
    resolved_name: str
    formatted_address: str


class GroupConfig(TypedDict, total=False):
    adults: int
    children: int
    seniors: int


class UserPreferences(TypedDict, total=False):
    budget_tier: str
    accessibility: bool
    preferred_class: str


class AgentError(TypedDict, total=False):
    agent: str
    message: str
    recoverable: bool


class ConfidenceScore(TypedDict, total=False):
    level: str
    score: float


class TripPlanningState(TypedDict, total=False):
    origin: LocationInput
    destination: LocationInput
    travel_date: str
    departure_preference: str
    return_time_preference: str
    trip_end_time_preference: str
    group: GroupConfig
    preferences: UserPreferences

    geocoded_origin: GeocodedLocation
    geocoded_destination: GeocodedLocation
    distance_km: float

    transport_mode_plan: list[str]

    train_data: Optional[dict[str, Any]]
    bus_data: Optional[dict[str, Any]]
    weather_data: Optional[dict[str, Any]]
    temple_data: Optional[dict[str, Any]]
    hotel_data: Optional[list[dict[str, Any]]]
    budget_data: Optional[dict[str, Any]]

    itinerary: Optional[dict[str, Any]]

    errors: list[AgentError]
    retry_count: int
    confidence_summary: dict[str, Any]
