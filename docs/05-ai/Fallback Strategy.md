# Fallback Strategy.md

# TravelMate AI — Fallback Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Fallback Philosophy

**Core principle:** The user must NEVER be left without an answer. If the best-case data is unavailable, degrade gracefully with clear communication about what is confirmed and what is estimated.

Fallback hierarchy:
```
1. Primary source (official API, real-time data)        → HIGH confidence
2. Secondary source (alternative API, cached data)       → MEDIUM confidence  
3. Rule-based estimation (distance calculations)         → LOW confidence
4. AI-guided estimation (LLM reasoning without tools)   → LOW confidence
5. User advisory (guide user to official source)         → No confidence (advisory)
```

---

## 2. Per-Service Fallback Chains

### 2.1 Train Schedule Fallback

```
RailwayAPI.in (primary)
    ↓ FAIL (5xx, timeout, rate limit)
RailwayAPI.in retry (2x with backoff)
    ↓ FAIL
RapidAPI Indian Railways (alternative provider)
    ↓ FAIL
Static GTFS India train timetable (cached locally)
    ↓ NOT FOUND (route not in GTFS)
Advisory: "Train schedules unavailable. Check IRCTC: irctc.co.in"
+ Plan bus alternative route
```

### 2.2 Bus Route Fallback

```
State GTFS feed (GSRTC, MSRTC, etc.)
    ↓ FAIL or NOT FOUND
Google Transit Directions API
    ↓ FAIL or NOT FOUND  
State transport website scraped data (if available)
    ↓ NOT FOUND
AI-guided route estimation:
    "From [stop], buses run towards [direction] approximately every [N] minutes.
     Fare: approximately ₹[estimate]. Confirm at the bus stand."
    Confidence: LOW
    ↓ ALL SOURCES FAIL
Advisory: "Bus route data unavailable for this area. 
    Hire an auto/cab from [origin point] to [destination]. 
    Estimated cost: ₹[distance * 15]/km"
```

### 2.3 Geocoding Fallback

```
Google Maps Geocoding API
    ↓ FAIL (429, 500)
Mapbox Geocoding API
    ↓ FAIL
OpenStreetMap Nominatim API (rate-limited)
    ↓ FAIL
Error: "Location services temporarily unavailable. Please try again."
```

### 2.4 Weather Fallback

```
OpenWeatherMap One Call API
    ↓ FAIL
OpenWeatherMap retry (1x)
    ↓ FAIL
Hide weather section entirely
    Message: "Weather data temporarily unavailable."
    Do NOT block itinerary generation (weather is supplementary)
```

### 2.5 Temple Data Fallback

```
TravelMate Temple Database (PostgreSQL)
    ↓ NOT FOUND
Google Maps Places API (search for temple name)
    ↓ FOUND → Display basic info (name, location, rating) from Google
    ↓ NOT FOUND
Advisory: "Temple information not in our database.
    Google Maps: [deep link]
    Google Search: [temple name + timings]"
```

### 2.6 Hotel Suggestions Fallback

```
Google Maps Places API (type: hotel, near destination)
    ↓ FAIL or NO RESULTS
Cached hotel data for the city (if available)
    ↓ NOT FOUND
Advisory: "Hotel suggestions unavailable. 
    Search on Booking.com: [deep link]
    Search on MakeMyTrip: [deep link]"
```

### 2.7 AI LLM Fallback

```
Google Gemini 3.5 Flash (primary)
    ↓ FAIL (5xx, timeout, rate limit)
Retry 1: Same model, simplified context (1s backoff)
    ↓ FAIL
Retry 2: Same model, minimal prompt (3s backoff)
    ↓ FAIL
Retry 3: Same model, last attempt (9s backoff)
    ↓ FAIL
Rule-based fallback (no LLM):
    1. Look up cached train schedules for the route
    2. Calculate first/last mile as auto (distance * ₹15/km)
    3. Assemble basic itinerary
    4. Mark ALL data as LOW confidence
    5. Message: "AI planning is temporarily unavailable. 
        We've planned your route using our schedule database."
```

---

## 3. Fallback Data Quality Labels

When fallback data is used, the UI clearly communicates:

| Fallback Level | User-Facing Message |
|---|---|
| Secondary API | "Data from [source]. May differ from official schedules." |
| Cached data | "Based on scheduled data from [date]. Verify current schedules." |
| Rule-based estimate | "Route estimated based on distance. Verify locally." |
| AI-guided | "AI-suggested route. Not confirmed by official sources." |
| Advisory only | "Data unavailable. We recommend checking [official source]." |

---

## 4. Degraded Itinerary Display

When fallback produces a partial itinerary, the UI adapts:

### 4.1 Confirmed Legs vs Estimated Legs

```
┌─────────────────────────────────────┐
│ Leg 1: 🚗 Auto         ✓ CONFIRMED │  ← Google Maps data, HIGH confidence
│ Home → Navsari Station              │
│ ₹50-80                              │
├─────────────────────────────────────┤
│ Leg 2: 🚂 Train        ✓ CONFIRMED │  ← RailwayAPI data, HIGH confidence
│ Navsari → Nashik Road               │
│ ₹180 (Sleeper)                      │
├─────────────────────────────────────┤
│ ⚠️ DATA QUALITY NOTICE              │
│ The following leg uses estimated     │
│ data. Please verify locally.         │
├─────────────────────────────────────┤
│ Leg 3: 🚌 Bus          ⚠ ESTIMATED │  ← GTFS unavailable; AI-guided
│ Nashik Rd → Trimbak                 │
│ ~₹40-55 (approx)                    │
│ "Buses run hourly from Nashik CBS"  │
└─────────────────────────────────────┘
```

### 4.2 Complete Fallback Display

When AI is completely unavailable:

```
┌─────────────────────────────────────┐
│ ⚠️ AI Planning Temporarily          │
│    Unavailable                       │
│                                     │
│ We've planned your route using      │
│ cached schedule data.               │
│                                     │
│ Route: Navsari → Trimbakeshwar      │
│ Estimated Distance: 280 km          │
│ Estimated Duration: 5-7 hours       │
│                                     │
│ Suggested Route:                    │
│ 1. Auto to Navsari Station (~₹60)  │
│ 2. Train to Nashik Road (check      │
│    IRCTC for schedules)             │
│ 3. Bus from Nashik to Trimbak      │
│    (check at bus stand)             │
│                                     │
│ [Open IRCTC] [Open Google Maps]     │
│                                     │
│ Try again later for a complete      │
│ AI-powered itinerary.               │
└─────────────────────────────────────┘
```

---

## 5. Circuit Breaker Pattern

External APIs are wrapped in circuit breakers to prevent cascading failures:

```
States: CLOSED → OPEN → HALF_OPEN

CLOSED (normal): All requests pass through
    → IF 5 failures in 60 seconds → Move to OPEN

OPEN (tripped): All requests immediately return fallback
    → After 30 seconds → Move to HALF_OPEN

HALF_OPEN (testing): Let 1 request through
    → IF success → Move to CLOSED
    → IF failure → Move to OPEN
```

Circuit breakers per external API:
- `google_maps_circuit`
- `railway_api_circuit`
- `openweather_circuit`
- `gemini_circuit`
- `amadeus_circuit`
