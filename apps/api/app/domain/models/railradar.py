from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime, date


class Station(BaseModel):
    code: str = Field(..., description="Station code (e.g., NDLS)")
    name: str = Field(..., description="Station name (e.g., New Delhi)")
    zone: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        frozen = True


class Platform(BaseModel):
    number: Optional[str] = None
    is_confirmed: bool = False

    class Config:
        frozen = True


class Coach(BaseModel):
    type: str = Field(..., description="Coach class (e.g., 3A, SL)")
    number: Optional[str] = None
    position: Optional[int] = None

    class Config:
        frozen = True


class ScheduleStop(BaseModel):
    sequence: Optional[int] = None
    station_code: str = ""
    station_name: str = ""
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    arrival: Optional[str] = None
    departure: Optional[str] = None
    halt_minutes: int = 0
    halt: int = 0
    distance_km: float = 0.0
    distance: float = 0.0
    day_count: int = 1
    day: int = 1
    arrival_day: Optional[int] = None
    departure_day: Optional[int] = None
    platform: Optional[str] = None
    is_halt: Optional[bool] = None
    speed_to_next_station_kmph: Optional[float] = None

    class Config:
        frozen = True


class StationSchedule(BaseModel):
    station_code: str
    station_name: str
    arrival: Optional[str] = None
    departure: Optional[str] = None
    halt: int = 0
    distance: float = 0.0
    day: int = 1
    platform: Optional[str] = None
    sequence: Optional[int] = None
    arrival_day: Optional[int] = None
    departure_day: Optional[int] = None

    class Config:
        frozen = True


class Train(BaseModel):
    number: str = Field(..., description="5-digit train number")
    name: str
    train_type: str = Field(..., description="EXPRESS, RAJDHANI, SHATABDI, etc.")
    category: Optional[str] = None
    run_days: List[str] = Field(default_factory=list)
    runs_days: List[str] = Field(default_factory=list)
    source_station: Station
    destination_station: Station
    classes_available: List[str] = Field(default_factory=list)
    schedule: List[StationSchedule] = Field(default_factory=list)
    distance_km: Optional[float] = None
    distance: Optional[float] = None
    duration_minutes: Optional[int] = None
    duration: Optional[int] = None
    avg_speed: Optional[float] = None
    max_speed: Optional[float] = None
    total_halts: Optional[int] = None
    return_train: Optional[str] = None
    coach_position: Optional[str] = None

    class Config:
        frozen = True


class Journey(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    source: Station
    destination: Station
    departure_time: str
    arrival_time: str
    duration_minutes: int
    distance_km: float
    runs_days: List[str] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    classes_available: List[str] = Field(default_factory=list)
    train_code: Optional[str] = None
    train: Optional[Train] = None
    from_station: Optional[Station] = None
    to_station: Optional[Station] = None
    live: Optional[Any] = None

    class Config:
        frozen = True


class CurrentLocation(BaseModel):
    station_code: Optional[str] = None
    sequence: Optional[int] = None
    status: Optional[str] = None
    is_halt: Optional[bool] = None
    is_diverted: Optional[bool] = None
    is_actual_position: Optional[bool] = None
    segment_progress: Optional[float] = None
    speed_kmh: Optional[float] = None
    bearing_degrees: Optional[float] = None


class HaltInfo(BaseModel):
    station_code: Optional[str] = None
    station_name: Optional[str] = None
    sequence: Optional[int] = None
    distance: Optional[float] = None


class ExceptionInfo(BaseModel):
    type: Optional[str] = None
    message: Optional[str] = None
    diverted: Optional[Any] = None
    partially_cancelled: Optional[Any] = None
    rescheduled: Optional[Any] = None


class RunningStatus(BaseModel):
    train_number: str
    train_name: Optional[str] = None
    current_station_code: Optional[str] = None
    current_station_name: Optional[str] = None
    status: str = Field(..., description="running, not-started, completed, cancelled, ON_TIME, DELAYED, ARRIVED, etc.")
    delay_minutes: int = 0
    last_updated: Optional[str] = None
    reported_at: Optional[str] = None
    start_date: Optional[str] = None
    train: Optional[Train] = None
    current_location: Optional[CurrentLocation] = None
    previous_halt: Optional[HaltInfo] = None
    next_halt: Optional[HaltInfo] = None
    exceptions: List[ExceptionInfo] = Field(default_factory=list)
    route: List[StationSchedule] = Field(default_factory=list)
    is_live: Optional[bool] = None
    origin: Optional[Station] = None
    destination: Optional[Station] = None

    class Config:
        frozen = True


class StationBoardEntry(BaseModel):
    train_number: str
    train_name: str
    source: str
    destination: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    platform: Optional[str] = None
    status: str = "ON_TIME"
    delay_minutes: int = 0
    current_status: Optional[str] = None
    sequence: Optional[int] = None
    stop_type: Optional[str] = None
    live_type: Optional[str] = None
    live_status: Optional[Any] = None

    class Config:
        frozen = True


class RouteStop(BaseModel):
    station_code: str
    station_name: str
    arrival: Optional[str] = None
    departure: Optional[str] = None
    halt_minutes: int = 0
    distance_km: float = 0.0
    day: int = 1
    platform: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sequence: Optional[int] = None
    is_halt: Optional[bool] = None
    speed_to_next_station_kmph: Optional[float] = None

    class Config:
        frozen = True


class RouteGeometry(BaseModel):
    train_number: str
    stops: List[RouteStop] = Field(default_factory=list)
    coordinates: List[List[float]] = Field(default_factory=list)
    total_distance_km: float = 0.0
    format: Optional[str] = None
    geojson: Optional[Any] = None
    polyline: Optional[str] = None


class TrainDetails(BaseModel):
    number: str
    name: str
    train_type: str
    source: Station
    destination: Station
    classes_available: List[str] = Field(default_factory=list)
    schedule: List[StationSchedule] = Field(default_factory=list)
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    runs_days: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    avg_speed: Optional[float] = None
    max_speed: Optional[float] = None
    total_halts: Optional[int] = None
    return_train: Optional[str] = None
    coach_position: Optional[str] = None

    class Config:
        frozen = True


class StationLookupResult(BaseModel):
    station_code: str
    station_name: str
    zone: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        frozen = True


class StationSearchResponse(BaseModel):
    stations: List[StationLookupResult] = Field(default_factory=list)
    total: int = 0

    class Config:
        frozen = True
