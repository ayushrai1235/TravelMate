from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="TravelMate AI API",
    version=settings.VERSION,
    description="Backend API for TravelMate AI",
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.VERSION}


@app.get("/health/ready")
async def health_ready():
    return {"status": "healthy"}
