# Indexes.md

# TravelMate AI — Database Indexes

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

Proper indexing is critical for performance, especially as `trip_plans` and `audit_logs` grow. All foreign keys must have corresponding indexes to prevent full table scans during JOINs and cascade deletes.

---

## 2. Core Indexes

### 2.1 `users` Table

| Index Name | Type | Columns | Purpose |
|---|---|---|---|
| `idx_users_email` | B-Tree | `(email)` | UNIQUE constraint; fast lookup during login sync |
| `idx_users_deleted_at` | B-Tree | `(deleted_at)` | Partial index for filtering active users (`WHERE deleted_at IS NULL`) |

### 2.2 `trip_plans` Table

| Index Name | Type | Columns | Purpose |
|---|---|---|---|
| `idx_trips_user_id` | B-Tree | `(user_id)` | Fast lookup for `/v1/trips` endpoint |
| `idx_trips_travel_date` | B-Tree | `(travel_date)` | Dashboard reporting and finding upcoming trips |
| `idx_trips_created_at` | B-Tree | `(created_at)` | Sorting recent trips |
| `idx_trips_deleted_at` | B-Tree | `(deleted_at)` | Partial index for active trips |

### 2.3 `temples` Table

| Index Name | Type | Columns | Purpose |
|---|---|---|---|
| `idx_temples_city_state` | B-Tree | `(state, city)` | Filtering temples by region |
| `idx_temples_location` | GiST | `(ll_to_earth(lat, lng))` | Earthdistance extension for geographic radius searches |
| `idx_temples_name_trgm` | GIN | `(name gin_trgm_ops)` | pg_trgm extension for fast text autocomplete search |

### 2.4 `notifications` Table

| Index Name | Type | Columns | Purpose |
|---|---|---|---|
| `idx_notif_status_sched` | B-Tree | `(status, scheduled_for)` | Celery worker query: find 'PENDING' notifications due now |
| `idx_notif_user_id` | B-Tree | `(user_id)` | Look up user's notifications |
| `idx_notif_trip_id` | B-Tree | `(trip_id)` | Cascade actions when trip is modified/deleted |

### 2.5 `audit_logs` Table

| Index Name | Type | Columns | Purpose |
|---|---|---|---|
| `idx_audit_created_at` | B-Tree | `(created_at DESC)` | Default sorting for admin dashboard |
| `idx_audit_entity` | B-Tree | `(entity_type, entity_id)` | Fast lookup for entity history |
| `idx_audit_user_id` | B-Tree | `(user_id)` | Look up all actions by a specific user |

---

## 3. JSONB Indexes

We store the complete itinerary in `trip_plans.itinerary_json`. To query inside this structure efficiently without unpacking the JSON in memory, we use GIN (Generalized Inverted Index).

| Index Name | Type | Definition | Purpose |
|---|---|---|---|
| `idx_trips_jsonb_path` | GIN | `USING gin (itinerary_json jsonb_path_ops)` | Enables fast containment queries (`@>`). E.g., Find all trips that contain a train leg |

*Example Query:*
```sql
-- Find trips that used a specific train number
SELECT id FROM trip_plans 
WHERE itinerary_json @> '{"legs": [{"mode": "TRAIN", "train_number": "11057"}]}';
```

---

## 4. Maintenance

1. **Auto-vacuum:** PostgreSQL auto-vacuum is enabled by default to prevent index bloat.
2. **Reindexing:** A weekly maintenance task (Sunday 03:00 IST) runs `REINDEX TABLE CONCURRENTLY trip_plans;` to maintain performance on heavily updated tables.
3. **Unused Index Monitoring:** Datadog agent monitors `pg_stat_user_indexes`. Indexes with `idx_scan = 0` over 30 days are flagged for removal.
