# Decision Engine.md

# TravelMate AI — Decision Engine

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Purpose

The Decision Engine is the rule-based logic layer that works alongside the AI agents. While the AI LLM handles complex reasoning and natural language, the Decision Engine handles deterministic business logic that must be consistent and auditable.

---

## 2. Decision Points

### 2.1 Should We Include a Train Leg?

```
INPUT: origin_station, destination_station, distance_km, user_preferences
OUTPUT: include_train (boolean), reason (string)

RULES:
1. IF distance < 30km → NO ("Distance too short for train")
2. IF no railway station within 20km of origin → NO ("No nearby station")
3. IF no railway station within 20km of destination → NO ("No station near destination")
4. IF user_preference.avoid_trains = true → NO ("User preference")
5. IF distance 30-50km → YES but also plan bus alternative
6. IF distance > 50km → YES (primary transport recommendation)
```

### 2.2 Should We Include a Flight Leg?

```
INPUT: distance_km, user_budget_tier, departure_preference
OUTPUT: include_flight (boolean), reason (string)

RULES:
1. IF distance < 300km → NO ("Too short for flight")
2. IF user_budget_tier = "budget" → NO unless distance > 1000km
3. IF distance 300-800km → Optional (show as alternative to train)
4. IF distance > 800km → YES (recommended, train as alternative)
5. IF no airport within 100km of origin → NO
6. IF no airport within 100km of destination → NO
```

### 2.3 Free Tier Trip Limit Check

```
INPUT: user_id, subscription_tier
OUTPUT: allow_plan (boolean), remaining_trips (int)

RULES:
1. IF tier = "free" AND monthly_trip_count >= 3 → DENY
2. IF tier = "explorer" AND monthly_trip_count >= 20 → DENY
3. IF tier = "pro" or "business" → ALLOW (unlimited)
4. IF user not authenticated → ALLOW first 3 trips (tracked by session cookie)
```

### 2.4 Notification Scheduling

```
INPUT: trip, notification_preferences
OUTPUT: scheduled_notifications[]

RULES:
1. IF notifications disabled → []
2. IF trip date is today → [30min reminder only]
3. IF trip date is tomorrow → [24h, 2h, 30min]
4. IF trip date is > 1 day away → [24h before departure]
5. Notification time = departure_time - buffer
6. NEVER schedule a notification in the past
```

### 2.5 Cache Decision

```
INPUT: query_hash, cache_entry
OUTPUT: use_cache (boolean), reason (string)

RULES:
1. IF cache entry exists AND age < TTL → USE CACHE
2. IF cache entry exists AND age > TTL AND external API fails → USE STALE CACHE (mark as stale)
3. IF no cache entry → CACHE MISS (call external API)
4. IF user explicitly requests "refresh" → BYPASS CACHE
```

---

## 3. Scoring and Ranking

### 3.1 Route Scoring

Each generated route is scored on three dimensions:

| Dimension | Weight (Fastest) | Weight (Cheapest) | Weight (Comfortable) |
|---|---|---|---|
| Total time (lower = better) | 0.7 | 0.1 | 0.2 |
| Total cost (lower = better) | 0.1 | 0.7 | 0.2 |
| Number of transfers (lower = better) | 0.1 | 0.1 | 0.5 |
| Walking distance (lower = better) | 0.1 | 0.1 | 0.1 |

**Score calculation:**
```
score = (time_norm * w_time) + (cost_norm * w_cost) + (transfers_norm * w_transfers) + (walk_norm * w_walk)

where *_norm = 1 - (value / max_value_in_alternatives)
```

### 3.2 Hotel Ranking

Hotels are ranked by a weighted score:

```
hotel_score = (0.3 * proximity_score) +     # Closer to destination = higher
              (0.3 * price_score) +          # Closer to budget tier = higher
              (0.2 * rating_score) +          # Higher Google rating = higher
              (0.1 * veg_food_score) +        # Bonus if vegetarian food available
              (0.1 * accessibility_score)     # Bonus if wheelchair accessible (when needed)
```

---

## 4. Decision Audit Trail

Every decision made by the Decision Engine is logged for debugging and transparency:

```json
{
  "decision_id": "dec_abc123",
  "request_id": "req_def456",
  "decision_type": "include_train",
  "inputs": {
    "distance_km": 250,
    "origin_station": "NVS",
    "destination_station": "NK"
  },
  "result": true,
  "reason": "Distance 250km; nearest stations within 5km of both endpoints",
  "timestamp": "2026-07-03T14:00:00Z"
}
```

Stored in structured logs (Datadog); searchable by request_id.
