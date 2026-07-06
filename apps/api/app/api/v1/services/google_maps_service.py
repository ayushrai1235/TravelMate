
import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleMapsService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = 'https://maps.googleapis.com/maps/api'
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        '''Convert address to latitude/longitude coordinates'''
        if not self.api_key:
            logger.warning('Google Maps API key not configured')
            return None
            
        try:
            response = await self.client.get(
                f'{self.base_url}/geocode/json',
                params={
                    'address': address,
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': result['formatted_address'],
                    'place_id': result['place_id'],
                    'types': result['types']
                }
            return None
        except Exception as e:
            logger.error(f'Error geocoding address {address}: {str(e)}')
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        '''Convert latitude/longitude to address'''
        if not self.api_key:
            logger.warning('Google Maps API key not configured')
            return None
            
        try:
            response = await self.client.get(
                f'{self.base_url}/geocode/json',
                params={
                    'latlng': f'{latitude},{longitude}',
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                return {
                    'formatted_address': result['formatted_address'],
                    'place_id': result['place_id'],
                    'types': result['types']
                }
            return None
        except Exception as e:
            logger.error(f'Error reverse geocoding coordinates {latitude},{longitude}: {str(e)}')
            return None
    
    async def distance_matrix(
        self, 
        origins: List[str], 
        destinations: List[str],
        mode: str = 'driving'
    ) -> Optional[Dict[str, Any]]:
        '''Calculate distance and time between origins and destinations'''
        if not self.api_key:
            logger.warning('Google Maps API key not configured')
            return None
            
        try:
            response = await self.client.get(
                f'{self.base_url}/distancematrix/json',
                params={
                    'origins': '|'.join(origins),
                    'destinations': '|'.join(destinations),
                    'mode': mode,
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error calculating distance matrix: {str(e)}')
            return None
    
    async def places_nearby(
        self, 
        latitude: float, 
        longitude: float, 
        radius: int = 1000,
        place_type: str = 'point_of_interest'
    ) -> Optional[Dict[str, Any]]:
        '''Find places near a location'''
        if not self.api_key:
            logger.warning('Google Maps API key not configured')
            return None
            
        try:
            response = await self.client.get(
                f'{self.base_url}/place/nearbysearch/json',
                params={
                    'location': f'{latitude},{longitude}',
                    'radius': radius,
                    'type': place_type,
                    'key': self.api_key
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error searching for nearby places: {str(e)}')
            return None
    
    async def close(self):
        '''Close the HTTP client'''
        await self.client.aclose()
