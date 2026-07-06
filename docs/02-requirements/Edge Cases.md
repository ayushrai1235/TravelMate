# Edge Cases.md

# TravelMate AI — Edge Cases

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Purpose:** Documents all known edge cases, their detection logic, and required system behavior.

---

## 1. Location and Geocoding Edge Cases

### EC-LOC-001: Ambiguous Location Name

**Trigger:** User enters a name that matches multiple locations (e.g., "Ram Mandir" matches 100+ temples)

**Detection:** Geocoding API returns multiple results with low confidence differentiation

**Required Behavior:**
1. Display disambiguation dialog listing top 5 matches with city, state context
2. Show a small map preview for each option
3. Require explicit user selection before proceeding
4. Never silently pick one match and proceed

**Example:**
- "Hanuman Mandir" → Disambiguation: "Hanuman Mandir, Connaught Place, Delhi" | "Hanuman Mandir, Nashik" | "Hanuman Mandir, Ahmedabad" ...

---

### EC-LOC-002: Origin Same as Destination

**Trigger:** User enters the same city or exact location for origin and destination

**Detection:** Geocoordinates within 500m of each other

**Required Behavior:**
- Show error: "Your start and end point are the same location. Please enter a different destination."
- Do not attempt route planning

---

### EC-LOC-003: International Location Entered

**Trigger:** User enters a location outside India (e.g., "Dubai", "Nepal")

**Detection:** Google Maps returns country code other than "IN"

**Required Behavior (v1.0):**
- Message: "TravelMate AI currently supports journeys within India only. International travel planning is coming soon."
- Do not attempt route planning
- Store the query for product analytics (international demand signal)

---

### EC-LOC-004: GPS Location Unavailable

**Trigger:** User taps "Use Current Location" but GPS permission is denied or unavailable

**Detection:** navigator.geolocation returns PermissionDeniedError or PositionUnavailableError

**Required Behavior:**
1. Show a user-friendly message: "Location access is required to use your current location. Please enable location permissions in your browser settings."
2. Show a link to help article: "How to enable location permissions"
3. Fall back to manual input with the "From" field focused

---

### EC-LOC-005: Very Remote Location

**Trigger:** User enters a location in a very remote area with no nearby transport infrastructure

**Detection:** No public transport stops within 50km; no roads in Mapbox/Google Maps

**Required Behavior:**
1. Inform user: "This location is very remote. Transport options may be limited."
2. Plan the best available route to the nearest accessible point
3. Provide a note: "From [nearest accessible point], you may need to hire a private vehicle."
4. Show LOW confidence for the final leg

---

## 2. Transport Data Edge Cases

### EC-TR-001: No Direct Train

**Trigger:** No train runs directly between origin and destination stations

**Detection:** RailwayAPI returns empty results for the station pair

**Required Behavior:**
1. Check for trains via nearest junction cities (e.g., Navsari → Nashik via Surat or Mumbai)
2. If found: present the multi-leg train route
3. If still not found: suggest bus alternatives
4. Never display "No results found" without an alternative

---

### EC-TR-002: Train Running Status Unavailable

**Trigger:** NTES/RailwayAPI does not return real-time running status for a train

**Detection:** API returns null or 404 for running status

**Required Behavior:**
- Do not show "On Time" (this would be false information)
- Show field as "Status: Not available. Check NTES app or 139."
- Display NTES deep link

---

### EC-TR-003: Train Cancelled

**Trigger:** Selected train is cancelled on the requested date

**Detection:** RailwayAPI returns cancellation status

**Required Behavior:**
1. Prominently alert user: "Train [number] [name] is CANCELLED on [date]."
2. Immediately suggest next available train on same route
3. Suggest bus alternative
4. Remove cancelled train from itinerary automatically

---

### EC-TR-004: Train Fully Booked (No Seats)

**Trigger:** All classes on the requested train show "No availability"

**Detection:** Seat availability API returns null/0 for all classes

**Required Behavior:**
1. Alert user: "Train [number] appears to have no available seats in any class."
2. Suggest: "Check IRCTC Tatkal quota (opens 24h before departure)."
3. Show next 3 trains on same route with availability
4. Note: TravelMate AI does not book tickets; user is directed to IRCTC

---

### EC-BU-001: Bus Route Not in GTFS

**Trigger:** Bus needed for a leg has no GTFS data for the state

**Detection:** GTFS query returns empty; Google Transit also returns no result

**Required Behavior:**
1. Search state transport website (if scraped data available)
2. If still unavailable:
   - Show route guidance: "Take a bus from [origin stop] towards [destination city]. Buses typically depart every [X] minutes. Fare: approximately ₹[estimate]."
   - Label with LOW confidence
   - Add note: "We recommend confirming the bus schedule locally."
3. Never invent a bus number

---

### EC-FL-001: No Flights Available

**Trigger:** No commercial flights operate between origin and destination city pair

**Detection:** Amadeus API returns no results

**Required Behavior:**
1. Do not show a flight leg
2. Plan via ground transport (train + bus)
3. If distance > 1000km and no direct ground route is feasible, show note: "Consider flying to [nearest airport] and connecting via road."

---

## 3. Temple and Destination Edge Cases

### EC-TM-001: Temple Closed on Travel Date

**Trigger:** The destination temple is closed on the user's planned travel date (annual closure, maintenance, full moon restrictions)

**Detection:** Temple database closure_dates array contains the requested date

**Required Behavior:**
1. Prominently alert: "⚠️ [Temple Name] is CLOSED on [date]. Reason: [Annual closure / Maintenance]."
2. Show nearest open date
3. Offer to replan for the next open date
4. Do not hide this warning

---

### EC-TM-002: Destination Ambiguous Between Temple and City

**Trigger:** User types "Trimbakeshwar" which is both a city and a temple

**Detection:** Multiple entity types returned (city, religious site)

**Required Behavior:**
1. Ask: "Are you traveling to Trimbakeshwar City or Trimbakeshwar Temple?"
2. Show both options clearly with map icons
3. Temple selection triggers temple data display; city selection plans route to city center

---

### EC-TM-003: Temple During Festival (High Crowd)

**Trigger:** User's travel date coincides with a major festival (Maha Shivaratri for Trimbakeshwar, Navratri, Diwali, etc.)

**Detection:** Festival calendar database matches travel date with temple's significant festivals

**Required Behavior:**
1. Warning: "🎉 Your visit coincides with [Festival Name]. Crowds will be significantly higher than normal."
2. Show estimated crowd level: Low / Moderate / High / Very High
3. Suggest: arriving early morning for darshan
4. Show extended hotel options (more may be needed)
5. Warn of potential train/bus overcrowding

---

## 4. User Input Edge Cases

### EC-UI-001: Date in the Past

**Trigger:** User selects a travel date before today

**Detection:** Selected date < current date

**Required Behavior:**
- Prevent selection in date picker (past dates grayed out)
- If manually entered: "The selected date has already passed. Please choose a future date."

---

### EC-UI-002: Departure Time After Last Transport

**Trigger:** User selects a departure time after which no transport is available (e.g., 11 PM, but last bus/train is at 9 PM)

**Detection:** Route planning returns no valid routes for the departure time window

**Required Behavior:**
1. Alert: "No transport available after [time] for this route."
2. Show last available departure time
3. Show first morning departure as alternative
4. Option: Plan for next day

---

### EC-UI-003: Special Characters in Input

**Trigger:** User enters special characters in location fields (script injection attempt or accidental)

**Detection:** Input contains `<`, `>`, `"`, `'`, `\`, or SQL injection patterns

**Required Behavior:**
- Frontend sanitizes input before submission
- Backend validates and rejects if injection patterns detected
- Show error: "Please enter a valid location name."
- Log the attempt (security audit log)

---

## 5. API and System Edge Cases

### EC-API-001: Google Maps API Rate Limit Hit

**Trigger:** Monthly Google Maps API quota exceeded or per-second rate limit hit

**Detection:** Google Maps API returns 429 or OVER_QUERY_LIMIT

**Required Behavior:**
1. Immediately switch to Mapbox Geocoding API for geocoding
2. Use cached results if available
3. If both fail: inform user "Location services are temporarily unavailable. Please try again in a few minutes."
4. Alert engineering via PagerDuty
5. Do not charge the user's free trip quota for failed plans

---

### EC-API-002: AI LLM API Failure

**Trigger:** Gemini API returns 500, times out, or returns malformed response

**Detection:** HTTP 5xx or timeout > 30 seconds

**Required Behavior:**
1. Retry with exponential backoff: 1s, 3s, 9s (max 3 retries)
2. If all retries fail: show degraded itinerary using rule-based fallback (cached routes, non-AI logic)
3. Message to user: "AI planning is temporarily unavailable. We've planned your route using our schedule database."
4. Alert engineering
5. Log incident for debugging

---

### EC-API-003: Weather API Failure

**Trigger:** OpenWeatherMap API unavailable

**Detection:** HTTP 5xx or timeout

**Required Behavior:**
1. Retry once after 2 seconds
2. If failed: hide weather widget; show message "Weather data temporarily unavailable."
3. Do not block itinerary generation — weather is supplementary

---

### EC-API-004: Database Connection Failure

**Trigger:** PostgreSQL primary is unreachable

**Detection:** SQLAlchemy raises OperationalError on connection

**Required Behavior:**
1. Attempt connection to read replica immediately
2. For read operations: serve from replica
3. For write operations: queue in Redis; retry when primary recovers
4. Alert on-call engineer via PagerDuty
5. Show user: "We're experiencing a minor technical issue. Your trip planning is not affected." (if reads available)

---

## 6. Payment Edge Cases

### EC-PAY-001: Payment Declined

**Trigger:** Stripe returns a declined payment

**Detection:** Stripe PaymentIntent status = `payment_failed`

**Required Behavior:**
1. Show specific error reason (if available from Stripe): "Your card was declined. Please try a different payment method."
2. Allow retry with new card
3. Do not downgrade existing plan immediately
4. Log event (Stripe webhook)

---

### EC-PAY-002: Subscription Expired, User Still Using App

**Trigger:** User's subscription has lapsed (non-payment) but they attempt to use a paid feature

**Detection:** Clerk session + Stripe subscription status = `past_due` or `canceled`

**Required Behavior:**
1. Allow current session to complete active trip plan
2. On next feature access: soft wall — "Your subscription has expired. Renew to continue using [feature]."
3. Do not immediately lock user out mid-planning

---

## 7. Offline Edge Cases

### EC-OFF-001: Itinerary Stale After Download

**Trigger:** User downloaded itinerary 2 days ago; train schedule has changed

**Detection:** User opens app online; downloaded itinerary timestamp > 24 hours

**Required Behavior:**
1. Show banner: "Your saved itinerary may have outdated information. Refresh to get the latest schedules?"
2. Allow user to refresh or keep current version
3. If train cancelled since download: show alert prominently

---

### EC-OFF-002: Device Storage Full

**Trigger:** User attempts to download PDF or cache data but device storage is full

**Detection:** Browser storage quota exceeded error

**Required Behavior:**
1. Show message: "Not enough storage to save offline. Please free up space on your device."
2. Offer to generate the PDF for viewing without saving
3. Do not silently fail

---

## 8. Group Travel Edge Cases

### EC-GRP-001: Wheelchair User in Group

**Trigger:** User marks "Wheelchair/mobility impaired" in group settings

**Detection:** `accessibility_needs.wheelchair = true` in trip parameters

**Required Behavior:**
1. Filter out non-wheelchair-accessible transit options
2. Prioritize trains with accessible coaches (PH quota)
3. Show wheelchair accessibility status for each hotel
4. Add note to walking legs: "[Xm walk — wheelchair accessible path]" or "[May require assistance on stairs at station Y]"

---

### EC-GRP-002: Large Group (>10 People)

**Trigger:** Group size > 10 people

**Detection:** adults + children + seniors > 10

**Required Behavior:**
1. Note: "For groups of 10+, consider a group train booking via IRCTC (special quota available)."
2. Suggest private bus/mini-van for local legs
3. Note that individual train seat availability shown may not reflect group booking availability
4. Recommend contacting a travel agent for group IRCTC booking

---

## Edge Case Response Matrix

| Category | Count | Primary Action | Fallback |
|---|---|---|---|
| Location ambiguity | 5 | Disambiguation dialog | Manual input |
| Transport unavailability | 6 | Alternative route | Degraded guidance with LOW confidence |
| Temple/destination | 3 | Warning + alternatives | External link |
| API failures | 4 | Retry + graceful degrade | Cached data / rule-based fallback |
| User input errors | 3 | Client-side validation | Backend validation |
| Payment | 2 | Retry / grace period | Support contact |
| Offline | 2 | Storage management | PDF fallback |
| Group travel | 2 | Accessibility filter | Advisory note |
