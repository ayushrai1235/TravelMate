import asyncio
from itertools import permutations, islice

from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis_pool
from app.infrastructure.external.google_maps import GoogleMapsService
from app.infrastructure.external.railway_api import RailwayService
import redis.asyncio as redis

MAJOR_CITIES = [
    "Navsari",
    "Surat",
    "Mumbai",
    "Nashik",
    "Trimbakeshwar",
    "Pune",
    "Ahmedabad",
    "Vadodara",
    "Delhi",
    "Somnath",
    "Ujjain",
]


async def warm_cache() -> None:
    client = redis.Redis(connection_pool=get_redis_pool())
    cache = CacheService(client)
    maps = GoogleMapsService(cache)
    railways = RailwayService(cache)

    for city in MAJOR_CITIES:
        await maps.geocode(city)

    for origin, destination in islice(permutations(MAJOR_CITIES, 2), 100):
        await railways.search_trains(origin, destination, "2026-07-15")

    await client.aclose()


if __name__ == "__main__":
    asyncio.run(warm_cache())
