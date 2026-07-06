# TRD.md

# TravelMate AI — Technical Requirements Document (TRD)

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Owner:** Engineering Team  
**Status:** Approved

---

## 1. Purpose

This Technical Requirements Document defines the engineering constraints, technology choices, integration specifications, and performance requirements for TravelMate AI. It translates the Product Requirements Document (PRD) into precise technical specifications that engineers will implement.

---

## 2. Technology Stack Specification

### 2.1 Frontend

| Technology | Version | Purpose | Justification |
|---|---|---|---|
| **Next.js** | 16.x | React framework, SSR/SSG, file-based routing | Industry standard, great SEO, App Router, RSC support |
| **React** | 19.x | UI component library | Latest stable, concurrent features, Server Components |
| **TypeScript** | 5.x | Type safety across entire codebase | Prevents runtime bugs, better IDE support |
| **TailwindCSS** | 3.x | Utility-first CSS | Rapid development, consistent design system |
| **shadcn/ui** | Latest | Pre-built accessible component primitives | Accessible, customizable, no runtime overhead |
| **Framer Motion** | 11.x | Animation library | Smooth, production-ready animations |
| **Mapbox GL JS** | 3.x | Map rendering | Superior control vs Google Maps embed for custom styling |
| **Zustand** | 4.x | Client state management | Lightweight, no boilerplate, works with React 19 |
| **React Query (TanStack)** | 5.x | Server state management, caching, refetch | Industry standard for API state |
| **React Hook Form** | 7.x | Form management | Performance-optimized forms |
| **Zod** | 3.x | Schema validation (shared with backend) | Type-safe validation end-to-end |

### 2.2 Backend

| Technology | Version | Purpose | Justification |
|---|---|---|---|
| **FastAPI** | 0.115.x | Python API framework | Async, fast, automatic OpenAPI docs, type hints |
| **Python** | 3.12.x | Backend language | Required for LangGraph, LangChain ecosystem |
| **LangGraph** | 0.2.x | AI agent orchestration | State machine for multi-agent workflows |
| **LangChain** | 0.3.x | LLM tooling, tool-calling | Standard LLM integration library |
| **Pydantic** | 2.x | Data validation (FastAPI models) | Fast, type-safe validation |
| **SQLAlchemy** | 2.x | ORM | Async support, type-safe queries |
| **Alembic** | 1.x | Database migrations | Version-controlled schema changes |
| **Celery** | 5.x | Background task queue | Async notification processing, data refresh |
| **httpx** | 0.27.x | Async HTTP client | For external API calls in async context |

### 2.3 Database and Storage

| Technology | Version | Purpose | Justification |
|---|---|---|---|
| **PostgreSQL** | 16.x | Primary relational database | ACID compliance, JSON support, full-text search |
| **Redis** | 7.x | Caching, session storage, Celery broker | Sub-millisecond reads, pub/sub for real-time |
| **Cloudinary** | — | Image and media storage | Automatic optimization, CDN delivery |

### 2.4 Infrastructure and DevOps

| Technology | Version | Purpose | Justification |
|---|---|---|---|
| **Docker** | 27.x | Containerization | Reproducible environments |
| **Docker Compose** | 2.x | Local multi-service orchestration | Developer experience |
| **GitHub Actions** | — | CI/CD pipeline | Integrated with repository |
| **Vercel** | — | Frontend hosting | Next.js native platform, edge functions |
| **Railway** | — | Backend hosting | Simple FastAPI deployment, managed PostgreSQL |
| **AWS S3** | — | Backup storage | Cheap, durable |

### 2.5 External APIs

| API | Provider | Purpose | Tier Required |
|---|---|---|---|
| **Maps (Geocoding, Directions, Places)** | Google Maps Platform | Location resolution, routing, POIs | Pay-as-you-go |
| **Maps (Rendering)** | Mapbox | Interactive map display | Free tier + paid for scale |
| **Train Schedules** | RailwayAPI.in (RapidAPI) | Real-time Indian train data | Pro plan |
| **Flights** | Amadeus for Developers | Flight schedule and pricing | Self-service |
| **Weather** | OpenWeatherMap | 7-day forecasts | One Call API plan |
| **Bus GTFS** | GSRTC, MSRTC (public feeds) | Bus schedules | Free (public data) |
| **Authentication** | Clerk | User management, OAuth | Pro plan |
| **Payments** | Stripe | Subscriptions, payments | Standard plan |
| **AI LLM** | Google Gemini 3.5 Flash | Agent reasoning, chat | API plan |
| **Image Storage** | Cloudinary | Image uploads and optimization | Free tier |

---

## 3. System Architecture Requirements

### 3.1 Architecture Pattern

**Clean Architecture** with Domain-Driven Design (DDD) separation:

```
Presentation Layer    → Next.js pages, API routes
Application Layer     → FastAPI endpoints, use cases
Domain Layer          → Business logic, entities, value objects
Infrastructure Layer  → Database, cache, external API clients
```

**Key Principles:**
- Dependency injection throughout (no circular imports)
- Repository pattern for all database operations
- Service layer between API endpoints and database repositories
- All external API calls abstracted behind interface classes

### 3.2 Communication Patterns

| Pattern | Use Case |
|---|---|
| **REST API** | Frontend → Backend (trip planning, user data) |
| **Server-Sent Events (SSE)** | AI response streaming to frontend |
| **WebSockets** | Real-time train delay updates (if needed) |
| **Celery tasks** | Background notification sending, data refresh |
| **Redis pub/sub** | Real-time events between services |

### 3.3 Caching Strategy

| Cache Type | Technology | TTL | Data |
|---|---|---|---|
| Train schedules | Redis | 30 minutes | Live train data |
| Bus GTFS data | Redis | 24 hours | Scheduled routes |
| Geocoding results | Redis | 7 days | Location lookups |
| Weather forecasts | Redis | 1 hour | Weather data |
| Temple timings | Redis | 24 hours | Curated data |
| AI responses | Redis | 1 hour (for identical queries) | LLM responses |
| User sessions | Redis | 24 hours | JWT session data |

---

## 4. Performance Requirements

### 4.1 Response Time Requirements

| Endpoint | P50 | P95 | P99 |
|---|---|---|---|
| GET /health | < 50ms | < 100ms | < 200ms |
| POST /api/geocode | < 200ms | < 500ms | < 1000ms |
| POST /api/trips/plan | < 4s | < 8s | < 12s |
| GET /api/trips/{id} | < 100ms | < 300ms | < 500ms |
| POST /api/chat | < 2s (first token) | < 3s | < 5s |
| GET /api/weather | < 200ms | < 500ms | < 1s |
| GET /api/temples/{id} | < 100ms | < 200ms | < 400ms |

### 4.2 Throughput Requirements

| Metric | Requirement |
|---|---|
| Concurrent users | 10,000 (v1.0), 100,000 (v2.0) |
| Trip planning requests/minute | 500 (v1.0), 5,000 (v2.0) |
| API requests/second | 200 (v1.0), 2,000 (v2.0) |
| Database connections | 100 max (connection pooling) |

### 4.3 Reliability Requirements

| Metric | Requirement |
|---|---|
| API uptime | 99.9% (8.7 hours downtime/year) |
| Data durability | 99.999% (database backups) |
| Recovery Point Objective (RPO) | < 1 hour |
| Recovery Time Objective (RTO) | < 4 hours |

---

## 5. Security Requirements

| Requirement | Specification |
|---|---|
| Authentication | Clerk JWT tokens; verified on every protected request |
| Authorization | Role-based: user, admin; checked in middleware |
| Data encryption (rest) | AES-256 for sensitive fields (location history) |
| Data encryption (transit) | TLS 1.3 minimum |
| API rate limiting | 100 requests/minute per user; 10 per IP (unauthenticated) |
| SQL injection prevention | SQLAlchemy ORM parameterized queries only |
| XSS prevention | React auto-escaping; Content-Security-Policy headers |
| CSRF protection | SameSite cookies; CSRF tokens on mutations |
| Secret management | Environment variables; never in code or logs |
| Dependency scanning | Dependabot + Snyk in CI |

---

## 6. Data Requirements

### 6.1 Data Residency

All user data must be stored in servers located in India (AWS ap-south-1 Mumbai) to comply with DPDP Act 2023 data localization provisions.

### 6.2 Data Retention

| Data Type | Retention Period | Justification |
|---|---|---|
| User account data | Until deletion request | DPDP compliance |
| Trip planning history | 24 months | User value (re-plan same trips) |
| AI conversation logs | 6 months | Debugging, accuracy improvement |
| Transport API responses | 24 hours | Freshness requirement |
| Error logs | 90 days | Debugging |
| Audit logs | 12 months | Security and compliance |
| Payment records | 7 years | GST compliance |

### 6.3 Data Backup

- PostgreSQL: Daily full backup + WAL streaming replication
- Redis: RDB snapshots every 5 minutes + AOF
- Backups stored in AWS S3 (same region: ap-south-1)
- Backup retention: 30 days

---

## 7. Accessibility Requirements

| Requirement | Standard | Scope |
|---|---|---|
| Color contrast | WCAG 2.1 AA (4.5:1 minimum) | All text |
| Keyboard navigation | All interactive elements reachable by Tab | Core flows |
| Screen reader support | ARIA labels, landmark roles | Core screens |
| Font size | Minimum 16px body; resizable to 200% without loss | All screens |
| Focus indicators | Visible focus ring on all interactive elements | All screens |
| Alt text | All images have descriptive alt text | All images |
| Form labels | All form inputs have associated labels | All forms |
| Error messages | All errors announced to screen readers | All forms |

---

## 8. Internationalisation Requirements (i18n)

| Phase | Languages |
|---|---|
| v1.0 | English |
| v1.5 | Hindi |
| v2.0 | Gujarati, Marathi |
| v2.5 | Tamil, Telugu, Kannada |

**Implementation:** next-intl library; all strings extracted to locale JSON files from day 1 (even if only English exists initially). This prevents costly refactoring later.

---

## 9. Browser and Device Support

| Browser/OS | Minimum Version | Support Level |
|---|---|---|
| Chrome (Android/Desktop) | 90+ | Full |
| Safari (iOS/macOS) | 14+ | Full |
| Firefox (Desktop) | 88+ | Full |
| Samsung Internet | 14+ | Full |
| Edge | 90+ | Full |
| Opera Mini | — | Degraded (no JS features) |

**Device Support:**
- Mobile: 360px minimum viewport width
- Tablet: 768px–1024px
- Desktop: 1024px+
- Large Desktop: 1440px+ (max-width constrained)
