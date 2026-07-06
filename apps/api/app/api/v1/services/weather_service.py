
import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHERMAP_API_KEY
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        '''Get current weather for latitude and longitude'''
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = await self.client.get(f'{self.base_url}/weather', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error fetching current weather: {e}')
            return self._get_mock_weather(lat, lon)
    
    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict[str, Any]]:
        '''Get weather forecast for latitude and longitude'''
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = await self.client.get(f'{self.base_url}/forecast', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error fetching weather forecast: {e}')
            return self._get_mock_forecast(lat, lon, days)
    
    async def get_one_call(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        '''Get One Call API data (current, minutely, hourly, daily)'''
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = await self.client.get(f'{self.base_url}/onecall', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error fetching One Call weather data: {e}')
            return self._get_mock_one_call(lat, lon)
    
    def _get_mock_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        '''Return mock current weather data'''
        return {
            'coord': {'lon': lon, 'lat': lat},
            'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
            'base': 'stations',
            'main': {
                'temp': 25.0,
                'feels_like': 25.0,
                'temp_min': 22.0,
                'temp_max': 28.0,
                'pressure': 1012,
                'humidity': 60
            },
            'visibility': 10000,
            'wind': {'speed': 3.5, 'deg': 180},
            'clouds': {'all': 0},
            'dt': 1626097200,
            'sys': {
                'type': 2,
                'id': 2000789,
                'country': 'IN',
                'sunrise': 1626072443,
                'sunset': 1626115762
            },
            'timezone': 19800,
            'id': 1275339,
            'name': 'Mumbai',
            'cod': 200
        }
    
    def _get_mock_forecast(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        '''Return mock forecast data'''
        import datetime
        base_time = int(datetime.datetime.now().timestamp())
        
        forecast_list = []
        for i in range(days * 8):  # 8 intervals per day (3-hour intervals)
            dt = base_time + (i * 3 * 3600)  # 3 hours in seconds
            forecast_list.append({
                'dt': dt,
                'main': {
                    'temp': 25.0 + (i % 5),  # Vary temperature slightly
                    'feels_like': 25.0 + (i % 5),
                    'temp_min': 22.0 + (i % 5),
                    'temp_max': 28.0 + (i % 5),
                    'pressure': 1012,
                    'humidity': 60 + (i % 20)
                },
                'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
                'clouds': {'all': 0},
                'wind': {'speed': 3.5, 'deg': 180},
                'visibility': 10000,
                'pop': 0.0  # Probability of precipitation
            })
        
        return {
            'cod': '200',
            'message': 0,
            'cnt': len(forecast_list),
            'list': forecast_list,
            'city': {
                'id': 1275339,
                'name': 'Mumbai',
                'coord': {'lat': lat, 'lon': lon},
                'country': 'IN',
                'population': 1000000,
                'timezone': 19800,
                'sunrise': 1626072443,
                'sunset': 1626115762
            }
        }
    
    def _get_mock_one_call(self, lat: float, lon: float) -> Dict[str, Any]:
        '''Return mock One Call API data'''
        import datetime
        now = int(datetime.datetime.now().timestamp())
        
        return {
            'lat': lat,
            'lon': lon,
            'timezone': 'Asia/Kolkata',
            'timezone_offset': 19800,
            'current': self._get_mock_weather(lat, lon),
            'minutely': [{'dt': now + (i * 60), 'precipitation': 0} for i in range(60)],
            'hourly': [
                {
                    'dt': now + (i * 3600),
                    'temp': 25.0 + (i % 5),
                    'feels_like': 25.0 + (i % 5),
                    'pressure': 1012,
                    'humidity': 60 + (i % 20),
                    'dew_point': 18.0,
                    'clouds': 0,
                    'visibility': 10000,
                    'wind_speed': 3.5,
                    'wind_deg': 180,
                    'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
                    'pop': 0.0
                } for i in range(48)  # 48 hours
            ],
            'daily': [
                {
                    'dt': now + (i * 86400),
                    'sunrise': now + (i * 86400) + 21600,
                    'sunset': now + (i * 86400) + 46800,
                    'moonrise': 0,
                    'moonset': 0,
                    'moon_phase': 0.5,
                    'temp': {
                        'day': 28.0,
                        'min': 22.0,
                        'max': 35.0,
                        'night': 24.0,
                        'eve': 26.0,
                        'morn': 20.0
                    },
                    'feels_like': {
                        'day': 28.0,
                        'night': 24.0,
                        'eve': 26.0,
                        'morn': 20.0
                    },
                    'pressure': 1012,
                    'humidity': 60,
                    'dew_point': 18.0,
                    'wind_speed': 3.5,
                    'wind_deg': 180,
                    'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}],
                    'clouds': 0,
                    'pop': 0.0,
                    'uvi': 8.5
                } for i in range(8)  # 8 days
            ]
        }
    
    async def close(self):
        '''Close the HTTP client'''
        await self.client.aclose()
