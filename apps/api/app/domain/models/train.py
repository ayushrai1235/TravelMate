from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class Station(BaseModel):
    code: str = Field(..., description="Station code (e.g., NDLS)")
    name: str = Field(..., description="Station name (e.g., New Delhi)")
    lat: Optional[float] = None
    lng: Optional[float] = None

class Platform(BaseModel):
    number: str
    is_confirmed: bool = False

class Coach(BaseModel):
    type: str = Field(..., description="Coach class (e.g., 3A, SL)")
    number: Optional[str] = None
    position: Optional[int] = None

class Schedule(BaseModel):
    station: Station
    arrival_time: str
    departure_time: str
    day_count: int
    distance_km: float
    platform: Optional[Platform] = None
    halt_minutes: int = 0

class Availability(BaseModel):
    train_number: str
    date: date
    quota: str
    coach_class: str
    status: str = Field(..., description="Current status (e.g., AVAILABLE, WL, RAC)")
    seats: int
    confirmation_probability: Optional[float] = None

class Fare(BaseModel):
    train_number: str
    source: str
    destination: str
    coach_class: str
    quota: str
    base_fare: float
    total_fare: float
    currency: str = "INR"

class Train(BaseModel):
    number: str = Field(..., description="5-digit train number")
    name: str
    type: str
    runs_on_days: List[str]
    source: Station
    destination: Station
    classes_available: List[str]

class Journey(BaseModel):
    train: Train
    date: date
    source: Station
    destination: Station
    departure_time: str
    arrival_time: str
    duration_minutes: int
    distance_km: float
    classes: List[str]

class RunningStatus(BaseModel):
    train_number: str
    date: date
    current_station: Station
    status: str = Field(..., description="e.g., ON_TIME, DELAYED")
    delay_minutes: int
    updated_at: datetime
    last_reported_location: Optional[str] = None

class PassengerStatus(BaseModel):
    number: int
    booking_status: str
    current_status: str
    coach: Optional[str] = None
    berth: Optional[int] = None

class PNR(BaseModel):
    pnr_number: str
    train_number: str
    train_name: str
    date_of_journey: date
    source: Station
    destination: Station
    boarding_point: Station
    reservation_upto: Station
    passengers: List[PassengerStatus]
    chart_status: str
    coach_class: str
    quota: str
