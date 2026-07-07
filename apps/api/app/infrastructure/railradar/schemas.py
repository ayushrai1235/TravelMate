"""RailRadar API response schemas (external DTOs)."""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Any


class RailRadarMeta(BaseModel):
    traceId: str = ""
    timestamp: Optional[str] = None
    executionTime: Optional[int] = None
    source: Optional[str] = None


class RailRadarError(BaseModel):
    code: str = ""
    message: str = ""


class RailRadarEnvelope(BaseModel):
    """Standard response envelope wrapping all API responses."""
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    meta: RailRadarMeta = Field(default_factory=RailRadarMeta)


class RailRadarStation(BaseModel):
    code: str
    name: str
    zone: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RailRadarStationInfo(BaseModel):
    """Station info used in train details and station board responses."""
    code: str
    name: str


class RailRadarScheduleStop(BaseModel):
    sequence: Optional[int] = None
    station_code: Optional[str] = None
    station: Optional[RailRadarStationInfo] = None
    station_name: Optional[str] = None
    arrival: Optional[str] = None
    departure: Optional[str] = None
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    halt: int = 0
    halt_minutes: int = 0
    distance: float = 0.0
    distance_km: float = 0.0
    day: int = 1
    arrivalDay: Optional[int] = None
    departureDay: Optional[int] = None
    day_count: int = 1
    platform: Optional[str] = None
    isHalt: Optional[bool] = None
    speedToNextStationKmph: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class RailRadarTrain(BaseModel):
    number: str
    name: str
    type: str
    category: Optional[str] = None
    source: RailRadarStationInfo
    destination: RailRadarStationInfo
    runDays: List[str] = Field(default_factory=list)
    runs_days: List[str] = Field(default_factory=list)
    distance: Optional[float] = None
    distance_km: Optional[float] = None
    duration: Optional[int] = None
    duration_minutes: Optional[int] = None
    avgSpeed: Optional[float] = None
    avg_speed: Optional[float] = None
    maxSpeed: Optional[float] = None
    max_speed: Optional[float] = None
    totalHalts: Optional[int] = None
    total_halts: Optional[int] = None
    returnTrain: Optional[str] = None
    coachPosition: Optional[str] = None
    classes_available: List[str] = Field(default_factory=list)
    schedule: List[RailRadarScheduleStop] = Field(default_factory=list)


class RailRadarJourney(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    train: Optional[RailRadarTrain] = None
    source: RailRadarStation
    destination: RailRadarStation
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    runs_days: List[str] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    classes_available: List[str] = Field(default_factory=list)
    train_code: Optional[str] = None
    from_station: Optional[Any] = None
    to_station: Optional[Any] = None
    live: Optional[Any] = None


class RailRadarSearchResponse(BaseModel):
    """Response for trains between stations."""
    model_config = {"populate_by_name": True}
    from_station: Optional[RailRadarStationInfo] = Field(None, alias="from")
    to_station: Optional[RailRadarStationInfo] = Field(None, alias="to")
    count: int = 0
    total: int = 0
    trains: List[RailRadarJourney] = Field(default_factory=list)
    data: List[RailRadarJourney] = Field(default_factory=list)


class RailRadarCurrentLocation(BaseModel):
    stationCode: Optional[str] = None
    current_station_code: Optional[str] = None
    sequence: Optional[int] = None
    status: Optional[str] = None
    isHalt: Optional[bool] = None
    isDiverted: Optional[bool] = None
    isActualPosition: Optional[bool] = None
    segmentProgress: Optional[float] = None
    speedKmh: Optional[float] = None
    bearingDegrees: Optional[float] = None


class RailRadarHaltInfo(BaseModel):
    stationCode: Optional[str] = None
    station_name: Optional[str] = None
    current_station_code: Optional[str] = None
    current_station_name: Optional[str] = None
    sequence: Optional[int] = None
    distance: Optional[float] = None


class RailRadarException(BaseModel):
    type: Optional[str] = None
    message: Optional[str] = None
    diverted: Optional[Any] = None
    partiallyCancelled: Optional[Any] = None
    rescheduled: Optional[Any] = None


class RailRadarStatusResponse(BaseModel):
    trainNumber: Optional[str] = None
    train_number: Optional[str] = None
    trainName: Optional[str] = None
    train_name: Optional[str] = None
    startDate: Optional[str] = None
    lastUpdatedAt: Optional[str] = None
    last_updated: Optional[str] = None
    reported_at: Optional[str] = None
    status: Optional[str] = None
    delayMinutes: Optional[int] = None
    delay_minutes: int = 0
    train: Optional[RailRadarTrain] = None
    currentLocation: Optional[RailRadarCurrentLocation] = None
    current_location: Optional[RailRadarCurrentLocation] = None
    previousHalt: Optional[RailRadarHaltInfo] = None
    nextHalt: Optional[RailRadarHaltInfo] = None
    exceptions: List[RailRadarException] = Field(default_factory=list)
    route: List[RailRadarScheduleStop] = Field(default_factory=list)
    isLive: Optional[bool] = None
    current_station_code: Optional[str] = None
    current_station_name: Optional[str] = None


class RailRadarGeoJSONGeometry(BaseModel):
    type: Optional[str] = None
    coordinates: List[List[float]] = Field(default_factory=list)


class RailRadarGeoJSON(BaseModel):
    type: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    geometry: RailRadarGeoJSONGeometry = Field(default_factory=RailRadarGeoJSONGeometry)


class RailRadarRouteStop(BaseModel):
    sequence: Optional[int] = None
    code: Optional[str] = None
    station_code: Optional[str] = None
    name: Optional[str] = None
    station_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class RailRadarRouteResponse(BaseModel):
    trainNumber: Optional[str] = None
    train_number: Optional[str] = None
    format: Optional[str] = None
    geojson: Optional[RailRadarGeoJSON] = None
    polyline: Optional[str] = None
    coordinates: List[List[float]] = Field(default_factory=list)
    stops: List[RailRadarRouteStop] = Field(default_factory=list)
    route: List[RailRadarScheduleStop] = Field(default_factory=list)
    total_distance_km: float = 0.0


class RailRadarStopInfo(BaseModel):
    sequence: Optional[int] = None
    arrival: Optional[str] = None
    departure: Optional[str] = None
    arrivalDay: Optional[int] = None
    departureDay: Optional[int] = None
    day: Optional[int] = None
    distance: float = 0.0
    stopType: Optional[str] = None


class RailRadarTrainBoardEntry(BaseModel):
    train: Optional[RailRadarTrain] = None
    stop: Optional[RailRadarStopInfo] = None
    live: Optional[Any] = None


class RailRadarStationBoardResponse(BaseModel):
    station: Optional[RailRadarStationInfo] = None
    count: int = 0
    total: int = 0
    includeIntermediate: Optional[bool] = None
    window: Optional[Any] = None
    trains: List[RailRadarTrainBoardEntry] = Field(default_factory=list)
    entries: List[dict[str, Any]] = Field(default_factory=list)


class RailRadarTrainDetailsResponse(BaseModel):
    train: RailRadarTrain
    route: List[RailRadarScheduleStop] = Field(default_factory=list)
    schedule: List[RailRadarScheduleStop] = Field(default_factory=list)


class RailRadarTrainLookupResponse(BaseModel):
    """Response for GET /lookup/trains - flat {number: name} map."""
    data: dict[str, str] = Field(default_factory=dict)


class RailRadarStationLookupResponse(BaseModel):
    """Response for GET /lookup/stations - flat {code: name} map."""
    data: dict[str, str] = Field(default_factory=dict)


class RailRadarStationSearchResponse(BaseModel):
    stations: List[RailRadarStation] = Field(default_factory=list)
    total: int = 0
