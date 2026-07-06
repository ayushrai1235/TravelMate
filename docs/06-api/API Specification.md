# API Specification.md

# TravelMate AI — API Specification

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

This document specifies the core REST API endpoints exposed by the FastAPI backend (and consumed by the Next.js BFF).

**Base URL:** `https://api.travelmate.ai/v1`

---

## 2. Trip Planning Endpoints

### 2.1 Plan a New Trip (Streaming)

**Endpoint:** `POST /trips/plan`
**Description:** Initiates AI trip planning and streams the result via Server-Sent Events (SSE).

**Request Headers:**
- `Authorization: Bearer <clerk_jwt>` (Optional)
- `X-User-ID: <user_id>` (Internal BFF header)

**Request Body (JSON):**
```json
{
  "origin": "Navsari",
  "destination": "Trimbakeshwar",
  "travel_date": "2026-07-15",
  "departure_preference": "morning",
  "return_time_preference": "evening",
  "trip_end_time_preference": "20:00",
  "group": {
    "adults": 1,
    "children": 0,
    "seniors": 0
  }
}
```

**Response (text/event-stream):**
```text
data: {"type": "status", "message": "Geocoding locations..."}

data: {"type": "status", "message": "Planning route..."}

data: {"type": "partial", "leg": {"sequence": 1, "mode": "AUTO", ...}}

data: {"type": "context", "weather": {...}}

data: {"type": "complete", "itinerary": {"itinerary_id": "itin_123", "legs": [...]}}
```

### 2.2 List Saved Trips

**Endpoint:** `GET /trips`
**Description:** Returns a paginated list of the user's saved trips.

**Query Parameters:**
- `limit` (int, default: 20)
- `offset` (int, default: 0)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "trip_abc123",
      "origin_name": "Navsari",
      "destination_name": "Trimbakeshwar",
      "travel_date": "2026-07-15",
      "created_at": "2026-07-03T10:00:00Z"
    }
  ],
  "meta": { "total_count": 5, "has_more": false }
}
```

### 2.3 Get Trip Details

**Endpoint:** `GET /trips/{trip_id}`
**Description:** Returns the complete itinerary for a specific trip.

**Response (200 OK):** (Returns `ItineraryResponse` schema)

---

## 3. AI Chat Endpoints

### 3.1 Send Chat Message

**Endpoint:** `POST /chat`
**Description:** Sends a message to the ChatAgent and receives a streamed response.

**Request Body:**
```json
{
  "trip_id": "trip_abc123",
  "message": "Can I leave later?",
  "session_id": "sess_xyz789"  // Optional, for continuing conversation
}
```

**Response (text/event-stream):**
```text
data: {"type": "chunk", "text": "I can help with that. "}
data: {"type": "chunk", "text": "I'll replan for an afternoon departure."}
data: {"type": "action", "action_type": "replan_trigger", "params": {"new_time": "14:00"}}
data: {"type": "done"}
```

---

## 4. User Endpoints

### 4.1 Get User Profile

**Endpoint:** `GET /users/me`
**Description:** Retrieves the current user's profile and preferences.

**Response (200 OK):**
```json
{
  "id": "user_2aBcDeFg",
  "email": "user@example.com",
  "subscription_tier": "explorer",
  "monthly_trips_used": 1,
  "preferences": {
    "home_address": "Navsari, Gujarat",
    "budget_tier": "mid"
  }
}
```

### 4.2 Update User Preferences

**Endpoint:** `PATCH /users/me/preferences`
**Description:** Updates user preferences.

**Request Body:**
```json
{
  "budget_tier": "premium"
}
```
**Response (200 OK):** Updated user object.

---

## 5. Transport Data Endpoints (Internal)

These endpoints are used primarily by the BFF for specific UI components, bypassing the full orchestrator.

### 5.1 Geocode Location

**Endpoint:** `POST /geocode`
**Request Body:** `{"query": "Trimbakeshwar"}`
**Response:** `{"lat": 19.9386, "lng": 73.5302, "name": "Trimbakeshwar, Maharashtra"}`

### 5.2 Get Temple Info

**Endpoint:** `GET /temples/{temple_id}`
**Response:** `TempleData` object

---

## 6. Open API Specification (Swagger)

FastAPI automatically generates the OpenAPI schema.
It is available at:
- Swagger UI: `https://api.travelmate.ai/docs`
- ReDoc: `https://api.travelmate.ai/redoc`
- OpenAPI JSON: `https://api.travelmate.ai/openapi.json`
