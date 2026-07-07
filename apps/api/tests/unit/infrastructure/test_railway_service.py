import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.infrastructure.railradar.railradar_service import RailRadarService
from app.infrastructure.railradar.cache import RailRadarCache
from app.infrastructure.railradar.exceptions import (
    RailRadarNotFoundError,
    RailRadarRateLimitError,
    RailRadarServerError,
    RailRadarTimeoutError,
    RailRadarValidationError,
)
from app.infrastructure.railradar.client import RailRadarClient


@pytest.fixture
def mock_cache():
    cache = AsyncMock(spec=RailRadarCache)
    cache.get_between_stations.return_value = None
    cache.get_train_lookup.return_value = None
    cache.get_live_status.return_value = None
    cache.get_station_board.return_value = None
    cache.get_live_board.return_value = None
    cache.get_station_lookup.return_value = None
    cache.get_all_trains_lookup.return_value = None
    cache.get_station_search.return_value = None
    return cache


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=RailRadarClient)
    return client


@pytest.fixture
def railradar_service(mock_cache, mock_client):
    service = RailRadarService(api_key="test_key", cache=mock_cache)
    service._client = mock_client
    return service


@pytest.mark.asyncio
async def test_search_trains_cache_hit(railradar_service, mock_cache, mock_client):
    mock_cache.get_between_stations.return_value = [{
        "train_number": "12345",
        "train_name": "Test Express",
        "train_type": "EXP",
        "source": {"code": "NDLS", "name": "New Delhi"},
        "destination": {"code": "BCT", "name": "Mumbai Central"},
        "departure_time": "10:00",
        "arrival_time": "22:00",
        "duration_minutes": 720,
        "distance_km": 1300.0,
        "runs_days": ["Mon"],
        "classes": ["SL"],
        "classes_available": ["SL"],
    }]

    result = await railradar_service.search_trains("NDLS", "BCT", "2026-07-15")

    mock_client.search_trains.assert_not_called()
    assert len(result) == 1
    assert result[0].train_number == "12345"


@pytest.mark.asyncio
async def test_search_trains_cache_miss_api_success(railradar_service, mock_cache, mock_client):
    mock_journey = MagicMock()
    mock_journey.model_dump.return_value = {"mock": "data"}

    mock_search_response = MagicMock()
    mock_search_response.trains = [mock_journey]
    mock_client.search_trains.return_value = mock_search_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_journey") as mock_map:
        mock_map.return_value = "MappedJourney"
        result = await railradar_service.search_trains("NDLS", "BCT", "2026-07-15")

        mock_client.search_trains.assert_called_once_with("NDLS", "BCT", "2026-07-15", False)
        mock_cache.set_between_stations.assert_called_once()
        assert result == ["MappedJourney"]


@pytest.mark.asyncio
async def test_search_trains_retry_on_rate_limit(railradar_service, mock_cache, mock_client):
    mock_search_response = MagicMock()
    mock_search_response.trains = []
    mock_client.search_trains.return_value = mock_search_response

    mock_client.search_trains.side_effect = [
        RailRadarRateLimitError("Rate limit"),
        RailRadarTimeoutError("Timeout"),
        mock_search_response,
    ]

    result = await railradar_service.search_trains("NDLS", "BCT", "2026-07-15")

    assert mock_client.search_trains.call_count == 3
    assert result == []


@pytest.mark.asyncio
async def test_search_trains_raises_after_max_retries(railradar_service, mock_cache, mock_client):
    mock_client.search_trains.side_effect = RailRadarRateLimitError("Rate limit")

    with pytest.raises(RailRadarRateLimitError):
        await railradar_service.search_trains("NDLS", "BCT", "2026-07-15")

    assert mock_client.search_trains.call_count == 3


@pytest.mark.asyncio
async def test_search_trains_validation_error_no_retry(railradar_service, mock_cache, mock_client):
    mock_client.search_trains.side_effect = RailRadarValidationError("Invalid input")

    with pytest.raises(RailRadarValidationError):
        await railradar_service.search_trains("INVALID", "CODE", "not-a-date")

    assert mock_client.search_trains.call_count == 1


@pytest.mark.asyncio
async def test_train_lookup_returns_train(railradar_service, mock_cache, mock_client):
    mock_train = MagicMock()
    mock_train.model_dump.return_value = {
        "number": "12951",
        "name": "Rajdhani Express",
        "type": "RAJDHANI",
        "source": {"code": "NDLS", "name": "New Delhi"},
        "destination": {"code": "MMCT", "name": "Mumbai Central"},
        "classes_available": ["1A", "2A", "3A"],
        "runDays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "distance": 1384,
        "duration": 925,
    }
    mock_details = MagicMock()
    mock_details.train = mock_train
    mock_client.get_train_details.return_value = mock_details

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_train") as mock_map:
        mock_map.return_value = MagicMock(number="12951")
        result = await railradar_service.train_lookup("12951")

        mock_client.get_train_details.assert_called_once()
        mock_cache.set_train_lookup.assert_called_once()


@pytest.mark.asyncio
async def test_train_lookup_uses_cache(railradar_service, mock_cache, mock_client):
    mock_cache.get_train_lookup.return_value = {
        "number": "12951",
        "name": "Rajdhani Express",
        "type": "RAJDHANI",
        "source": {"code": "NDLS", "name": "New Delhi"},
        "destination": {"code": "MMCT", "name": "Mumbai Central"},
        "classes_available": ["1A", "2A", "3A"],
        "runDays": ["Mon"],
        "distance": 1384,
        "duration": 925,
    }

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_train") as mock_map:
        mock_map.return_value = MagicMock(number="12951")
        result = await railradar_service.train_lookup("12951")

        mock_client.get_train_details.assert_not_called()
        assert result.number == "12951"


@pytest.mark.asyncio
async def test_live_status_retry_on_server_error(railradar_service, mock_cache, mock_client):
    mock_status = MagicMock()
    mock_status.model_dump.return_value = {
        "trainNumber": "12951",
        "status": "running",
        "delayMinutes": 0,
        "currentLocation": {"stationCode": "BRC", "status": "departed"},
    }
    mock_response = MagicMock()
    mock_response.model_dump.return_value = mock_status.model_dump()
    mock_client.get_live_status.return_value = mock_response

    mock_client.get_live_status.side_effect = [
        RailRadarServerError("Server error"),
        mock_response,
    ]

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_running_status") as mock_map:
        mock_map.return_value = MagicMock(train_number="12951", status="running")
        result = await railradar_service.get_live_status("12951", "2026-07-15")

        assert mock_client.get_live_status.call_count == 2
        assert result.train_number == "12951"


@pytest.mark.asyncio
async def test_live_status_not_found_raises_404(railradar_service, mock_cache, mock_client):
    mock_client.get_live_status.side_effect = RailRadarNotFoundError("Train not found")

    with pytest.raises(RailRadarNotFoundError):
        await railradar_service.get_live_status("99999", "2026-07-15")

    assert mock_client.get_live_status.call_count == 1


@pytest.mark.asyncio
async def test_live_status_auto_detect_date(railradar_service, mock_cache, mock_client):
    mock_status = MagicMock()
    mock_status.model_dump.return_value = {
        "trainNumber": "12951",
        "status": "running",
        "delayMinutes": 5,
    }
    mock_response = MagicMock()
    mock_response.model_dump.return_value = mock_status.model_dump()
    mock_client.get_live_status.return_value = mock_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_running_status") as mock_map:
        mock_map.return_value = MagicMock(train_number="12951", status="running")
        result = await railradar_service.get_live_status("12951", None)

        mock_client.get_live_status.assert_called_once_with("12951", None)
        assert result.train_number == "12951"


@pytest.mark.asyncio
async def test_station_board_returns_entries(railradar_service, mock_cache, mock_client):
    mock_board_response = MagicMock()
    mock_board_response.trains = []
    mock_board_response.count = 0
    mock_client.get_station_board.return_value = mock_board_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_station_board") as mock_map:
        mock_map.return_value = []
        result = await railradar_service.get_station_board("NDLS")

        mock_client.get_station_board.assert_called_once_with("NDLS", False)
        assert result == []


@pytest.mark.asyncio
async def test_station_board_with_intermediate(railradar_service, mock_cache, mock_client):
    mock_board_response = MagicMock()
    mock_board_response.trains = []
    mock_client.get_station_board.return_value = mock_board_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_station_board") as mock_map:
        mock_map.return_value = []
        result = await railradar_service.get_station_board("NDLS", include_intermediate=True)

        mock_client.get_station_board.assert_called_once_with("NDLS", True)
        assert result == []


@pytest.mark.asyncio
async def test_station_lookup_returns_result(railradar_service, mock_cache, mock_client):
    mock_cache.get_station_lookup.return_value = None
    mock_lookup_response = MagicMock()
    mock_lookup_response.data = {"NDLS": "New Delhi"}
    mock_client.station_lookup.return_value = mock_lookup_response

    result = await railradar_service.station_lookup("NDLS")

    mock_client.station_lookup.assert_called_once_with("NDLS")
    assert result.station_code == "NDLS"
    assert result.station_name == "New Delhi"


@pytest.mark.asyncio
async def test_station_lookup_not_found_raises_404(railradar_service, mock_cache, mock_client):
    mock_cache.get_station_lookup.return_value = None
    mock_lookup_response = MagicMock()
    mock_lookup_response.data = {"BGP": "Begusarai"}
    mock_client.station_lookup.return_value = mock_lookup_response

    with pytest.raises(RailRadarNotFoundError):
        await railradar_service.station_lookup("NDLS")


@pytest.mark.asyncio
async def test_station_lookup_uses_cache(railradar_service, mock_cache, mock_client):
    mock_cache.get_station_lookup.return_value = {"code": "NDLS", "name": "New Delhi"}

    result = await railradar_service.station_lookup("NDLS")

    mock_client.station_lookup.assert_not_called()
    assert result.station_code == "NDLS"


@pytest.mark.asyncio
async def test_get_all_trains_lookup(railradar_service, mock_cache, mock_client):
    mock_cache.get_all_trains_lookup.return_value = None
    mock_lookup_response = MagicMock()
    mock_lookup_response.data = {"12951": "Rajdhani Express", "12345": "Test Express"}
    mock_client.train_lookup.return_value = mock_lookup_response

    result = await railradar_service.get_all_trains_lookup()

    mock_client.train_lookup.assert_called_once()
    assert result == {"12951": "Rajdhani Express", "12345": "Test Express"}


@pytest.mark.asyncio
async def test_get_all_trains_lookup_uses_cache(railradar_service, mock_cache, mock_client):
    mock_cache.get_all_trains_lookup.return_value = {"12951": "Rajdhani Express"}

    result = await railradar_service.get_all_trains_lookup()

    mock_client.train_lookup.assert_not_called()
    assert result == {"12951": "Rajdhani Express"}


@pytest.mark.asyncio
async def test_route_with_format_and_stops(railradar_service, mock_cache, mock_client):
    mock_cache.get_route.return_value = None
    mock_route_response = MagicMock()
    mock_route_response.trainNumber = "12951"
    mock_route_response.format = "geojson"
    mock_route_response.stops = []
    mock_route_response.coordinates = []
    mock_route_response.total_distance_km = 0.0
    mock_client.get_route.return_value = mock_route_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_route") as mock_map:
        mock_map.return_value = MagicMock(train_number="12951", stops=[], coordinates=[])
        result = await railradar_service.get_route("12951", format="geojson", stops=True)

        mock_client.get_route.assert_called_once_with("12951", "geojson", True)
        assert result.train_number == "12951"


@pytest.mark.asyncio
async def test_live_station_board_with_hours(railradar_service, mock_cache, mock_client):
    mock_board_response = MagicMock()
    mock_board_response.trains = []
    mock_client.get_live_station_board.return_value = mock_board_response

    with patch("app.infrastructure.railradar.railradar_service.RailRadarMapper.map_station_board") as mock_map:
        mock_map.return_value = []
        result = await railradar_service.get_live_station_board("NDLS", hours=4, include_intermediate=False)

        mock_client.get_live_station_board.assert_called_once_with("NDLS", 4, False)
        assert result == []
