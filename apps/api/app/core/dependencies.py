from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.connection import get_db


async def get_cache(redis_client=Depends(get_redis)) -> CacheService:
    return CacheService(redis_client)


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncGenerator[AsyncSession, None]:
    yield db
