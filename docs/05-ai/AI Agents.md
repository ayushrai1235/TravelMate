# AI Agents.md

# TravelMate AI — AI Agents Documentation

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Purpose:** Complete specification of every AI agent in TravelMate AI, including responsibilities, inputs, outputs, prompts, memory, retry logic, and fallback strategies.

---

## 1. AI Agent System Overview

TravelMate AI uses a **Hierarchical Multi-Agent System** built on LangGraph. The system consists of:

1. **OrchestratorAgent** — Manages the agent execution graph; synthesizes final output
2. **RouteAgent** — Determines transport mode combinations
3. **TrainAgent** — Queries and interprets train schedule data
4. **BusAgent** — Queries GTFS and Google Transit for bus routes
5. **WeatherAgent** — Retrieves and interprets weather data
6. **TempleAgent** — Retrieves temple/destination contextual information
7. **HotelAgent** — Suggests accommodation options
8. **BudgetAgent** — Computes cost breakdown
9. **ChatAgent** — Handles conversational Q&A and itinerary modification

All agents:
- Operate within a LangGraph `StateGraph`
- Use Google Gemini 3.5 Flash as the reasoning LLM
- Have access only to tools relevant to their domain
- Return structured JSON (Pydantic-validated)
- Include confidence scores on all data claims

---

## 2. OrchestratorAgent

### 2.1 Purpose

The OrchestratorAgent is the master coordinator. It:
- Parses the user's trip request
- Determines which sub-agents to activate
- Schedules parallel vs sequential execution
- Aggregates all sub-agent results
- Synthesizes the final itinerary JSON

### 2.2 Inputs

```json
{
  "origin": {
    "text": "Navsari",
    "coordinates": { "lat": 20.9467, "lng": 72.9520 },
    "resolved_name": "Navsari, Gujarat, India"
  },
  "destination": {
    "text": "Trimbakeshwar Temple",
    "coordinates": { "lat": 19.9386, "lng": 73.5302 },
    "resolved_name": "Trimbakeshwar Temple, Nashik, Maharashtra"
  },
  "travel_date": "2026-07-15",
  "departure_time_preference": "morning",
  "return_time_preference": "evening",
  "trip_end_time_preference": "20:00",
  "group": { "adults": 1, "children": 0, "seniors": 0 },
  "preferences": {
    "budget_tier": "mid",
    "accessibility": false
  }
}
```

### 2.3 Outputs

```json
{
  "itinerary_id": "itin_abc123",
  "itinerary": {
    "total_duration_minutes": 360,
    "total_cost_inr": { "min": 450, "max": 650 },
    "legs": [
      {
        "leg_id": "leg_001",
        "sequence": 1,
        "mode": "AUTO",
        "origin": { "name": "Home, Navsari", "coordinates": {...} },
        "destination": { "name": "Navsari Railway Station", "coordinates": {...} },
        "departure_time": "07:00",
        "arrival_time": "07:20",
        "duration_minutes": 20,
        "train_number": null,
        "bus_number": null,
        "cost_inr": { "min": 50, "max": 80 },
        "confidence": "MEDIUM",
        "data_source": "Google Maps Distance Matrix",
        "notes": "Auto fare is estimated. Negotiate with driver."
      }
    ],
    "contextual_data": {
      "weather": {...},
      "temple": {...},
      "hotels": [...],
      "budget_summary": {...}
    },
    "alternatives": []
  },
  "confidence_summary": {
    "overall": "MEDIUM",
    "low_confidence_legs": ["leg_003"],
    "warnings": []
  }
}
```

### 2.4 LangGraph State

```python
class TripPlanningState(TypedDict):
    # Input
    origin: LocationInput
    destination: LocationInput
    travel_date: str
    departure_preference: str
    return_time_preference: str
    trip_end_time_preference: str
    group: GroupConfig
    preferences: UserPreferences
    
    # Intermediate
    geocoded_origin: GeocodedLocation
    geocoded_destination: GeocodedLocation
    transport_mode_plan: list[str]  # e.g., ["AUTO", "TRAIN", "BUS", "WALK"]
    train_data: TrainData | None
    bus_data: BusData | None
    weather_data: WeatherData | None
    temple_data: TempleData | None
    hotel_data: list[HotelData]
    budget_data: BudgetData | None
    
    # Output
    itinerary: ItineraryResponse | None
    errors: list[AgentError]
    retry_count: int
```

### 2.5 Agent Graph (LangGraph Nodes)

```
START
  │
  ▼
geocode_node          ← Resolves text locations to coordinates
  │
  ▼
plan_transport_node   ← Determines what transport modes are needed
  │
  ├──────────────────────────────────────────────────────────────
  │                 (PARALLEL DISPATCH)
  ├── train_node    ← Calls TrainAgent (if train mode needed)
  ├── weather_node  ← Calls WeatherAgent (always)
  ├── temple_node   ← Calls TempleAgent (if religious destination)
  └── hotel_node    ← Calls HotelAgent (if multi-day trip detected)
  │
  ├──────────────────────────────────────────────────────────────
  │                 (SEQUENTIAL — depends on train arrival point)
  ├── bus_node      ← Calls BusAgent (uses train arrival station as origin)
  │
  ▼
budget_node           ← Calls BudgetAgent (uses all leg data)
  │
  ▼
synthesis_node        ← Combines all results into final ItineraryResponse
  │
  ▼
validate_node         ← ConfidenceValidator checks all claims
  │
  ▼
END → Return ItineraryResponse
```

---

## 3. TrainAgent

### 3.1 Purpose

Queries real Indian Railways train schedule data for the given origin station, destination station, and travel date. Returns structured train options with schedule, class availability, and real-time running status.

### 3.2 Tools Available

```python
@tool
def search_trains(origin_station: str, destination_station: str, date: str) -> list[TrainResult]:
    """Search for trains between two stations on a given date via RailwayAPI.in"""

@tool  
def get_train_running_status(train_number: str, date: str) -> RunningStatus:
    """Get real-time running status of a specific train via NTES"""

@tool
def get_nearest_station(location: dict) -> str:
    """Find the nearest railway station to a GPS coordinate via Google Maps Places API"""
```

### 3.3 Prompt

```
System:
You are TrainAgent, a specialized AI that finds accurate Indian Railways train schedules.

Your ONLY sources of truth are the results from the tools provided to you.
You MUST NOT invent train numbers, names, departure times, or availability.
If a tool returns no data, respond with a structured "no_trains_found" result.
If real-time status is unavailable, leave the running_status field null — do NOT assume "On Time".

Always return a valid JSON response matching the TrainData schema.
Include confidence scores:
- HIGH: Data retrieved directly from official API
- MEDIUM: Data from cached schedules (may be 30 minutes old)
- LOW: Estimated based on historical patterns (never use for actual planning)

User:
Find trains from {origin_station} to {destination_station} on {date}.
```

### 3.4 Output Schema

```json
{
  "trains": [
    {
      "train_number": "11057",
      "train_name": "Mumbai CSMT Amravati Express",
      "origin_station": "Navsari (NVS)",
      "destination_station": "Nashik Road (NK)",
      "departure_time": "07:45",
      "arrival_time": "12:30",
      "duration_minutes": 285,
      "classes_available": ["SL", "3A", "2A"],
      "runs_on_days": ["Mon", "Wed", "Fri", "Sun"],
      "runs_on_date": true,
      "running_status": null,
      "confidence": "HIGH",
      "data_source": "RailwayAPI.in",
      "data_timestamp": "2026-07-03T14:00:00Z"
    }
  ],
  "no_trains_found": false,
  "fallback_suggestion": null
}
```

### 3.5 Retry Strategy

```
Attempt 1: RailwayAPI.in (primary)
    → Failure (5xx, timeout) → Wait 2 seconds
Attempt 2: RailwayAPI.in retry
    → Failure → Wait 5 seconds
Attempt 3: RapidAPI Indian Railways alternative
    → Failure → Activate fallback
Fallback: Static GTFS India train schedules (cached, less fresh)
    → If no data: Return no_trains_found with suggestion to check IRCTC
```

### 3.6 Fallback Behavior

When no train data is available:
1. Return `no_trains_found: true`
2. Provide `fallback_suggestion`: "Check train availability at irctc.co.in or use the NTES app"
3. Set entire train leg confidence to `null` (not displayed as LOW — simply omitted)
4. OrchestratorAgent then plans a bus-only alternative

---

## 4. BusAgent

### 4.1 Purpose

Finds bus routes connecting a transit hub (e.g., train arrival station) to the final destination, or connecting any two points for intra-city/inter-city bus travel.

### 4.2 Tools Available

```python
@tool
def search_gtfs_routes(origin_stop: str, destination_stop: str, date: str) -> list[BusRoute]:
    """Search GTFS feeds for bus routes between stops"""

@tool
def search_google_transit(origin: dict, destination: dict, departure_time: str) -> list[TransitOption]:
    """Query Google Maps Transit Directions API for bus routes"""

@tool
def find_nearest_bus_stop(coordinates: dict, search_radius_m: int = 500) -> list[BusStop]:
    """Find nearest bus stops to a coordinate using Google Maps Places API"""
```

### 4.3 Multi-Source Fallback Order

```
1. GTFS feeds (GSRTC for Gujarat, MSRTC for Maharashtra, etc.)
2. Google Transit Directions API
3. State transport website scraped data (if available in cache)
4. AI-guided route estimation (LOW confidence)
```

### 4.4 Hallucination Prevention

The BusAgent is explicitly instructed:
- Never invent a bus route number
- Never claim a bus runs at a specific time without tool-confirmed data
- If only AI estimation is possible, use this template:
  ```
  "From [stop name], buses run towards [direction/city] approximately every [N] minutes.
   Approximate fare: ₹[estimate]. Ask locally for the exact bus."
  ```
- Confidence must be LOW for AI-estimated routes

### 4.5 Output Schema

```json
{
  "routes": [
    {
      "route_id": "MSRTC-NK-TBK-001",
      "route_name": "Nashik Road to Trimbak",
      "operator": "MSRTC",
      "bus_number": "MH-15-EG-5678",
      "origin_stop": "Nashik Road Bus Stand",
      "destination_stop": "Trimbak Bus Stand",
      "departure_times": ["08:00", "09:00", "10:00", "11:00"],
      "duration_minutes": 60,
      "fare_inr": { "min": 40, "max": 55 },
      "frequency_minutes": 60,
      "confidence": "MEDIUM",
      "data_source": "GTFS / MSRTC",
      "notes": "Buses from Nashik CBS (Central Bus Stand) also available. Board at Platform 4."
    }
  ],
  "ai_guidance": null,
  "fallback_used": false
}
```

---

## 5. WeatherAgent

### 5.1 Purpose

Fetches weather forecasts for all relevant locations in the trip (origin, transit points, destination) and identifies weather conditions that may affect the journey.

### 5.2 Tools Available

```python
@tool
def get_weather_forecast(lat: float, lng: float, date: str) -> WeatherForecast:
    """Get 7-day weather forecast for coordinates via OpenWeatherMap One Call API"""

@tool
def get_weather_alerts(lat: float, lng: float) -> list[WeatherAlert]:
    """Get active weather alerts/advisories for a location"""
```

### 5.3 Output Schema

```json
{
  "forecasts": [
    {
      "location": "Nashik, Maharashtra",
      "date": "2026-07-15",
      "temperature_max_c": 32,
      "temperature_min_c": 24,
      "rainfall_mm": 15,
      "rainfall_probability": 0.75,
      "condition": "Heavy Rain",
      "condition_icon": "rain",
      "uv_index": 4,
      "wind_speed_kmh": 22,
      "confidence": "HIGH",
      "data_source": "OpenWeatherMap"
    }
  ],
  "alerts": [
    {
      "type": "MONSOON_HEAVY_RAIN",
      "severity": "HIGH",
      "message": "Heavy rainfall expected in Nashik district. Carry rain gear. Road travel may be affected."
    }
  ]
}
```

---

## 6. TempleAgent

### 6.1 Purpose

Retrieves detailed information about temple or religious destinations: timings, puja schedule, dress code, crowd levels, and festival calendar.

### 6.2 Tools Available

```python
@tool
def get_temple_by_name(name: str) -> Temple | None:
    """Look up temple in TravelMate temple database by name"""

@tool
def get_temple_by_coordinates(lat: float, lng: float, radius_m: int = 1000) -> list[Temple]:
    """Find temples near given coordinates"""

@tool
def get_temple_festival_schedule(temple_id: str, date: str) -> FestivalInfo | None:
    """Check if a specific date has a festival schedule for the temple"""
```

### 6.3 Output Schema

```json
{
  "temple": {
    "id": "temple_trimbakeshwar",
    "name": "Trimbakeshwar Jyotirlinga Temple",
    "location": {
      "address": "Temple Road, Trimbak, Nashik, Maharashtra 422212",
      "coordinates": { "lat": 19.9386, "lng": 73.5302 }
    },
    "timings": {
      "opening_time": "05:30",
      "closing_time": "21:00",
      "morning_aarti": "06:00",
      "afternoon_aarti": "12:00",
      "evening_aarti": "19:00"
    },
    "darshan_info": {
      "type": "FREE",
      "paid_option": "Special Darshan: ₹200 for priority queue",
      "average_queue_time_minutes": 45,
      "crowd_level_general": "MODERATE"
    },
    "dress_code": "Traditional attire preferred. No shorts or sleeveless.",
    "photography": "Not allowed inside main shrine",
    "closed_dates": [],
    "nearby_dharamshalas": ["Shri Kshetra Trimbakeshwar Dharamshala"],
    "festival_on_date": {
      "is_festival": false,
      "festival_name": null,
      "expected_crowd": "NORMAL"
    },
    "data_freshness": {
      "last_updated": "2026-06-01",
      "is_stale": true,
      "staleness_warning": "Information last updated 32 days ago. Please verify current timings before visiting."
    },
    "confidence": "HIGH",
    "data_source": "TravelMate Temple Database v1"
  },
  "not_found": false,
  "external_links": {
    "google_maps": "https://maps.google.com/?q=Trimbakeshwar+Temple",
    "official_website": "https://www.trimbakeshwar.org"
  }
}
```

---

## 7. HotelAgent

### 7.1 Purpose

Suggests accommodation options near the destination based on user's budget tier, group size, and accessibility needs.

### 7.2 Tools Available

```python
@tool
def search_hotels(
    location: dict, 
    checkin_date: str, 
    budget_tier: str,  # "budget" | "mid" | "premium"
    amenities: list[str]
) -> list[Hotel]:
    """Search for hotels via Google Maps Places API filtered by type and rating"""
```

### 7.3 Output Schema

```json
{
  "hotels": [
    {
      "id": "hotel_001",
      "name": "Hotel Trimbak Residency",
      "distance_from_destination_m": 500,
      "distance_walk_minutes": 7,
      "price_range_inr": { "min": 800, "max": 1500 },
      "star_rating": 3,
      "vegetarian_food": true,
      "wheelchair_accessible": false,
      "google_rating": 4.1,
      "booking_link": "https://www.booking.com/...",
      "affiliate_link": "https://travelmate.ai/affiliate/hotel_001",
      "confidence": "MEDIUM",
      "data_source": "Google Maps Places API"
    }
  ],
  "dharamshalas": [
    {
      "name": "Shri Kshetra Dharamshala",
      "distance_m": 200,
      "price_range_inr": { "min": 0, "max": 300 },
      "vegetarian_food": true,
      "notes": "Free stay may be available for pilgrims. Contact temple trust."
    }
  ]
}
```

---

## 8. BudgetAgent

### 8.1 Purpose

Aggregates cost estimates from all transport legs, adds food cost estimates, and computes a total trip budget range.

### 8.2 Inputs

Receives the complete `legs` array from all transport agents plus `group` configuration.

### 8.3 Output Schema

```json
{
  "budget": {
    "transport": {
      "legs": [
        { "leg_id": "leg_001", "mode": "AUTO", "cost_inr": { "min": 50, "max": 80 } },
        { "leg_id": "leg_002", "mode": "TRAIN_SL", "cost_inr": { "min": 180, "max": 180 } },
        { "leg_id": "leg_003", "mode": "BUS", "cost_inr": { "min": 40, "max": 55 } },
        { "leg_id": "leg_004", "mode": "WALK", "cost_inr": { "min": 0, "max": 0 } }
      ],
      "total": { "min": 270, "max": 315 }
    },
    "food_estimate": {
      "per_person_per_day": { "min": 150, "max": 400 },
      "basis": "Budget dhaba to mid-range restaurant prices in Nashik/Trimbak"
    },
    "total_trip": {
      "transport_only": { "min": 270, "max": 315 },
      "with_food_1day": { "min": 420, "max": 715 },
      "with_accommodation_1night": { "min": 1220, "max": 2215 }
    },
    "confidence": "MEDIUM",
    "notes": "Cab/auto fares are estimates and may vary. Train fares are fixed class fares."
  }
}
```

---

## 9. ChatAgent

### 9.1 Purpose

Handles conversational interaction — answering questions about the itinerary, processing modification requests, and providing general travel guidance.

### 9.2 Context

The ChatAgent receives:
- Full conversation history
- Complete current itinerary JSON
- User preferences
- Trip context (destination type, dates)

### 9.3 Capabilities

| Capability | Example |
|---|---|
| Q&A on itinerary | "What platform does my train depart from?" |
| Modification request | "Change departure to 9 AM" |
| Clarification | "What class of train is this?" |
| General travel advice | "What should I wear to the temple?" |
| Emergency | "I've missed my train. What do I do?" |

### 9.4 Hallucination Guard

Before any response containing transport data, the ChatAgent must cross-reference the itinerary context. If the answer requires real-time data not in context:

**Required response format:**
```
"I don't have confirmed real-time information about [topic]. 
Based on your itinerary, [relevant context]. 
To get the most accurate information, I recommend [official source + link]."
```

### 9.5 Modification Flow

When user requests a modification:
1. ChatAgent extracts intent: `{ "modification_type": "change_departure_time", "new_time": "09:00" }`
2. Returns modification_required flag in response
3. OrchestratorAgent is reinvoked for affected legs only
4. New legs replace old legs; unchanged legs remain
5. Frontend highlights changed legs

---

## 10. Agent Memory System

### 10.1 Session Memory

Within a planning session, the LangGraph state carries all context. This is not persisted between sessions (stateless per request).

### 10.2 Conversation Memory (Chat)

ChatAgent uses LangChain's `ConversationBufferWindowMemory` with:
- Window: Last 20 messages
- Storage: Redis (session-scoped, TTL: 1 hour)
- Context compression: Summarized after 20 messages to stay within token limits

### 10.3 Long-Term Memory (Preferences)

User preferences (home address, transport class, budget tier) stored in PostgreSQL `user_preferences` table. Loaded at session start and injected into agent context.

---

## 11. Confidence Scoring System

Every data claim from every agent must include a confidence score.

### 11.1 Confidence Levels

| Level | Meaning | Examples |
|---|---|---|
| **HIGH** | Data from official API, < 30 minutes old | Train schedule from RailwayAPI, Weather from OpenWeatherMap, Temple from curated DB |
| **MEDIUM** | Scheduled/estimated data; likely accurate but not real-time | GTFS bus schedules, Cab fare from Distance Matrix, Hotel from Places API |
| **LOW** | AI-estimated, unverified, or inferred | AI-guided bus route when GTFS unavailable, crowd prediction |

### 11.2 Confidence Validator

After each agent response, the `ConfidenceValidator` runs:

```
For each data claim in agent output:
  1. Is the claim about a transport entity (train number, bus route, time)?
     → Cross-reference against tool call results in LangGraph state
     → If not in tool results: REJECT — likely hallucination
  
  2. Are all times chronologically valid?
     → Arrival > Departure for every leg
     → No leg ends before it begins
  
  3. Are all required fields present?
     → mode, origin, destination, departure_time, arrival_time, confidence, data_source
  
  4. Is confidence correctly assigned?
     → GTFS data → Must be at least MEDIUM
     → AI-only claim → Must be LOW
```

If validation fails on a critical field (hallucinated train number): **Discard and re-plan.**  
If validation fails on a non-critical field (missing hotel rating): **Flag and continue.**
