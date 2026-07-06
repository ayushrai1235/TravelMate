
from fastapi import APIRouter
from app.api.v1.endpoints import trips

api_router = APIRouter()

# Include routers
api_router.include_router(trips.router, prefix='/trips', tags=['trips'])

