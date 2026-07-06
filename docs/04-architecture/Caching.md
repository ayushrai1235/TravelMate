# Caching.md

# TravelMate AI — Caching Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Caching Architecture

```
Request → Application Cache (Redis) → External API Cache (Redis) → External API
```

TravelMate AI caches at two levels:
1. **Application-level:** Full itinerary responses for identical queries
2. **API-level:** Individual external API call results (geocoding, trains, weather)

---

## 2. Cache Entries

### 2.1 Application Cache

| Cache Key Pattern | TTL | Data | Invalidation |
|---|---|---|---|
| `itinerary:{hash(origin+dest+date+time)}` | 30 minutes | Complete itinerary JSON | TTL expiry; manual purge on data update |
| `user:{user_id}:preferences` | 24 hours | User preference JSON | On profile update |
| `user:{user_id}:trip_count` | Until month end | Monthly trip count (free tier limit) | Reset on 1st of month |

### 2.2 External API Cache

| Cache Key Pattern | TTL | Data | Justification |
|---|---|---|---|
| `geocode:{hash(location_text)}` | 7 days | Geocoding result (lat, lng, name) | Locations rarely change |
| `distance:{hash(origin_coords+dest_coords)}` | 24 hours | Distance matrix result | Traffic patterns change daily |
| `trains:{hash(origin_stn+dest_stn+date)}` | 30 minutes | Train schedule results | Schedules change; running status is real-time |
| `bus_gtfs:{hash(origin_stop+dest_stop)}` | 24 hours | GTFS bus route results | GTFS is scheduled data; infrequently updated |
| `weather:{hash(lat+lng+date)}` | 1 hour | Weather forecast | Forecasts update hourly |
| `temple:{temple_id}` | 24 hours | Temple information JSON | Curated data; changes manually |
| `hotels:{hash(lat+lng+budget_tier)}` | 6 hours | Hotel search results | Prices fluctuate; moderate TTL |
| `places:{hash(query+location)}` | 12 hours | Google Places results | POIs change slowly |

### 2.3 Session Cache

| Cache Key Pattern | TTL | Data |
|---|---|---|
| `chat:{session_id}:messages` | 1 hour | AI chat conversation history |
| `rate_limit:{user_id}` | 1 minute | Request count for rate limiting |
| `rate_limit:ip:{ip}` | 1 minute | Request count for IP rate limiting |

---

## 3. Cache Key Construction

All cache keys follow this convention:
```
{domain}:{entity_type}:{hash_or_id}
```

Hash function: SHA-256 of JSON-serialized, sorted key-value parameters, truncated to 16 characters.

```python
import hashlib, json

def cache_key(domain: str, entity: str, params: dict) -> str:
    param_str = json.dumps(params, sort_keys=True)
    hash_val = hashlib.sha256(param_str.encode()).hexdigest()[:16]
    return f"{domain}:{entity}:{hash_val}"

# Example:
# cache_key("trains", "schedule", {"origin": "NVS", "dest": "NK", "date": "2026-07-15"})
# → "trains:schedule:a1b2c3d4e5f6g7h8"
```

---

## 4. Cache Warming

Proactively populate cache for high-value data:

| Data | Strategy | Frequency |
|---|---|---|
| Top 100 route pairs | Pre-compute and cache train schedules | Every 30 minutes (Celery task) |
| Major city geocoding | Pre-cache geocoding for 500 Indian cities | On deployment |
| Temple database | Load all temples into Redis | On deployment |

---

## 5. Cache Invalidation

| Trigger | Action |
|---|---|
| User updates profile | Delete `user:{user_id}:preferences` |
| Admin updates temple | Delete `temple:{temple_id}` |
| New month starts | Reset `user:{user_id}:trip_count` for all free users |
| Train schedule changes | TTL-based expiry (30 min) handles this automatically |
| Deployment | Selective invalidation via deployment script (not full flush) |

**Rule:** Never flush the entire Redis cache on deployment. Use targeted invalidation only.

---

## 6. Cache Miss Strategy

When a cache miss occurs:

1. Execute the actual operation (API call, DB query)
2. Store result in cache with appropriate TTL
3. Return result to caller

If the external API also fails:
1. Check if a stale cache entry exists (Redis doesn't auto-delete expired keys immediately)
2. If stale entry exists: return stale data with `stale: true` flag and `stale_since` timestamp
3. If no stale entry: return error

---

## 7. Redis Configuration

```
maxmemory: 512MB (v1.0), 2GB (v2.0)
maxmemory-policy: allkeys-lru  # Evict least recently used keys when memory full
save: 300 1                     # RDB snapshot every 5 minutes if ≥1 write
appendonly: yes                 # AOF for durability
```
