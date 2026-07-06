# Schema.md

# TravelMate AI — Database Schema

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Database:** PostgreSQL 16

---

## 1. Schema Design Principles

1. **UUIDv4** for all primary keys (prevents ID enumeration, allows offline generation).
2. **Timestamps** (`created_at`, `updated_at`) on every table.
3. **Soft Deletes** (`deleted_at`) for core entities (users, trips).
4. **JSONB** for unstructured or highly variable data (itinerary legs, AI context).
5. **Foreign Keys** enforced at the database level.

---

## 2. Table Definitions

### 2.1 `users`
Core user identity (synced from Clerk).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Matches Clerk user_id |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's primary email |
| `full_name` | VARCHAR(255) | | User's full name |
| `subscription_tier` | VARCHAR(50) | DEFAULT 'free' | 'free', 'explorer', 'pro', 'business' |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | Soft delete marker |

### 2.2 `user_preferences`
User travel preferences. 1-to-1 with `users`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | UUID | PK, FK(users.id) | |
| `home_address` | TEXT | | Default origin |
| `home_lat` | DECIMAL(10,8) | | |
| `home_lng` | DECIMAL(11,8) | | |
| `budget_tier` | VARCHAR(50) | DEFAULT 'mid' | 'budget', 'mid', 'premium' |
| `preferred_class` | VARCHAR(50) | DEFAULT 'SL' | Train class preference |
| `accessibility_senior`| BOOLEAN | DEFAULT FALSE | |
| `accessibility_wheelchair`| BOOLEAN | DEFAULT FALSE | |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | |

### 2.3 `trip_plans`
A single end-to-end itinerary.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK(users.id) | |
| `origin_name` | VARCHAR(255) | NOT NULL | e.g. "Navsari" |
| `destination_name`| VARCHAR(255) | NOT NULL | e.g. "Trimbakeshwar" |
| `travel_date` | DATE | NOT NULL | |
| `total_duration_min`| INTEGER | | Total trip duration |
| `total_cost_min` | INTEGER | | Lower bound cost estimate |
| `total_cost_max` | INTEGER | | Upper bound cost estimate |
| `itinerary_json` | JSONB | NOT NULL | The complete itinerary payload |
| `overall_confidence`| VARCHAR(20) | | 'HIGH', 'MEDIUM', 'LOW' |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULL | Soft delete marker |

### 2.4 `temples`
Curated database of religious sites.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(100) | PRIMARY KEY | e.g. "temple_trimbakeshwar" |
| `name` | VARCHAR(255) | NOT NULL | |
| `lat` | DECIMAL(10,8) | NOT NULL | |
| `lng` | DECIMAL(11,8) | NOT NULL | |
| `city` | VARCHAR(100) | NOT NULL | |
| `state` | VARCHAR(100) | NOT NULL | |
| `timings` | JSONB | | Open/close, aarti times |
| `darshan_info` | JSONB | | Types, queues |
| `dress_code` | TEXT | | |
| `is_active` | BOOLEAN | DEFAULT TRUE | |
| `last_verified_at`| TIMESTAMPTZ | | For data freshness check |

### 2.5 `notifications`
Scheduled and sent notifications.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK(users.id) | |
| `trip_id` | UUID | FK(trip_plans.id) | |
| `type` | VARCHAR(50) | NOT NULL | 'REMINDER', 'DELAY', 'WEATHER' |
| `scheduled_for` | TIMESTAMPTZ | NOT NULL | When to send |
| `sent_at` | TIMESTAMPTZ | NULL | When it was actually sent |
| `status` | VARCHAR(20) | DEFAULT 'PENDING'| 'PENDING', 'SENT', 'FAILED', 'CANCELLED' |
| `payload` | JSONB | | Message content |

### 2.6 `audit_logs`
System activity logging for security and compliance.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK(users.id) | Can be null (system events) |
| `action` | VARCHAR(100) | NOT NULL | e.g. 'USER_DELETED', 'SUBSCRIPTION_UPGRADED' |
| `entity_type` | VARCHAR(50) | | e.g. 'user', 'trip' |
| `entity_id` | VARCHAR(255) | | |
| `details` | JSONB | | |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 3. JSONB Structures

### 3.1 `trip_plans.itinerary_json`
Instead of creating dozens of relational tables for trip legs, transfers, and weather, the complete AI-generated itinerary is stored as a structured JSONB document.

**Why JSONB?**
1. Trip structures vary wildly (some have flights, some only walking).
2. The AI generates the complete object at once.
3. Reading a trip is a single row fetch (O(1) complexity) instead of a 6-table JOIN.
4. Schema flexibility as we add new transport modes.

*Structure matches the `ItineraryResponse` schema documented in AI Agents.md.*
