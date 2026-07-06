from typing import Any

from app.infrastructure.cache.cache_keys import temple_key, temple_search_key
from app.infrastructure.cache.cache_service import CacheService
from app.repositories.temple_repository import TempleRepository


class TempleService:
    def __init__(self, repository: TempleRepository, cache: CacheService):
        self.repository = repository
        self.cache = cache

    async def get_temple(self, temple_id: str) -> dict[str, Any] | None:
        cache_key = temple_key(temple_id)
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return {**cached, "cache_hit": True}

        temple = await self.repository.get_by_id(temple_id)
        if temple is not None:
            await self.cache.set_json(cache_key, temple, ttl_seconds=86400)
            return {**temple, "cache_hit": False}
        return None

    async def search_temples(
        self,
        query: str | None = None,
        city: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        cache_key = temple_search_key({"query": query, "city": city, "limit": limit})
        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return cached

        temples = await self.repository.search(query=query, city=city, limit=limit)
        await self.cache.set_json(cache_key, temples, ttl_seconds=86400)
        return temples
