# PRD.md

# TravelMate AI — Product Requirements Document (PRD)

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Status:** Approved  
**Owner:** Product Team  
**Classification:** Internal — Engineering Reference

---

## 1. Executive Summary

TravelMate AI is a production-grade, AI-powered Multi-Agent Travel Operating System (MATOS) designed to plan complete, door-to-door, multi-modal journeys anywhere in India. Unlike conventional travel apps that surface train or flight options in isolation, TravelMate AI reasons across all available transport modes — walking, auto, cab, metro, bus, train, flight — and produces a single coherent itinerary from the user's doorstep to their final destination.

**Tagline:** "From your doorstep to your destination."

The core value proposition is eliminating the cognitive load of travel planning. The user provides only an origin and destination (e.g., "Navsari → Trimbakeshwar Temple"), and the system autonomously:

1. Determines the user's precise starting point (home address, current GPS location, or custom).
2. Plans the first-mile connection (walking, auto, cab to nearest transit hub).
3. Selects inter-city transport (train, bus, flight) based on cost, time, and availability.
4. Plans the last-mile connection from the arrival point to the destination.
5. Layers in contextual data: weather, temple timings, hotel options, food suggestions, budget estimates, and crowd predictions.
6. Presents the full itinerary with real-time data, downloadable for offline access.

---

## 2. Problem Statement

### 2.1 The Fragmented Travel Planning Reality

Indian travelers currently must coordinate across 5–10 different apps and websites to plan a single trip:

- **IRCTC** for train tickets
- **MakeMyTrip / Goibibo** for flights and hotels
- **RedBus** for buses
- **Ola / Uber** for cabs
- **Google Maps** for local navigation
- **Zomato / Swiggy** for food
- **TripAdvisor / Google** for tourist information
- **Weather apps** for conditions
- **Temple / attraction websites** for timings

This fragmentation causes:
- **Decision fatigue:** Users spend 2–5 hours planning a single trip.
- **Coordination errors:** Missed connections due to poor time buffer estimation.
- **Financial overruns:** Failure to budget all transport legs.
- **Missed opportunities:** Unaware of better routes, hidden gems, or deals.
- **Accessibility barriers:** Senior citizens and non-tech-savvy users cannot navigate multiple apps.

### 2.2 The AI Opportunity

Generative AI with tool-calling capability can act as a reasoning orchestrator — not just a chatbot — that calls real transport APIs, weather APIs, hotel APIs, and mapping services simultaneously, then synthesizes a coherent, real-data-backed itinerary. This is the core technical differentiation of TravelMate AI.

---

## 3. Product Vision

> **Vision Statement:** To become India's most trusted AI travel companion — the single interface that any Indian, regardless of technical literacy, uses to plan every journey from a pilgrimage in Maharashtra to a business trip to Bangalore.

### 3.1 Mission

Eliminate the complexity of multi-modal travel planning through intelligent automation, while maintaining absolute data integrity and transparency about confidence levels.

### 3.2 Core Principles

| Principle | Description |
|---|---|
| **Accuracy over Hallucination** | Never invent transport data. Always cite source, timestamp, and confidence score. |
| **Completeness** | Every leg of the journey — including walking 200m to a bus stop — must be in the itinerary. |
| **Inclusivity** | Works for senior citizens, foreign tourists, and users with disabilities. |
| **Transparency** | Show confidence scores on every data point. Users must know when data is estimated. |
| **Offline First** | Core itinerary must be downloadable and usable without internet. |
| **Privacy** | Location data is never sold. User data is encrypted at rest and in transit. |

---

## 4. Product Scope

### 4.1 In Scope (v1.0)

| Feature Area | Features |
|---|---|
| **Trip Planning** | Door-to-door multi-modal itinerary, origin/destination input, date/time selection |
| **Transport Modes** | Train, flight, bus, metro, cab, auto, walking, bike, shared taxi |
| **Contextual Data** | Weather, temple timings, tourist places, hotel options, food suggestions |
| **Budgeting** | Per-leg cost estimation, total trip budget, currency formatting |
| **AI Chat** | Natural language trip modification, Q&A about itinerary |
| **Offline Mode** | Downloadable itinerary PDF and local data cache |
| **User Accounts** | Saved trips, trip history, preferences, profile |
| **Notifications** | Departure reminders, train delay alerts, weather warnings |
| **Emergency** | Quick access to emergency contacts, nearest police, hospital |
| **Maps** | Embedded multi-modal map view for entire journey |

### 4.2 Out of Scope (v1.0 — Planned for v2.0+)

| Feature | Rationale |
|---|---|
| **In-app ticket booking** | Requires IRCTC/Airline API partnerships (regulatory complexity) |
| **Live GPS tracking of vehicles** | Requires real-time vehicle telemetry agreements |
| **International travel** | Focus on India-first for v1.0 |
| **Payment processing for hotels** | Hotel aggregator API partnerships required |
| **Social travel (group coordination)** | Planned for v1.5 |

---

## 5. User Segments

### 5.1 Primary Segments

| Segment | Description | Key Need |
|---|---|---|
| **Pilgrimage Travelers** | Hindu, Jain, Buddhist devotees visiting temples, dargahs, gurudwaras | Temple timings, crowd levels, nearby dharamshalas, spiritual routes |
| **Solo Travelers** | 18–35, tech-savvy, exploring India | Best-value routes, hidden gems, safety features |
| **Families** | Parents with children, multi-generational trips | Comfort, seat availability, kid-friendly stops |
| **Senior Citizens** | 60+, may have mobility constraints | Simplified UI, accessibility features, wheelchair-friendly routes |
| **Business Travelers** | Professionals, frequent travelers | Speed, premium options, expense tracking |

### 5.2 Secondary Segments

| Segment | Description |
|---|---|
| **Foreign Tourists** | Non-Indian visitors, English/multilingual support needed |
| **Students** | Budget-conscious, backpacker routes |
| **Road Trip Users** | Planning long-distance road journeys with stops |

---

## 6. Core User Journey

### 6.1 Primary Flow: "Plan a Trip"

```
Step 1: User opens TravelMate AI
Step 2: User enters "Navsari" → "Trimbakeshwar Temple"
Step 3: User selects travel date and preferred time
Step 4: AI Orchestrator activates:
         ├── GeolocationAgent: Resolves "Navsari" to coordinates
         ├── RouteAgent: Queries train, bus, cab APIs
         ├── WeatherAgent: Fetches forecast for travel dates
         ├── TempleAgent: Fetches Trimbakeshwar timings, puja schedule
         ├── HotelAgent: Fetches accommodation near Nashik/Trimbak
         └── BudgetAgent: Computes total cost estimates
Step 5: System synthesizes multi-modal itinerary:
         Home (Navsari) → Auto to Navsari Railway Station → 
         Train (Navsari → Nashik Road) → Bus (Nashik Road → Trimbak) → 
         Walking (Trimbak Bus Stand → Trimbakeshwar Temple)
Step 6: Itinerary displayed with:
         - Timeline view (leg-by-leg)
         - Map view (full route visualization)
         - Budget breakdown
         - Temple timings overlay
         - Weather warnings
         - Hotel options near destination
Step 7: User reviews, modifies via AI chat if needed
Step 8: User saves or downloads itinerary
Step 9: Day-of notifications activated
```

---

## 7. Feature Requirements

### 7.1 Trip Planning Engine

**P0 (Must Have for Launch)**

| ID | Feature | Description |
|---|---|---|
| TP-001 | Origin resolution | Convert text origin to geocoordinates with fuzzy matching |
| TP-002 | Destination resolution | Convert text destination to geocoordinates with landmark support |
| TP-003 | Multi-modal route synthesis | Combine 2–6 transport modes into one seamless itinerary |
| TP-004 | Train leg planning | Query train schedules via RailwayAPI/IRCTC API |
| TP-005 | Bus leg planning | Query bus routes via GSRTC, MSRTC, and GTFS feeds |
| TP-006 | Cab/Auto estimation | Compute first/last mile cab routes via Google Maps Distance Matrix |
| TP-007 | Walking legs | Compute walking segments with distance and time |
| TP-008 | Transfer time buffers | Insert realistic transfer buffers between transport legs |
| TP-009 | Departure time awareness | Schedule itinerary around user-specified departure time |
| TP-010 | Confidence scoring | Every data point must carry source and confidence score (0–1) |

**P1 (Must Have within 60 days)**

| ID | Feature | Description |
|---|---|---|
| TP-011 | Flight leg planning | Query flights via Amadeus or Skyscanner API |
| TP-012 | Metro leg planning | GTFS-based metro route planning |
| TP-013 | Return trip planning | Reverse itinerary for return journey |
| TP-014 | Multi-city planning | Plan A → B → C → D with intermediate stops |
| TP-015 | Alternatives | 3 alternative itineraries (fastest, cheapest, most comfortable) |

### 7.2 Contextual Intelligence

| ID | Feature | Description |
|---|---|---|
| CI-001 | Weather integration | 7-day forecast for origin, transit points, destination |
| CI-002 | Temple timings | Puja timings, darshan queues, special events |
| CI-003 | Crowd prediction | Estimated crowd levels at destination (festival calendar awareness) |
| CI-004 | Hotel suggestions | 3–5 hotel options with price range and distance from destination |
| CI-005 | Food suggestions | Local food recommendations near stops |
| CI-006 | Tourist highlights | Notable places en route or near destination |

### 7.3 AI Chat Interface

| ID | Feature | Description |
|---|---|---|
| AC-001 | Natural language Q&A | "What time does the train arrive at Nashik?" |
| AC-002 | Itinerary modification | "Change departure to 6 AM" — replans relevant legs |
| AC-003 | Preference application | "I prefer window seats" — stores in user profile |
| AC-004 | Clarification handling | Asks for clarification when destination is ambiguous |
| AC-005 | Voice input | Speech-to-text input for all queries |

### 7.4 Offline Mode

| ID | Feature | Description |
|---|---|---|
| OF-001 | PDF export | Full itinerary as formatted PDF |
| OF-002 | Data caching | Cache itinerary data in browser localStorage/IndexedDB |
| OF-003 | Map tile caching | Cache map tiles for offline viewing |
| OF-004 | Emergency contacts offline | Emergency numbers always accessible |

---

## 8. Non-Functional Requirements (Summary)

| Category | Requirement |
|---|---|
| **Performance** | Itinerary generation < 8 seconds (P95) |
| **Availability** | 99.9% uptime SLA |
| **Scalability** | Support 100,000 concurrent users |
| **Security** | OWASP Top 10 compliance, SOC 2 roadmap |
| **Accessibility** | WCAG 2.1 AA compliance |
| **Localization** | English, Hindi (v1.0); Gujarati, Marathi, Tamil (v2.0) |
| **Mobile** | Progressive Web App (PWA) with native-like experience |

---

## 9. Success Metrics

| Metric | Target (3 months) | Target (12 months) |
|---|---|---|
| Monthly Active Users (MAU) | 10,000 | 200,000 |
| Trip Plans Generated | 50,000 | 2,000,000 |
| P95 Itinerary Generation Time | < 8 seconds | < 5 seconds |
| User Satisfaction (CSAT) | ≥ 4.2 / 5.0 | ≥ 4.5 / 5.0 |
| Return User Rate | 30% | 55% |
| Conversion (Free → Premium) | 5% | 12% |
| Offline Itinerary Downloads | 20% of plans | 40% of plans |

---

## 10. Monetization Model

### 10.1 Freemium Tiers

| Tier | Price | Features |
|---|---|---|
| **Free** | ₹0/month | 3 trip plans/month, standard routes, ads |
| **Explorer** | ₹99/month | 20 trip plans/month, no ads, PDF export |
| **Pro** | ₹249/month | Unlimited plans, priority AI, multi-city, voice assistant |
| **Business** | ₹999/month | Team accounts, expense reports, priority support |

### 10.2 Revenue Streams

| Stream | Description |
|---|---|
| **Subscriptions** | Primary revenue — monthly/annual plans via Stripe |
| **Hotel Referral Commissions** | Affiliate links to booking platforms |
| **Transport Affiliate** | Deep links to IRCTC, RedBus, MakeMyTrip |
| **B2B API** | Travel agencies integrating TravelMate AI planning API |

---

## 11. Constraints and Assumptions

### 11.1 Constraints

- IRCTC does not have a public booking API; train seat booking is handled via deep link redirect.
- Real-time bus GPS is unavailable in most Indian cities; GTFS scheduled data is the fallback.
- Temple timings must be manually curated for the initial dataset and refreshed periodically.
- Airline PNR booking requires IATA accreditation; v1.0 redirects to airline websites.

### 11.2 Assumptions

- Users have a mobile device with modern browser (Chrome 90+, Safari 14+).
- Internet connectivity is available for trip planning; offline mode activates post-plan.
- Google Maps Platform and Mapbox APIs remain available and within budget.
- LangGraph-based agent orchestration can complete within an 8-second response budget.

---

## 12. Dependencies

| Dependency | Type | Criticality |
|---|---|---|
| Google Maps Platform (Geocoding, Distance Matrix, Places) | External API | Critical |
| RailwayAPI.in or RapidAPI Indian Railways | External API | Critical |
| OpenWeatherMap or IMD API | External API | High |
| GTFS feeds (GSRTC, MSRTC, BMTC) | Data feed | High |
| Clerk Authentication | External Service | Critical |
| Stripe | External Service | High |
| Cloudinary | External Service | Medium |
| Google Gemini 3.5 Flash | AI Provider | Critical |

---

## 13. Approval and Signoff

| Role | Name | Date | Status |
|---|---|---|---|
| Product Owner | — | 2026-07-03 | Approved |
| Engineering Lead | — | 2026-07-03 | Approved |
| Design Lead | — | 2026-07-03 | Approved |
| QA Lead | — | 2026-07-03 | Approved |
