# Phase Rollout.md

# TravelMate AI — Implementation Phase Rollout

**Version:** 1.1.0  
**Date:** 2026-07-06

---

## 1. Overview

This document outlines the sequential steps required to build TravelMate AI from zero to production. It breaks the project into distinct, testable phases, ensuring all architectural requirements, security measures, and AI capabilities are systematically implemented.

---

## 2. Phase 1: Foundation & Scaffolding (Week 1)

**Goal:** Get the environments up and running with basic connectivity, database, and authentication.

1. **Repository Setup:**
   - Initialize monorepo structure (`apps/web`, `apps/api`, `packages/shared-types`).
   - Configure ESLint, Prettier, Ruff, and MyPy.
   - Set up GitHub Actions for CI/CD pipelines (Frontend to Vercel, Backend to Railway).

2. **Database & Auth Foundation (Supabase):**
   - Provision Supabase project (PostgreSQL Database + Authentication).
   - Configure Supabase Auth providers (Email/OTP, Google OAuth).
   - Write SQLAlchemy models and initial Alembic migrations for FastAPI to connect to Supabase PostgreSQL.
   - Set up Supabase webhooks to sync user creation to custom backend tables, and apply Row Level Security (RLS) if required.

3. **Frontend Shell:**
   - Initialize Next.js 16 (App Router) with TypeScript.
   - Install TailwindCSS, shadcn/ui, and Framer Motion.
   - Build the `<Navbar>` with Supabase Auth UI / session management.
   - Build an empty `/planner` page (protected route via Next.js middleware using Supabase SSR client).

4. **Backend Shell & Infrastructure:**
   - Initialize FastAPI 0.115 backend on Python 3.12.
   - Provision Redis 7 on Railway (for caching, rate limiting, and session state).
   - Setup AWS S3 for database backup storage and PDF itinerary storage.

---

## 3. Phase 2: Core Data & APIs (Week 2)

**Goal:** Connect to external data sources and build core backend services.

1. **External API Integrations (Tools):**
   - Implement `GoogleMapsService` (Geocoding, Distance Matrix, Places).
   - Implement `RailwayService` (Train search via RailwayAPI.in/RapidAPI).
   - Implement `WeatherService` (OpenWeatherMap One Call API).
   - Implement `BusService` (GTFS feeds parsing and Google Transit).
   - *Mock these services for local development and unit testing.*

2. **Backend API Structure:**
   - Create FastAPI versioned endpoints (`/v1/trips`, `/v1/geocode`, `/v1/temples`).
   - Implement Next.js BFF proxy routes (e.g., `/api/plan`) to forward requests securely.
   - Implement Redis caching layer for API responses (e.g., Geocoding, Train Schedules).

3. **Data Population:**
   - Run initial seed scripts for the `temples` database table.
   - Pre-cache top 100 route pairs and major city geocoding in Redis.

---

## 4. Phase 3: AI Orchestration (Week 3-4)

**Goal:** Build the LangGraph multi-agent system powered by Gemini 3.5 Flash.

1. **Agent Setup:**
   - Define `TripPlanningState` typed dictionary.
   - Create individual agent nodes: `RouteAgent`, `TrainAgent`, `BusAgent`, `WeatherAgent`, `TempleAgent`, `HotelAgent`, `BudgetAgent`, and `ChatAgent`.
   - Inject external API tools into respective agents.
   - Implement `ConversationBufferWindowMemory` backed by Redis for `ChatAgent`.

2. **Orchestrator & Validation:**
   - Build the LangGraph state machine connecting the nodes.
   - Implement parallel dispatch logic for independent agents (Weather, Temple, Hotel).
   - Implement sequential dispatch for dependent agents (e.g., Bus after Train).
   - Write the `ConfidenceValidator` to evaluate agent outputs and assign HIGH/MEDIUM/LOW confidence scores.
   - Implement Fallback Strategies (e.g., degrade gracefully if primary APIs fail).

3. **Streaming Endpoint:**
   - Connect the LangGraph stream to a FastAPI SSE (Server-Sent Events) endpoint (`/v1/trips/plan`).

---

## 5. Phase 4: Frontend Implementation (Week 5)

**Goal:** Build the responsive user interface for trip planning and rendering.

1. **Planner Interface:**
   - Build the search form (`LocationInput`, Date/Time Picker, Preferences).
   - Build the SSE consumer (EventSource / fetch stream) to read planning events.
   - Build the loading state UI (progress steps based on SSE status messages).

2. **Itinerary Rendering:**
   - Build domain components: `LegCard`, `ConfidenceBadge`, `TempleCard`, `WeatherCard`, `HotelCard`, `BudgetPanel`.
   - Implement the interactive timeline view.
   - Integrate Mapbox GL JS (`TripMap`) for route visualization.
   - Implement offline storage (IndexedDB) and PDF generation (`usePdfExport`).

3. **Chat Interface:**
   - Build the conversational UI sidebar (`ChatPanel`).
   - Connect to `/v1/chat` endpoint (SSE) for itinerary modifications and Q&A.
   - Implement Voice Input integration (Web Speech API).

---

## 6. Phase 5: Monetization & Polish (Week 6)

**Goal:** Secure the application and prepare for production launch.

1. **Stripe Integration:**
   - Set up Stripe products (Explorer, Pro, Business tiers).
   - Implement Next.js checkout session endpoints.
   - Implement Stripe webhook handler in FastAPI to update user subscription tiers.

2. **Rate Limiting & Cost Control:**
   - Implement Redis sliding-window rate limiting middleware in FastAPI.
   - Enforce free tier limits (3 trips/month tracked in Redis/PostgreSQL).
   - Implement global circuit breakers (e.g., Gemini spend limits, Maps volume limits).

3. **Security & Observability:**
   - Integrate Datadog APM tracing, metrics, and structured logs.
   - Configure Sentry for frontend and backend error tracking.
   - Audit RBAC and data privacy constraints (DPDP Act compliance).

---

## 7. Phase 6: Beta & Production Launch (Week 7+)

**Goal:** Execute the progressive release strategy defined in the Release Plan.

1. **v0.1 Internal Alpha:**
   - Deploy to Vercel/Railway staging environments.
   - Internal team validation of basic UI and auth flow.
2. **v0.2 Feature Alpha:**
   - End-to-end trip planning with real data.
   - AI orchestration and fallback validation.
3. **v0.5 Closed Beta:**
   - Invite 100 users (pilgrimage travel communities).
   - Monitor P95 response times, token consumption, and hallucination rates.
4. **v1.0 General Availability (GA):**
   - Full public launch with Stripe monetization active.
   - Ensure all exit criteria (WCAG 2.1 AA, Lighthouse > 85, Uptime > 99.9%) are met.
