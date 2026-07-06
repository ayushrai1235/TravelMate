# ER Diagram.md

# TravelMate AI — Entity Relationship Diagram

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o| USER_PREFERENCES : has
    USERS ||--o{ TRIP_PLANS : creates
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ AUDIT_LOGS : generates
    
    TRIP_PLANS ||--o{ NOTIFICATIONS : triggers
    
    USERS {
        uuid id PK "Matches Supabase ID"
        varchar email UK
        varchar full_name
        varchar subscription_tier
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }
    
    USER_PREFERENCES {
        uuid user_id PK, FK
        text home_address
        decimal home_lat
        decimal home_lng
        varchar budget_tier
        varchar preferred_class
        boolean accessibility_senior
        boolean accessibility_wheelchair
        timestamp updated_at
    }
    
    TRIP_PLANS {
        uuid id PK
        uuid user_id FK
        varchar origin_name
        varchar destination_name
        date travel_date
        int total_duration_min
        int total_cost_min
        int total_cost_max
        jsonb itinerary_json "Contains all legs & AI data"
        varchar overall_confidence
        timestamp created_at
        timestamp deleted_at
    }
    
    TEMPLES {
        varchar id PK
        varchar name
        decimal lat
        decimal lng
        varchar city
        varchar state
        jsonb timings
        jsonb darshan_info
        text dress_code
        boolean is_active
        timestamp last_verified_at
    }
    
    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        uuid trip_id FK
        varchar type
        timestamp scheduled_for
        timestamp sent_at
        varchar status
        jsonb payload
    }
    
    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK "Nullable"
        varchar action
        varchar entity_type
        varchar entity_id
        jsonb details
        timestamp created_at
    }
```

---

## 2. Design Notes

### 2.1 No `trip_legs` Table
Traditional travel apps create separate tables for trips, legs, segments, and transit points. TravelMate AI avoids this by storing the entire itinerary as a `jsonb` column in `TRIP_PLANS`.

**Benefits:**
- Perfect schema flexibility as AI generates new transport combinations.
- Reading a trip is a single query (no complex JOINs).
- Immutable snapshot of the trip exactly as the AI planned it.

### 2.2 Auth Separation
Authentication state (passwords, MFA, social links) lives entirely in Supabase. Our `USERS` table only holds the UUID and profile fields necessary for our application's foreign keys and business logic.

### 2.3 Soft Deletion
`USERS` and `TRIP_PLANS` use `deleted_at` instead of hard deletion. This preserves foreign key integrity in `AUDIT_LOGS` and `NOTIFICATIONS` for historical reporting. A periodic background task anonymizes PII from soft-deleted users after 72 hours (DPDP Act compliance).
