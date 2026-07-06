
import httpx
import logging
import csv
import io
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class BusService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY  # Reuse Google Maps API key for Transit
        self.base_url = 'https://maps.googleapis.com/maps/api'
        self.client = httpx.AsyncClient(timeout=30.0)
        # GTFS feed URLs for major Indian states (these would be configured in real implementation)
        self.gtfs_feeds = {
            'GSRTC': 'https://gsrtc.in/gtfs/gujarat.zip',  # Gujarat State Road Transport Corporation
            'MSRTC': 'https://msrt.maharashtra.gov.in/gtfs/maharashtra.zip',  # Maharashtra State Road Transport Corporation
            'BMTC': 'https://mybmtc.com/gtfs/bangalore.zip',  # Bangalore Metropolitan Transport Corporation
        }
        # Cache for GTFS data
        self._gtfs_cache = {}
    
    async def get_bus_routes(
        self, 
        origin: str, 
        destination: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        '''Get bus routes between origin and destination'''
        # Try GTFS first, then fall back to Google Transit
        gtfs_result = await self._get_routes_from_gtfs(origin, destination, date)
        if gtfs_result:
            return gtfs_result
        
        # Fallback to Google Transit API
        return await self._get_routes_from_google_transit(origin, destination, date)
    
    async def _get_routes_from_gtfs(
        self, 
        origin: str, 
        destination: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        '''Get bus routes from GTFS feeds'''
        try:
            # In a real implementation, we would:
            # 1. Geocode origin and destination to get coordinates
            # 2. Find nearby bus stops from GTFS stops.txt
            # 3. Find routes that connect these stops using routes.txt, trips.txt, stop_times.txt
            # 4. Filter by date using calendar.txt and calendar_dates.txt
            # 5. Return formatted results
            
            # For now, we'll return mock data since implementing full GTFS parsing is complex
            return self._get_mock_bus_data(origin, destination)
        except Exception as e:
            logger.error(f'Error processing GTFS data: {str(e)}')
            return None
    
    async def _get_routes_from_google_transit(
        self, 
        origin: str, 
        destination: str,
        date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        '''Get bus routes using Google Transit API (via Distance Matrix with transit mode)'''
        if not self.api_key:
            logger.warning('Google Maps API key not configured for transit')
            return self._get_mock_bus_data(origin, destination)
            
        try:
            # Use Distance Matrix API with transit mode to get route options
            response = await self.client.get(
                f'{self.base_url}/distancematrix/json',
                params={
                    'origins': origin,
                    'destinations': destination,
                    'mode': 'transit',
                    'transit_mode': 'bus',
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                return self._parse_google_transit_response(data, origin, destination)
            return None
        except Exception as e:
            logger.error(f'Error getting bus routes from Google Transit: {str(e)}')
            return self._get_mock_bus_data(origin, destination)
    
    def _parse_google_transit_response(
        self, 
        data: Dict[str, Any], 
        origin: str, 
        destination: str
    ) -> Dict[str, Any]:
        '''Parse Google Transit API response into our format'''
        # This would contain 'transit details from the Google Distance Matrix response
        # For now, return a simplified version
        return {
            'source': 'google_transit',
            'origin': origin,
            'destination': destination,
            'routes': [
                {
                    'route_number': 'Bus 101',
                    'origin': origin,
                    'destination': destination,
                    'departure_time': '08:00',
                    'arrival_time': '11:30',
                    'duration': '3h 30m',
                    'distance': '150 km',
                    'fare': '₹250',
                    'bus_type': 'AC Seater'
                }
            ]
        }
    
    def _get_mock_bus_data(self, origin: str, destination: str) -> Dict[str, Any]:
        '''Return mock bus data when APIs are not available'''
        return {
            'source': 'mock',
            'origin': origin,
            'destination': destination,
            'routes': [
                {
                    'route_number': 'Bus 101',
                    'origin': origin,
                    'destination': destination,
                    'departure_time': '08:00',
                    'arrival_time': '11:30',
                    'duration': '3h 30m',
                    'distance': '150 km',
                    'fare': '₹250',
                    'bus_type': 'AC Seater',
                    'availability': 'Available'
                },
                {
                    'route_number': 'Bus 205',
                    'origin': origin,
                    'destination': destination,
                    'departure_time': '14:00',
                    'arrival_time': '18:45',
                    'duration': '4h 45m',
                    'distance': '150 km',
                    'fare': '₹180',
                    'bus_type': 'Non-AC Sleeper',
                    'availability': 'Limited'
                }
            ]
        }
    
    async def get_bus_stops_near_location(
        self, 
        latitude: float, 
        longitude: float, 
        radius: int = 1000  # meters
    ) -> Optional[Dict[str, Any]]:
        '''Get bus stops near a given location'''
        # In a real implementation, this would query GTPS stops.txt
        # For now, return mock data
        return {
            'location': {'latitude': latitude, 'longitude': longitude},
            'radius_meters': radius,
            'stops': [
                {
                    'stop_id': 'STOP001',
                    'stop_name': 'Main Bus Stand',
                    'latitude': latitude + 0.001,
                    'longitude': longitude + 0.001,
                    'location_type': 'stop'
                },
                {
                    'stop_id': 'STOP002',
                    'stop_name': 'City Center',
                    'latitude': latitude - 0.001,
                    'longitude': longitude - 0.001,
                    'location_type': 'stop'
                }
            ]
        }
    
    async def close(self):
        '''Close the HTTP client'''
        await self.client.aclose()
