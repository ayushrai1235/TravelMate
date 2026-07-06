from fastapi import APIRouter

from app.api.v1 import geocode, temples, trips

api_router = APIRouter()
api_router.include_router(trips.router)
api_router.include_router(geocode.router)
api_router.include_router(temples.router)
