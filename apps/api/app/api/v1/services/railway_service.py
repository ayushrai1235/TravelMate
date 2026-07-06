
import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class RailwayService:
    def __init__(self):
        self.api_key = settings.RAILWAY_API_KEY
        # Using RailwayAPI.in via RapidAPI as mentioned in docs
        self.base_url = 'https://railway-indianrailway.p.rapidapi.com'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'railway-indianrailway.p.rapidapi.com'
        } if self.api_key else {}
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_trains_between_stations(
        self, 
        from_station_code: str, 
        to_station_code: str,
        date_of_journey: str  # Format: dd-mm-yyyy
    ) -> Optional[Dict[str, Any]]:
        '''Search for trains between two stations on a given date'''
        if not self.api_key:
            logger.warning('Railway API key not configured')
            return self._get_mock_train_data(from_station_code, to_station_code, date_of_journey)
            
        try:
            response = await self.client.get(
                f'{self.base_url}/trains-between-stations',
                params={
                    'fromStation': from_station_code,
                    'toStation': to_station_code,
                    'dateOfJourney': date_of_journey
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error searching trains between {from_station_code} and {to_station_code}: {str(e)}')
            return self._get_mock_train_data(from_station_code, to_station_code, date_of_journey)
    
    async def get_train_schedule(self, train_number: str) -> Optional[Dict[str, Any]]:
        '''Get schedule for a specific train'''
        if not self.api_key:
            logger.warning('Railway API key not configured')
            return self._get_mock_train_schedule(train_number)
            
        try:
            response = await self.client.get(
                f'{self.base_url}/train-schedule',
                params={'trainNo': train_number},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error getting schedule for train {train_number}: {str(e)}')
            return self._get_mock_train_schedule(train_number)
    
    async def get_station_code(self, station_name: str) -> Optional[str]:
        '''Get station code from station name'''
        # This would typically call an API, but for now we'll use a simple mapping
        # In a real implementation, this would call the Railway API's station search
        station_map = {
            'Mumbai Central': 'MMCT',
            'Delhi': 'DLI',
            'Bangalore': 'SBC',
            'Chennai': 'MAS',
            'Kolkata': 'KOAA',
            'Hyderabad': 'HYB',
            'Ahmedabad': 'ADI',
            'Pune': 'PUNE',
            'Jaipur': 'JP',
            'Lucknow': 'LKO',
            'Navsari': 'NVS',
            'Nashik Road': 'NK',
            'Trimbak': 'TKB'  # Nearest to Trimbakeshwar Temple
        }
        return station_map.get(station_name.strip(), None)
    
    def _get_mock_train_data(self, from_station: str, to_station: str, date: str) -> Dict[str, Any]:
        '''Return mock train data when API is not available'''
        from_code = self.get_station_code(from_station) or 'XXX'
        to_code = self.get_station_code(to_station) or 'YYY'
        
        return {
            'response_code': '200',
            'train_between_station': [
                {
                    'train_number': '12909',
                    'train_name': 'Mumbai Rajdhani',
                    'from_station_code': from_code,
                    'from_station_name': from_station,
                    'to_station_code': to_code,
                    'to_station_name': to_station,
                    'departure_time': '06:00',
                    'arrival_time': '14:30',
                    'duration': '8h 30m',
                    'days': 'M,Tu,W,Th,F,Sa,Su',
                    'classes_available': ['1A', '2A', '3A', 'SL']
                },
                {
                    'train_number': '12907',
                    'train_name': 'August Kranti Rajdhani',
                    'from_station_code': from_code,
                    'from_station_name': from_station,
                    'to_station_code': to_code,
                    'to_station_name': to_station,
                    'departure_time': '17:20',
                    'arrival_time': '02:10',
                    'duration': '8h 50m',
                    'days': 'M,W,F,Su',
                    'classes_available': ['1A', '2A', '3A', 'SL']
                }
            ]
        }
    
    def _get_mock_train_schedule(self, train_number: str) -> Dict[str, Any]:
        '''Return mock train schedule when API is not available'''
        return {
            'response_code': '200',
            'route': [
                {
                    'station_code': 'MMCT',
                    'station_name': 'Mumbai Central',
                    'arrival_time': 'Source',
                    'departure_time': '06:00',
                    'day': '1',
                    'distance': '0'
                },
                {
                    'station_code': 'VT',
                    'station_name': 'Mumbai VT',
                    'arrival_time': '06:15',
                    'departure_time': '06:20',
                    'day': '1',
                    'distance': '2'
                },
                {
                    'station_code': 'BCT',
                    'station_name': 'Mumbai Central',
                    'arrival_time': '06:35',
                    'departure_time': '06:40',
                    'day': '1',
                    'distance': '5'
                }
            ]
        }
    
    async def close(self):
        '''Close the HTTP client'''
        await self.client.aclose()
