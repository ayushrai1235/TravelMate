# Redis Cache Structure.md

# TravelMate AI — Redis Cache Structure

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

Redis is used for caching, session state, rate limiting, and as a message broker for Celery.

---

## 2. Key Namespaces

All keys are prefixed to avoid collisions.

| Namespace | Usage | Data Type | Default TTL |
|---|---|---|---|
| `cache:app:*` | Application-level caching (Itineraries) | JSON String | 30 minutes |
| `cache:api:*` | External API responses (Geocode, Weather) | JSON String | Varies (1h - 7d) |
| `cache:temple:*`| Temple database fast lookup | JSON String | 24 hours |
| `session:chat:*`| ChatAgent conversation memory | JSON String | 1 hour |
| `rate:*` | Rate limiting counters | Integer | 60 seconds |
| `celery:*` | Celery broker/backend keys | List / Hash | Managed by Celery |

---

## 3. Data Structures

### 3.1 Trip Planning Cache
Used to serve identical trip requests instantly without AI invocation.

**Key:** `cache:app:trip:{hash(origin+dest+date)}`
**Type:** `STRING` (JSON)
**TTL:** 1800s (30m)
**Content:** Complete `ItineraryResponse` JSON object.

### 3.2 External API Caches
Stores raw or slightly processed responses from external APIs to reduce billing and latency.

**Key:** `cache:api:geocode:{hash(location_text)}`
**Type:** `STRING` (JSON)
**TTL:** 604800s (7d)
**Content:** `{"lat": 19.9, "lng": 73.5, "name": "Trimbak"}`

**Key:** `cache:api:trains:{hash(origin_stn+dest_stn+date)}`
**Type:** `STRING` (JSON)
**TTL:** 1800s (30m)
**Content:** Array of train schedule objects.

### 3.3 Rate Limiting
Uses Redis `INCR` and `EXPIRE` for atomic rate limiting.

**Key:** `rate:ip:{ip_address}`
**Type:** `STRING` (Integer)
**TTL:** 60s
**Value:** Request count in current minute.

**Key:** `rate:user:{user_id}:plan`
**Type:** `STRING` (Integer)
**TTL:** End of current month
**Value:** Number of free trips planned this month.

### 3.4 Chat Session Memory
LangChain `ConversationBufferWindowMemory` serialization.

**Key:** `session:chat:{session_id}`
**Type:** `STRING` (JSON)
**TTL:** 3600s (1h)
**Content:** Array of `{ "type": "human" | "ai", "content": "..." }`

---

## 4. Connection Management

The FastAPI application uses `redis.asyncio` for non-blocking operations.
A connection pool is initialized on startup:

```python
import redis.asyncio as redis

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    decode_responses=True
)

async def get_redis():
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
```
