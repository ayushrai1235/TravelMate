# User Stories.md

# TravelMate AI — User Stories

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Format:** As a [persona], I want to [action], so that [benefit].

---

## Epic 1: Trip Planning

### US-001: Basic Trip Request
**As a** traveler,  
**I want to** enter a starting point and a destination in plain text,  
**so that** I receive a complete, multi-modal itinerary without visiting multiple apps.

**Acceptance Criteria:**
- Input accepts natural language (city name, landmark, address)
- Fuzzy matching resolves ambiguous inputs (e.g., "Nasik" → "Nashik")
- System produces at least one valid complete itinerary
- Response time < 8 seconds (P95)
- Each leg of the journey is clearly labeled (Train, Bus, Walk, etc.)

---

### US-002: Multi-Modal Route Synthesis
**As a** traveler,  
**I want to** see an itinerary that combines train + bus + walking,  
**so that** I don't have to plan each segment separately.

**Acceptance Criteria:**
- System detects appropriate transport modes for origin-to-destination pair
- Transit connections include realistic time buffers (minimum 15 minutes for trains)
- Walking legs are included for < 2km segments
- Each transport leg shows: mode, departure point, arrival point, departure time, arrival time, estimated cost
- Map view shows complete route with colored leg indicators

---

### US-003: Travel Date and Time Selection
**As a** traveler,  
**I want to** specify my desired travel date and departure time,  
**so that** the itinerary uses real schedules for that date.

**Acceptance Criteria:**
- Date picker shows dates up to 120 days in advance
- Time input allows morning/afternoon/evening preference or exact time for both departure and return/end of trip
- System uses schedule data for the specified date (considering weekday vs weekend timetables)
- System warns if travel during festival period may have high crowd levels

---

### US-004: Alternative Route Options
**As a** traveler,  
**I want to** see 3 alternative route options (fastest, cheapest, most comfortable),  
**so that** I can choose based on my current preference.

**Acceptance Criteria:**
- Three distinct alternatives are presented after initial plan
- Each alternative shows: total time, total cost, number of transfers
- Fastest option minimizes total travel time
- Cheapest option minimizes total cost (may increase transfers)
- Comfortable option minimizes number of transfers/mode changes

---

### US-005: Return Trip Planning
**As a** traveler,  
**I want to** generate a return trip plan with one click,  
**so that** I don't have to re-enter my details in reverse.

**Acceptance Criteria:**
- "Plan Return" button appears on completed itinerary
- System reverses origin/destination and prompts for return date/time
- Return itinerary is generated using the same quality standards
- Return plan is saved alongside the outward plan in trip history

---

### US-006: Multi-City Planning
**As a** business traveler,  
**I want to** plan A → B → C → D in sequence,  
**so that** I can manage multi-destination trips from a single interface.

**Acceptance Criteria:**
- User can add up to 5 waypoints
- Each leg (A→B, B→C, C→D) is planned independently and combined
- Total trip summary shows aggregate time, cost, and budget
- User can set different departure times for each leg

---

## Epic 2: Contextual Information

### US-007: Temple Timings
**As a** pilgrimage traveler (Rameshbhai),  
**I want to** see temple opening times, puja schedules, and darshan queue estimates,  
**so that** I can plan my arrival to attend morning aarti.

**Acceptance Criteria:**
- Temple data includes: opening time, closing time, puja schedule, prasad timing, closure days
- Special schedule shown for festival dates
- Confidence level shown for all timing data (High/Medium/Low)
- Data source and last-updated timestamp displayed
- Alert shown if travel arrival time may miss the desired puja

---

### US-008: Weather Forecast
**As a** traveler,  
**I want to** see weather forecasts for my journey dates at each key location,  
**so that** I can pack appropriately and anticipate disruptions.

**Acceptance Criteria:**
- Weather shown for: origin (departure day), transit points, destination (arrival day)
- Forecast for up to 7 days
- Shows temperature, rainfall probability, UV index, wind
- Monsoon warnings shown prominently
- Weather source and confidence displayed

---

### US-009: Hotel Suggestions
**As a** family traveler,  
**I want to** see hotel options near my destination sorted by suitability,  
**so that** I can plan accommodation without switching apps.

**Acceptance Criteria:**
- 3–5 hotel options shown per destination
- Shows: hotel name, distance from destination, price range, star rating, vegetarian food availability indicator
- Clicking hotel shows a booking link (affiliate redirect)
- User can filter by price, distance, amenities

---

### US-010: Budget Breakdown
**As a** student traveler (Vikram),  
**I want to** see a per-leg and total cost breakdown,  
**so that** I know exactly how much money to carry.

**Acceptance Criteria:**
- Per-leg cost shown: transport fare + estimated food cost + optional hotel
- Total trip cost shown as range (min–max)
- All costs in INR
- "Budget mode" toggle that replaces all suggestions with cheapest available option
- Export budget as PDF or CSV

---

## Epic 3: AI Chat Interface

### US-011: Natural Language Itinerary Modification
**As a** traveler,  
**I want to** say "change my departure to 6 AM" and have the itinerary update,  
**so that** I don't have to re-enter my complete trip.

**Acceptance Criteria:**
- AI chat accepts modifications to departure time, mode preference, budget, stops
- System re-plans only the affected legs
- Changed legs are highlighted in the timeline view
- Previous version preserved for "undo" action

---

### US-012: Q&A About Itinerary
**As a** foreign tourist (Carlos),  
**I want to** ask "which platform does the train depart from?" and get an accurate answer,  
**so that** I can navigate the station confidently.

**Acceptance Criteria:**
- AI answers questions about any element of the itinerary
- When data is real-time (platform numbers), shows confidence and source
- When data is not available, clearly states "Platform information not yet available; check NTES app on day of travel"
- No fabricated data is ever returned

---

### US-013: Voice Input
**As a** senior citizen (Rameshbhai),  
**I want to** speak my origin and destination instead of typing,  
**so that** I can use the app without struggling with the keyboard.

**Acceptance Criteria:**
- Voice input button prominent in search bar
- Accepts speech in English and Hindi (Gujarati in v2.0)
- Transcription is shown to user before submission
- User can correct transcription before submitting
- Works on mobile browser (Web Speech API)

---

## Epic 4: User Account & Preferences

### US-014: Saved Trips
**As a** returning user,  
**I want to** save my planned trips and access them later,  
**so that** I don't have to re-plan the same routes.

**Acceptance Criteria:**
- "Save Trip" button on any generated itinerary
- Saved trips appear in "My Trips" section
- Trips can be named by user
- Saved trips show last-updated status (data may be stale; user notified)
- Trips can be deleted

---

### US-015: User Profile and Preferences
**As a** returning user,  
**I want to** set my home address and travel preferences once,  
**so that** every future trip starts from the right place.

**Acceptance Criteria:**
- Profile fields: home address, preferred transport modes, budget tier, language, accessibility needs
- Home address used as default origin
- Accessibility flag (senior citizen mode, wheelchair mode) affects route selection
- Preferences persist across sessions

---

## Epic 5: Offline & Notifications

### US-016: Offline Itinerary Download
**As a** traveler in a low-signal area,  
**I want to** download my itinerary before I leave home,  
**so that** I can access it without internet.

**Acceptance Criteria:**
- "Download Offline" button generates PDF with complete itinerary
- PDF includes: all legs, timings, addresses, contact numbers, emergency info
- PDF is saved locally on device
- Previously downloaded itineraries appear in "Offline Trips" section

---

### US-017: Departure Reminders
**As a** traveler,  
**I want to** receive a push notification 2 hours before my train departure,  
**so that** I don't miss my connection.

**Acceptance Criteria:**
- User can enable notifications per trip
- System sends notifications: 24h before, 2h before, 30 min before each major transport leg
- Notification includes: transport mode, departure point, departure time
- Notification links directly to that leg in the app
- Works on PWA push notifications

---

### US-018: Train Delay Alerts
**As a** business traveler (Anjali),  
**I want to** receive an alert if my train is running late,  
**so that** I can adjust my plans accordingly.

**Acceptance Criteria:**
- System monitors train status via NTES/RailwayAPI polling
- Alert sent if train is delayed > 15 minutes from scheduled time
- Alert shows: new estimated departure, new estimated arrival, revised downstream connections
- AI suggests revised connecting legs if delay invalidates next connection

---

## Epic 6: Emergency Assistance

### US-019: Emergency Contacts
**As any** traveler,  
**I want to** access emergency contact numbers with one tap,  
**so that** I can get help quickly in an unfamiliar city.

**Acceptance Criteria:**
- Emergency button always visible in app (floating button)
- Shows: Police (100), Ambulance (108), Railway Police (1512), Women's Helpline (1091)
- Shows nearest police station to current GPS location
- Works offline (data cached)
- No authentication required to access emergency screen

---

### US-020: Group Travel Planning
**As a** family traveler (Sharma family),  
**I want to** plan a trip for 4 people including a senior citizen,  
**so that** the itinerary accounts for accessibility needs.

**Acceptance Criteria:**
- Group size input (number of adults, children, seniors)
- Senior citizen flag triggers wheelchair-accessible route preference
- Child flag triggers family-friendly accommodation preference
- Group pricing shown where applicable (rail group discounts)
- Itinerary note for each leg regarding accessibility

---

## Story Map Overview

```
Epic 1: Trip Planning
  US-001 Basic trip request          [P0]
  US-002 Multi-modal synthesis       [P0]
  US-003 Date/time selection         [P0]
  US-004 Alternative options         [P1]
  US-005 Return trip                 [P1]
  US-006 Multi-city                  [P1]

Epic 2: Contextual Info
  US-007 Temple timings              [P0]
  US-008 Weather                     [P0]
  US-009 Hotel suggestions           [P1]
  US-010 Budget breakdown            [P0]

Epic 3: AI Chat
  US-011 Itinerary modification      [P0]
  US-012 Q&A                         [P0]
  US-013 Voice input                 [P1]

Epic 4: User Account
  US-014 Saved trips                 [P0]
  US-015 Preferences                 [P1]

Epic 5: Offline & Notifications
  US-016 Offline download            [P0]
  US-017 Departure reminders         [P1]
  US-018 Train delay alerts          [P1]

Epic 6: Emergency
  US-019 Emergency contacts          [P0]
  US-020 Group travel                [P2]
```
