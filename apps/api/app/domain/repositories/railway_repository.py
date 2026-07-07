from abc import ABC, abstractmethod
from typing import List

from app.domain.models.railradar import Train, Journey, RunningStatus, StationBoardEntry, TrainDetails, StationLookupResult, StationSearchResponse, RouteGeometry


class IRailwayRepository(ABC):
    """Interface for Railway operations to enforce Dependency Inversion."""

    @abstractmethod
    async def search_trains(self, source: str, destination: str, date: str) -> List[Journey]:
        pass

    @abstractmethod
    async def train_lookup(self, train_number: str) -> Train:
        pass

    @abstractmethod
    async def train_details(self, train_number: str) -> TrainDetails:
        pass

    @abstractmethod
    async def get_live_status(self, train_number: str, date: str) -> RunningStatus:
        pass

    @abstractmethod
    async def get_route(self, train_number: str) -> RouteGeometry:
        pass

    @abstractmethod
    async def get_station_board(self, station_code: str, hours: int = 4) -> List[StationBoardEntry]:
        pass

    @abstractmethod
    async def get_live_station_board(self, station_code: str, hours: int = 4) -> List[StationBoardEntry]:
        pass

    @abstractmethod
    async def station_lookup(self, station_code: str) -> StationLookupResult:
        pass

    @abstractmethod
    async def search_stations(self, query: str) -> StationSearchResponse:
        pass
