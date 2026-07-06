from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.core.config import settings

_pool: redis.ConnectionPool | None = None


def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=50,
            decode_responses=True,
        )
    return _pool


async def get_redis() -> AsyncGenerator[redis.Redis | None, None]:
    client: redis.Redis | None = None
    try:
        client = redis.Redis(connection_pool=get_redis_pool())
        await client.ping()
        yield client
    except redis.RedisError:
        yield None
    finally:
        if client is not None:
            await client.aclose()
