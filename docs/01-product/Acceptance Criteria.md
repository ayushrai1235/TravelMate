# Acceptance Criteria.md

# TravelMate AI — Acceptance Criteria

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Purpose:** Defines the precise, testable conditions under which each feature is considered complete and ready for production.

---

## AC-TP-001: Trip Input and Origin Resolution

**Feature:** User enters trip origin in free text

**Given** a user is on the Trip Planner screen,  
**When** they type an origin into the "From" field,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | User types a valid Indian city name (e.g., "Navsari") | Geocoordinates resolved, city name confirmed in field |
| 2 | User types a landmark (e.g., "Chhatrapati Shivaji Terminus") | Resolved to station coordinates with "Station" label |
| 3 | User types a partial name with typo (e.g., "Nasik") | Fuzzy match suggests "Nashik, Maharashtra" with user confirmation |
| 4 | User types an ambiguous name (e.g., "Ram Mandir") | Disambiguation dialog shows top 5 matches with city context |
| 5 | User types an unrecognized string | Error message: "We couldn't find this location. Please try a city or landmark name." |
| 6 | User taps "Use Current Location" | GPS coordinates used, reverse-geocoded address shown |
| 7 | GPS permission denied | Graceful fallback to manual input with message explaining why |

---

## AC-TP-002: Itinerary Generation

**Feature:** System generates a multi-modal itinerary

**Given** valid origin, destination, date, and time are entered,  
**When** user taps "Plan My Trip",  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | Route requires train + bus | Both legs shown with exact transfer point |
| 2 | Route requires train only | Single leg shown with auto suggestion for first/last mile |
| 3 | Distance is < 5km | Walking or auto-only route suggested |
| 4 | No train connection exists on date | Bus or flight alternative shown with explanation |
| 5 | P95 response time | < 8 seconds from submission to itinerary display |
| 6 | API failure during generation | Partial itinerary shown with degraded legs marked; user notified |
| 7 | Complete API failure | Error screen with "Try again" and offline fallback explanation |
| 8 | Itinerary has > 2 transfers | Transfer summary shown at top; each transfer has time buffer labeled |

---

## AC-TP-003: Confidence Scoring Display

**Feature:** Every data point shows confidence level

**Given** an itinerary is displayed,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | Train schedule from official API | Confidence: HIGH, source: "Indian Railways / RailwayAPI" |
| 2 | Bus schedule from GTFS feed | Confidence: MEDIUM, source: "GTFS / GSRTC (scheduled)" |
| 3 | Bus route from fallback reasoning | Confidence: LOW, source: "AI-estimated route — verify locally" |
| 4 | Cab fare estimate | Confidence: MEDIUM, source: "Google Maps Distance Matrix estimate" |
| 5 | Walking time | Confidence: HIGH, source: "Google Maps walking directions" |
| 6 | Temple timings from curated DB | Confidence: HIGH, source: "TravelMate temple database (updated: DATE)" |
| 7 | Crowd prediction | Confidence: MEDIUM, source: "Historical data + festival calendar" |

**Visual representation:**
- HIGH confidence: green indicator
- MEDIUM confidence: amber indicator  
- LOW confidence: red indicator with warning icon

---

## AC-TP-004: Train Data Accuracy

**Feature:** Train schedules and availability

**Given** a train leg is planned,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | Train runs on selected date | Schedule shown: train number, name, departure time, arrival time, class availability |
| 2 | Train does not run on selected date (e.g., weekly train, not on Tuesday) | Warning shown: "Train [number] does not run on [date]. Next available: [date]" |
| 3 | Train data unavailable | Fallback message: "Schedule data unavailable for this route. Check NTES app or IRCTC." |
| 4 | Multiple trains available | Top 3 trains shown sorted by departure time |
| 5 | Real-time delay data available | Current running status shown with delay in minutes |
| 6 | Real-time delay unavailable | Field hidden; not shown as "On Time" |

---

## AC-TP-005: Bus Data Accuracy

**Feature:** Bus route planning

**Given** a bus leg is required in the itinerary,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | GTFS feed has route data | Bus route number, origin stop, destination stop, frequency shown |
| 2 | GTFS data not available for state | System queries Google Transit; result shown with Google Transit attribution |
| 3 | Google Transit unavailable | System provides route guidance: "Board a bus towards [direction] from [stop name]. Distance: Xkm." with LOW confidence label |
| 4 | Bus stop GPS data available | Walking directions to nearest bus stop shown |
| 5 | Bus stop GPS unavailable | Bus stop name shown with note: "Ask locals for directions to [stop name]" |

---

## AC-CI-001: Temple Information Accuracy

**Feature:** Temple timings and schedule display

**Given** destination is a recognized temple,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | Temple in curated database | Opening time, closing time, puja schedule, prasad schedule shown |
| 2 | Festival date detected | Special schedule shown with festival name and date |
| 3 | Temple closed on selected date | Alert: "Temple is closed on [date]. Nearest open date: [date]" |
| 4 | Temple not in database | Note: "Temple information not available. Please verify timings with the temple directly." External Google link provided. |
| 5 | Data > 30 days old | Timestamp shown with note: "Please verify current timings before visiting" |

---

## AC-UI-001: Loading States

**Feature:** Loading and skeleton states during data fetch

**Given** the user has submitted a trip request,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | < 2 seconds | Loading spinner with "Planning your journey..." |
| 2 | 2–5 seconds | Skeleton loader shows itinerary structure filling in progressively |
| 3 | 5–8 seconds | Progress message updates: "Checking train schedules... Fetching bus routes... Checking weather..." |
| 4 | > 8 seconds | Partial results shown if available; spinner on pending sections |
| 5 | > 15 seconds with no response | Timeout error: "This is taking longer than expected. Try again or check your connection." |

---

## AC-UI-002: Responsive Design

**Feature:** Application renders correctly on all device sizes

**Given** a user opens TravelMate AI on any device,  
**Then:**

| # | Device | Expected Layout |
|---|---|---|
| 1 | Mobile (< 768px) | Single column, full-width cards, sticky bottom navigation |
| 2 | Tablet (768px–1024px) | Two-column itinerary + mini-map layout |
| 3 | Desktop (> 1024px) | Three-column: sidebar + main content + map panel |
| 4 | Large desktop (> 1440px) | Same as desktop, max-width 1440px centered |

---

## AC-SEC-001: Authentication

**Feature:** User authentication via Supabase

**Given** a user attempts to access protected features,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | Unauthenticated user plans a trip | Trip planning works (no auth required for 3 free trips) |
| 2 | Unauthenticated user hits free trip limit | Prompted to sign up to continue |
| 3 | User signs in with Google | Supabase OAuth flow; redirected back to app with session |
| 4 | User signs in with email | OTP sent to email; session created after verification |
| 5 | Session expires | User redirected to login; unsaved trip is preserved in session storage |
| 6 | JWT token invalid | 401 returned; frontend redirects to login |

---

## AC-PERF-001: Performance Benchmarks

**Feature:** Application performance

| # | Metric | Target | Measurement Method |
|---|---|---|---|
| 1 | Itinerary P95 response time | < 8 seconds | Backend timing logs |
| 2 | First Contentful Paint (FCP) | < 1.5 seconds | Lighthouse |
| 3 | Largest Contentful Paint (LCP) | < 2.5 seconds | Lighthouse |
| 4 | Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| 5 | Time to Interactive (TTI) | < 3 seconds | Lighthouse |
| 6 | API endpoint P99 response | < 500ms (non-AI) | Datadog APM |

---

## AC-OFF-001: Offline Functionality

**Feature:** Offline itinerary access

**Given** a user has downloaded an itinerary,  
**When** they go offline,  
**Then:**

| # | Condition | Expected Result |
|---|---|---|
| 1 | User opens downloaded PDF | PDF renders without network |
| 2 | User opens app in offline mode | Saved itineraries load from IndexedDB |
| 3 | User tries to plan a new trip offline | Error: "Trip planning requires internet. Your saved trips are available below." |
| 4 | Emergency screen offline | Emergency contacts load from cached data |
| 5 | Map view offline | Cached tiles render; note: "Map may be incomplete in offline mode" |

---

## AC-NOTIFY-001: Notifications

**Feature:** Push notifications

| # | Notification Type | Trigger | Content |
|---|---|---|---|
| 1 | 24h reminder | 24 hours before first transport leg | "Your trip to [destination] starts tomorrow! First leg: [transport] at [time] from [place]" |
| 2 | 2h reminder | 2 hours before first transport leg | "Time to get ready! Your [train/bus] departs at [time] from [station]" |
| 3 | 30-min reminder | 30 minutes before departure | "Head out now! [transport] departs in 30 minutes from [platform/stop]" |
| 4 | Delay alert | Train delayed > 15 min (real-time API) | "Your train [number] is running [X] minutes late. New ETA: [time]" |
| 5 | Weather alert | Adverse weather in destination forecast | "Heavy rainfall expected in [destination] on [date]. Consider rain gear." |

---

## Definition of Done (Global)

A feature is considered "Done" when ALL of the following are true:

- [ ] Acceptance Criteria above pass in test environment
- [ ] Unit tests written and passing (≥ 80% coverage for the feature)
- [ ] Integration tests passing
- [ ] No critical or high security vulnerabilities (OWASP scan clean)
- [ ] WCAG 2.1 AA compliance verified for new UI components
- [ ] Performance benchmarks met (Lighthouse score ≥ 85)
- [ ] Code reviewed and approved by senior engineer
- [ ] Documentation updated
- [ ] QA sign-off received
- [ ] Product Owner acceptance received
