# Functional Requirements.md

# TravelMate AI — Functional Requirements

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Format:** FR-[module]-[sequence]: [Requirement Statement]

---

## Module 1: Trip Planning (TP)

### FR-TP-001: Origin Input
The system shall accept an origin in any of the following formats:
- Indian city name (e.g., "Navsari")
- Railway station name (e.g., "Nashik Road Railway Station")
- Temple or landmark name (e.g., "Siddhivinayak Temple")
- Full postal address
- GPS coordinates (from device location)

### FR-TP-002: Destination Input
The system shall accept a destination in any of the same formats as origin (FR-TP-001).

### FR-TP-003: Fuzzy Location Matching
The system shall implement fuzzy matching to resolve misspelled or colloquial location names. Confidence threshold for auto-accepting a match: 85%. Below 85%, a disambiguation dialog is presented.

### FR-TP-004: Geocoding
The system shall convert all text location inputs to latitude/longitude coordinates using the Google Maps Geocoding API before any routing is attempted.

### FR-TP-005: Date and Time Input
The system shall accept a desired travel date (calendar picker, dates up to 120 days in advance) and preferred departure time (morning 6–10am / afternoon 10am–4pm / evening 4–8pm / specific time).

### FR-TP-006: Multi-Modal Route Generation
The system shall generate a complete journey plan combining any subset of:
- Walking (up to 2km without user override)
- Auto-rickshaw / cab (first and last mile)
- Local bus (intra-city)
- State bus (inter-city, GSRTC/MSRTC)
- Metro (where available: Delhi, Mumbai, Bengaluru, Chennai, Hyderabad)
- Train (Indian Railways inter-city)
- Flight (where distance > 600km or time savings justify)
- Shared taxi (where data available)

### FR-TP-007: Transport Leg Specification
Each transport leg in the itinerary shall include:
- Mode of transport
- Departure location (name + address)
- Arrival location (name + address)
- Scheduled departure time
- Scheduled arrival time
- Estimated duration
- Estimated cost (INR)
- Confidence score (HIGH/MEDIUM/LOW)
- Data source attribution
- Data freshness timestamp

### FR-TP-008: Transfer Buffer Enforcement
The system shall insert a minimum buffer between consecutive transport legs:
- Train connections: 15 minutes minimum
- Bus connections: 10 minutes minimum
- Flight connections: 90 minutes minimum
- Walking to another mode: walking time + 5 minutes buffer

### FR-TP-009: Alternative Routes
The system shall generate three alternative itinerary options after the primary plan:
- **Fastest:** Minimizes total travel time
- **Cheapest:** Minimizes total cost (may add transfers)
- **Comfortable:** Minimizes number of mode changes

### FR-TP-010: Return Trip Generation
The system shall generate a return trip itinerary by reversing origin/destination and accepting a return date/time input, reusing cached data where applicable.

### FR-TP-011: Multi-City Planning
The system shall accept up to 5 waypoints and generate a sequential itinerary A→B→C→D→E.

### FR-TP-012: Group Travel Input
The system shall accept group size (number of adults, children, senior citizens) and use this to:
- Show group pricing where applicable
- Prioritize accessibility-compliant routes when senior citizens are in the group
- Show family-friendly accommodation options

---

## Module 2: Train Data (TR)

### FR-TR-001: Train Schedule Lookup
The system shall query real train schedules via the RailwayAPI.in (or equivalent) for a given origin station, destination station, and travel date.

### FR-TR-002: Train Not Running Alert
The system shall detect when a queried train does not operate on the requested date (due to weekday restrictions, holiday schedules, or cancellations) and display an appropriate warning.

### FR-TR-003: Train Class Display
The system shall display available seat classes for each train:
- General (GEN)
- Sleeper (SL)
- Third AC (3A)
- Second AC (2A)
- First AC (1A)
- Chair Car (CC)
- Second Sitting (2S)

### FR-TR-004: Real-Time Running Status
The system shall display real-time train running status (on time / delayed by X minutes) when this data is available from NTES API, with clear data source attribution.

### FR-TR-005: Train Not Found Fallback
When no direct train exists between origin and destination stations, the system shall:
1. Suggest trains to the nearest major junction
2. Suggest bus alternatives
3. Inform the user with a clear explanation

---

## Module 3: Bus Data (BU)

### FR-BU-001: GTFS Data Query
The system shall query GTFS (General Transit Feed Specification) feeds from available state transport operators for bus routes between stops.

### FR-BU-002: Multi-Source Bus Fallback
When GTFS data is unavailable for a region, the system shall:
1. Query Google Transit Directions API
2. Query state transport operator APIs (if available)
3. Use AI-based route reasoning with LOW confidence label
4. Never fabricate bus route numbers

### FR-BU-003: Bus Stop Resolution
The system shall resolve destination addresses to the nearest bus stop using Google Maps Places API.

### FR-BU-004: Bus Data Confidence Labeling
All bus route information shall be labeled with its data source and confidence level. Scheduled GTFS data = MEDIUM (schedule may not reflect real-time operation). AI-estimated route = LOW (verify locally).

---

## Module 4: Weather (WE)

### FR-WE-001: Weather Fetch
The system shall fetch weather forecasts for:
- Origin city (departure day)
- All major transit cities
- Destination (arrival day and next 3 days if multi-day trip)

### FR-WE-002: Weather Display
Weather data displayed shall include:
- High/low temperature (°C)
- Rainfall probability (%)
- Weather condition (sunny, cloudy, rainy, etc.)
- UV index
- Wind speed

### FR-WE-003: Weather Warnings
The system shall display a prominent warning if any of the following are forecast during the journey:
- Heavy rainfall (> 20mm expected)
- Cyclone warning (IMD advisory)
- Extreme heat (> 45°C)
- Fog affecting visibility (winter months, north India)

### FR-WE-004: Weather Confidence
All weather data shall show source (OpenWeatherMap) and forecast date. Forecasts > 5 days old must show a staleness indicator.

---

## Module 5: Temple Information (TM)

### FR-TM-001: Temple Recognition
The system shall recognize destinations as temples/religious sites and automatically surface contextual temple information.

### FR-TM-002: Temple Data Fields
Temple records shall contain:
- Name (official + common names)
- Location (coordinates, address, city, state)
- Opening time (weekday and weekend)
- Closing time
- Puja/aarti schedule (morning, afternoon, evening)
- Darshan type (free / paid / by appointment)
- Dress code
- Photography allowed (yes/no)
- Nearby accommodation (dharamshala, hotels)
- Annual closure dates
- Festival schedule (major events, special darshan timings)

### FR-TM-003: Temple Data Staleness
Temple timing data older than 30 days shall display: "Last updated: [DATE]. Please verify current timings before visiting."

### FR-TM-004: Temple Not Found
When a destination temple is not in the TravelMate database, the system shall:
1. Provide a Google Maps deep link to the temple
2. Provide Google Search link for "[temple name] timings"
3. Advise user to verify timings directly

---

## Module 6: Hotel Suggestions (HO)

### FR-HO-001: Hotel Query
The system shall query for accommodation options near the destination when a multi-day trip is detected or user requests hotel suggestions.

### FR-HO-002: Hotel Display
Hotel results shall show:
- Name
- Distance from destination (km/walking time)
- Price range (₹ per night)
- Star rating
- Vegetarian food availability
- Wheelchair accessibility flag (when known)
- Booking link (affiliate)

### FR-HO-003: Hotel Filters
User shall be able to filter hotel suggestions by:
- Price range
- Distance from destination
- Star rating
- Amenities (AC, WiFi, parking)
- Vegetarian kitchen

---

## Module 7: Budget (BG)

### FR-BG-001: Per-Leg Cost Estimation
The system shall provide a cost estimate for every transport leg in INR.

### FR-BG-002: Total Trip Budget
The system shall compute and display total trip cost as:
- Transport only total
- Transport + food estimate (based on city food cost index)
- Transport + food + accommodation (if hotel selected)

### FR-BG-003: Budget Mode
A "Budget Mode" toggle shall re-optimize the entire itinerary for minimum cost, replacing comfort options with cheapest available alternatives.

### FR-BG-004: Cost Confidence
All cost estimates shall display "(estimate)" label and data source (e.g., "Cab fare: ₹120–150 estimated via Google Maps Distance Matrix").

---

## Module 8: AI Chat (AI)

### FR-AI-001: Itinerary Q&A
The AI chat shall answer any question about the current itinerary in natural language.

### FR-AI-002: Itinerary Modification
The AI chat shall accept natural language modification requests and re-plan affected legs:
- Change departure time
- Change preferred transport mode
- Add a stop
- Avoid a specific city/route

### FR-AI-003: Context Retention
The AI chat shall retain the full conversation context and itinerary context throughout the session.

### FR-AI-004: Hallucination Prevention
The AI shall never fabricate transport data. When asked about data not in its context, it shall state: "I don't have confirmed data for this. I recommend checking [official source]."

### FR-AI-005: Voice Input
The system shall accept voice input for trip planning queries and AI chat using the Web Speech API (English and Hindi).

---

## Module 9: User Account (UA)

### FR-UA-001: Authentication Methods
The system shall support:
- Email OTP (magic link)
- Google OAuth
- Phone number OTP (v1.5)

### FR-UA-002: Trip History
Authenticated users shall have all generated itineraries saved automatically to their trip history.

### FR-UA-003: Saved Trips
Users shall be able to name and save specific trips as favorites.

### FR-UA-004: Preferences
User preferences stored:
- Home address (default origin)
- Preferred transport class (general/sleeper/AC)
- Budget tier (budget/mid/premium)
- Accessibility needs (senior citizen, wheelchair)
- Language preference
- Notification settings

---

## Module 10: Notifications (NO)

### FR-NO-001: Departure Reminders
For any saved trip with a planned date, the system shall send push/email notifications:
- 24 hours before first transport leg
- 2 hours before first transport leg
- 30 minutes before first transport leg

### FR-NO-002: Delay Alerts
When real-time train delay data is available and a user has a matching trip planned, the system shall send a delay alert if the delay exceeds 15 minutes.

### FR-NO-003: Weather Alerts
The system shall send a weather alert 24 hours before a trip if adverse weather is forecast at the destination.

### FR-NO-004: Notification Channels
Supported notification channels:
- PWA push notifications (browser)
- Email (via SendGrid/Resend)
- In-app notification center

---

## Module 11: Emergency (EM)

### FR-EM-001: Emergency Screen
A dedicated emergency screen shall be accessible at all times (no authentication required) showing:
- Police: 100
- Ambulance: 108
- Fire: 101
- Railway police: 1512
- Women's Helpline: 1091
- Tourist helpline: 1800-111-363

### FR-EM-002: Location-Aware Emergency
When location permission is granted, the system shall show the nearest:
- Police station
- Hospital
- Pharmacy

### FR-EM-003: Offline Emergency
Emergency contact data shall be cached for offline access. Cache is refreshed on every app open when online.

---

## Module 12: Offline (OF)

### FR-OF-001: PDF Generation
Any generated itinerary shall be downloadable as a formatted PDF containing all legs, timings, costs, and emergency contacts.

### FR-OF-002: IndexedDB Cache
Downloaded itineraries shall be stored in browser IndexedDB for offline access through the app UI.

### FR-OF-003: Map Tile Cache
Map tiles for the downloaded itinerary region shall be pre-cached for offline map viewing.

### FR-OF-004: Offline Indicator
The app shall detect online/offline status and display a clear banner when operating offline: "You're offline — showing saved trips."
