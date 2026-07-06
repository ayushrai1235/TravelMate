import json
import time
from typing import Any

import redis.asyncio as redis

_memory_cache: dict[str, tuple[float, Any]] = {}


class CacheService:
    def __init__(self, client: redis.Redis | None):
        self.client = client

    async def get_json(self, key: str) -> Any | None:
        if self.client is not None:
            try:
                raw = await self.client.get(key)
                if raw is not None:
                    return json.loads(raw)
            except (redis.RedisError, json.JSONDecodeError):
                pass

        cached = _memory_cache.get(key)
        if cached is None:
            return None

        expires_at, value = cached
        if expires_at < time.time():
            _memory_cache.pop(key, None)
            return None
        return value

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        if self.client is not None:
            try:
                await self.client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
                return
            except redis.RedisError:
                pass

        _memory_cache[key] = (time.time() + ttl_seconds, value)

    async def delete(self, key: str) -> None:
        if self.client is not None:
            try:
                await self.client.delete(key)
            except redis.RedisError:
                pass
        _memory_cache.pop(key, None)
