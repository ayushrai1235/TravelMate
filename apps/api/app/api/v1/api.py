
from fastapi import APIRouter
from app.api.v1.endpoints import trips
from app.api.v1 import trains

api_router = APIRouter()

# Include routers
api_router.include_router(trips.router, prefix='/trips', tags=['trips'])
api_router.include_router(trains.router, prefix='/trains', tags=['trains'])

