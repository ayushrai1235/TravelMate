from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api_errors import error_response
from app.core.dependencies import get_cache, get_session
from app.infrastructure.cache.cache_service import CacheService
from app.repositories.temple_repository import TempleRepository
from app.services.temple_service import TempleService

router = APIRouter(prefix="/temples", tags=["temples"])


@router.get("")
async def search_temples(
    query: str | None = Query(default=None, min_length=2, max_length=255),
    city: str | None = Query(default=None, min_length=2, max_length=100),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_session),
    cache: CacheService = Depends(get_cache),
) -> dict[str, list[dict[str, Any]]]:
    service = TempleService(TempleRepository(db), cache)
    return {"data": await service.search_temples(query=query, city=city, limit=limit)}


@router.get("/{temple_id}")
async def get_temple(
    temple_id: str,
    request: Request,
    db: AsyncSession = Depends(get_session),
    cache: CacheService = Depends(get_cache),
):
    service = TempleService(TempleRepository(db), cache)
    temple = await service.get_temple(temple_id)
    if temple is None:
        return error_response(
            request,
            status_code=404,
            code="NOT_FOUND",
            user_message="Temple not found.",
            suggestion="Try searching by city or temple name.",
            details={"temple_id": temple_id},
        )
    return temple
