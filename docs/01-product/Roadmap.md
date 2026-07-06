# Roadmap.md

# TravelMate AI — Product Roadmap

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Horizon:** 18 months

---

## Roadmap Philosophy

The roadmap is organized into three time horizons:
- **Now (0–3 months):** Core product. Highest confidence and detail.
- **Next (3–9 months):** Planned enhancements. Some flexibility.
- **Later (9–18 months):** Strategic direction. Subject to learnings.

---

## Phase 1: Foundation (Months 1–3) — MVP Launch

**Theme:** "Make it work, make it real, make it trustworthy."

### Sprint 1–2: Infrastructure Setup
- Next.js 16 + FastAPI project scaffolding
- PostgreSQL + Redis setup (Docker)
- Clerk authentication integration
- Stripe subscription integration (Free, Explorer, Pro tiers)
- CI/CD pipeline (GitHub Actions → Vercel + Railway)
- Environment variable management

### Sprint 3–4: Data Layer
- Google Maps API integration (Geocoding, Places, Distance Matrix)
- RailwayAPI.in integration for train schedules
- GTFS feed parser for GSRTC, MSRTC bus data
- OpenWeatherMap integration
- Temple database (curated initial dataset: 500 temples)

### Sprint 5–6: AI Agent System
- LangGraph orchestrator implementation
- RouteAgent (multi-modal synthesis)
- TrainAgent (schedule lookup, availability)
- BusAgent (GTFS + Google Transit fallback)
- WeatherAgent
- TempleAgent
- BudgetAgent
- Confidence scoring system

### Sprint 7–8: Core UI
- Landing page
- Trip planner screen (origin/destination input)
- Itinerary timeline view
- Map view (Mapbox)
- Budget breakdown panel
- Contextual cards (weather, temple, hotel)

### Sprint 9–10: Polish + Launch Prep
- AI chat interface
- Offline PDF export
- Notification system (email + push)
- Error handling and fallback states
- Performance optimization (< 8s P95)
- Security audit
- Soft launch (invite-only beta)

**Milestone:** Public v1.0 launch  
**Target:** Month 3

---

## Phase 2: Growth (Months 4–6)

**Theme:** "Make it better, make it stickier."

### Features
| Feature | Priority | Impact |
|---|---|---|
| Flight leg planning (Amadeus API) | P1 | High — enables long-distance trips |
| Metro GTFS integration (Delhi, Mumbai, Bengaluru) | P1 | High — urban planning completeness |
| Return trip planning | P1 | High — core user request |
| Multi-city planning (up to 5 stops) | P1 | High — enables complex trips |
| Voice input (English + Hindi) | P1 | High — accessibility |
| Alternative route options (3 options) | P1 | High — user choice |
| Senior citizen mode (large text, simplified UI) | P1 | High — pilgrimage segment |
| Group travel size input | P2 | Medium |
| Itinerary sharing (link) | P2 | Medium |
| Train delay real-time alerts | P2 | Medium |

**Milestone:** v1.5 Release  
**Target:** Month 6

---

## Phase 3: Monetization (Months 7–9)

**Theme:** "Make it pay."

### Features
| Feature | Priority | Impact |
|---|---|---|
| Business tier launch | P1 | Revenue — corporate market |
| B2B API (white-label planning API) | P1 | Revenue — travel agents |
| Expense report export (CSV/PDF) | P1 | Business tier value |
| Calendar integration (Google Calendar) | P2 | Engagement — business users |
| Affiliate hotel deep links | P1 | Revenue — commissions |
| Temple rating and reviews | P2 | Engagement |
| Community trip sharing | P2 | Viral growth |
| Admin dashboard | P1 | Operations |

**Milestone:** v2.0 Revenue Milestone  
**Target:** Month 9

---

## Phase 4: Scale (Months 10–18)

**Theme:** "Make it India's travel OS."

### Features
| Feature | Priority |
|---|---|
| Hindi + Gujarati + Marathi + Tamil UI | P1 |
| Voice assistant (regional languages) | P1 |
| Real-time vehicle tracking (bus GPS feeds) | P2 |
| International travel (South Asia) | P2 |
| AI-generated travel guide (destination pages) | P2 |
| Social features (travel companions, groups) | P3 |
| Native mobile apps (iOS + Android — React Native) | P1 |
| Aadhaar-linked senior citizen discounts | P3 |
| Live train PNR tracking integration | P1 |
| Festival crowd prediction model (ML) | P2 |
| Hotel booking integration (direct booking API) | P1 |

**Milestone:** v3.0 — India's Travel OS  
**Target:** Month 18

---

## Roadmap Timeline Summary

```
Month  1-2   │ Infrastructure, APIs, AI agents
Month  3     │ MVP Launch (v1.0)
Month  4-5   │ Growth features, Flight + Metro integration
Month  6     │ v1.5 Release
Month  7-8   │ Business tier, B2B API, Monetization features
Month  9     │ v2.0 Revenue Milestone
Month 10-11  │ Localization, Native apps
Month 12     │ Regional language launch
Month 13-15  │ Social features, Hotel booking
Month 16-18  │ v3.0 — Full Travel OS
```

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| IRCTC API access denied | High | High | Deep-link redirect fallback; not dependent on IRCTC API for v1.0 |
| Transport data quality poor | Medium | High | Multi-source fallback + confidence scoring |
| AI costs exceed budget | Medium | Medium | Token optimization, caching, response streaming |
| Competition launches similar product | Medium | High | Speed to market; niche focus on pilgrimage |
| Stripe India regulatory change | Low | High | Monitor RBI guidelines; maintain Razorpay as fallback |
