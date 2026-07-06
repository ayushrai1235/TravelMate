# Risk Analysis.md

# TravelMate AI — Risk Analysis

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## Risk Assessment Framework

Each risk is scored using:
- **Probability:** 1 (Very Low) – 5 (Very High)
- **Impact:** 1 (Minimal) – 5 (Catastrophic)
- **Risk Score:** Probability × Impact (1–25)
- **Priority:** Low (1–6) | Medium (7–14) | High (15–19) | Critical (20–25)

---

## 1. Technical Risks

### RT-001: AI Hallucination of Transport Data

**Description:** The AI LLM generates invented bus numbers, train schedules, or station names that appear real but are fabricated.

| Attribute | Value |
|---|---|
| Probability | 4 (High — inherent LLM behavior) |
| Impact | 5 (Catastrophic — user misses trains; trust destroyed) |
| **Risk Score** | **20 (Critical)** |

**Mitigation Strategy:**
1. Every AI-generated transport entity is cross-validated against real data sources
2. Confidence validator rejects any unverifiable transport entity
3. Fallback to rule-based routing when AI cannot produce verifiable output
4. Extensive prompt engineering to instruct AI to use only tool-call data
5. Ongoing monitoring: monthly audits of 100 random itineraries

**Residual Risk:** Low — confidence scoring + validator reduces hallucination risk to < 0.1%

---

### RT-002: IRCTC / Indian Railways API Unavailability

**Description:** No reliable, official, free Indian Railways booking API exists. Third-party APIs (RailwayAPI.in) may become unavailable or change their pricing.

| Attribute | Value |
|---|---|
| Probability | 3 (Medium) |
| Impact | 5 (Catastrophic — trains are primary transport mode in India) |
| **Risk Score** | **15 (High)** |

**Mitigation Strategy:**
1. Multi-source train data: RailwayAPI + RapidAPI alternatives
2. Cache train schedules (30-min TTL) to reduce dependency on live API
3. GTFS India train schedule files as static fallback
4. Communicate to users: "Schedule information; book via IRCTC to confirm availability"
5. Never use TravelMate as a booking platform (reduces liability)

**Residual Risk:** Medium — some degradation possible during API outages

---

### RT-003: Google Maps API Cost Overrun

**Description:** Google Maps Platform billing can escalate rapidly with high usage; geocoding + distance matrix + places = multiple API calls per trip.

| Attribute | Value |
|---|---|
| Probability | 3 (Medium) |
| Impact | 4 (High — cost spiral could threaten viability) |
| **Risk Score** | **12 (Medium)** |

**Mitigation Strategy:**
1. Implement Mapbox as primary geocoding fallback (cheaper for many use cases)
2. Aggressive caching of geocoding results (7-day TTL for city/landmark queries)
3. Google Maps API budget alerts at $500, $1000, $2000/month
4. Distance matrix results cached per origin-destination pair
5. Rate limiting per user to prevent abuse

**Residual Risk:** Low-Medium — caching should keep costs manageable

---

### RT-004: LLM API Cost Overrun

**Description:** Each trip planning request may consume 5,000–10,000 tokens (input + output). At scale, AI API costs can grow dramatically.

| Attribute | Value |
|---|---|
| Probability | 3 (Medium) |
| Impact | 4 (High) |
| **Risk Score** | **12 (Medium)** |

**Mitigation Strategy:**
1. Token budget enforced per request (max 8,000 tokens)
2. Response caching for identical trip queries (1-hour cache)
3. Free tier limits AI usage; paid tiers subsidize costs
4. Streaming reduces perceived latency without increasing tokens
5. Monthly token budget monitoring; alert at 80% of budget

**Residual Risk:** Low

---

### RT-005: GTFS Data Gaps

**Description:** Not all Indian states publish reliable GTFS feeds. Bus route data may be incomplete or outdated for Tier-2/3 cities.

| Attribute | Value |
|---|---|
| Probability | 5 (Very High — this is a known data reality) |
| Impact | 3 (Medium — bus planning degrades; alternatives available) |
| **Risk Score** | **15 (High)** |

**Mitigation Strategy:**
1. Multi-source bus data: GTFS → Google Transit → State API → AI-guided fallback
2. Confidence scoring transparently communicated to users
3. AI guidance with LOW confidence label preferred over silence
4. Partnerships with GSRTC, MSRTC to obtain official feeds (long-term)
5. Community-contributed bus route corrections (v2.0)

**Residual Risk:** Medium — fallback guidance is available but not as precise

---

### RT-006: Database Single Point of Failure

**Description:** If the primary PostgreSQL database becomes unavailable, all write operations fail.

| Attribute | Value |
|---|---|
| Probability | 2 (Low) |
| Impact | 5 (Catastrophic — service completely down) |
| **Risk Score** | **10 (Medium)** |

**Mitigation Strategy:**
1. PostgreSQL streaming replication to read replica (Railway managed)
2. Automatic failover via pgBouncer + Health check
3. Redis queue for write operations during brief outages
4. Daily automated backups to AWS S3
5. RTO target: < 4 hours; RPO: < 1 hour

**Residual Risk:** Low

---

## 2. Business Risks

### RB-001: Competition from MakeMyTrip / Goibibo

**Description:** Large incumbents launch AI-powered multi-modal planning features.

| Attribute | Value |
|---|---|
| Probability | 3 (Medium) |
| Impact | 4 (High) |
| **Risk Score** | **12 (Medium)** |

**Mitigation Strategy:**
1. Speed to market — launch before competitors
2. Deep pilgrimage niche specialization they won't prioritize
3. Open-source community data (temple database) creates moat
4. Superior UX for low-tech users (senior citizens, first-time users)
5. Partnership with pilgrimage organizations

---

### RB-002: Free Tier Abuse

**Description:** Users create multiple free accounts to bypass the 3 trips/month limit.

| Attribute | Value |
|---|---|
| Probability | 4 (High) |
| Impact | 2 (Low — increases AI costs, reduces conversion) |
| **Risk Score** | **8 (Medium)** |

**Mitigation Strategy:**
1. Phone number OTP verification for accounts (harder to fake)
2. IP-based rate limiting on trip planning API
3. Email verification required for free account
4. Device fingerprinting to detect multi-account creation
5. Make paid features compelling enough that abuse isn't worth effort

---

### RB-003: Regulatory Change (DPDP Act 2023)

**Description:** New data protection rules require significant architectural changes.

| Attribute | Value |
|---|---|
| Probability | 2 (Low) |
| Impact | 4 (High — significant development cost) |
| **Risk Score** | **8 (Medium)** |

**Mitigation Strategy:**
1. Data minimization by design — collect only what's necessary
2. Clear consent flows from day 1
3. Data portability and deletion implemented before launch
4. Legal counsel review of DPDP requirements quarterly

---

## 3. Operational Risks

### RO-001: Key Person Dependency

**Description:** Small team; if AI Engineer leaves, LangGraph orchestrator becomes unmanageable.

| Attribute | Value |
|---|---|
| Probability | 3 (Medium) |
| Impact | 4 (High) |
| **Risk Score** | **12 (Medium)** |

**Mitigation Strategy:**
1. Extensive code documentation (JSDoc, docstrings, architecture docs — this document)
2. Pair programming requirement for AI agent components
3. LangGraph state documented in AI Agents.md
4. Weekly knowledge transfer sessions

---

### RO-002: Transport Data Accuracy Causing Real-World Harm

**Description:** User misses a train or arrives at wrong destination due to incorrect AI-generated information.

| Attribute | Value |
|---|---|
| Probability | 2 (Low — if mitigation implemented) |
| Impact | 5 (Catastrophic — safety + legal liability) |
| **Risk Score** | **10 (Medium)** |

**Mitigation Strategy:**
1. Confidence scoring on every data point
2. Clear disclaimer: "TravelMate AI provides planning assistance. Always verify schedules with official sources."
3. Never claim real-time data without API confirmation
4. Legal Terms of Service limit liability to planning assistance (not guaranteed transport)
5. Emergency contacts always accessible

---

## 4. Risk Register Summary

| ID | Risk | Score | Priority | Owner |
|---|---|---|---|---|
| RT-001 | AI hallucination | 20 | Critical | AI Engineer |
| RT-002 | Train API unavailability | 15 | High | Backend Engineer |
| RT-005 | GTFS data gaps | 15 | High | Data Engineer |
| RT-003 | Google Maps cost | 12 | Medium | Engineering Lead |
| RT-004 | LLM cost | 12 | Medium | Engineering Lead |
| RB-001 | Competition | 12 | Medium | Product |
| RO-001 | Key person dependency | 12 | Medium | CTO |
| RT-006 | Database SPOF | 10 | Medium | DevOps |
| RO-002 | Data accuracy harm | 10 | Medium | Product + Legal |
| RB-002 | Free tier abuse | 8 | Medium | Engineering |
| RB-003 | Regulatory change | 8 | Medium | Legal + Engineering |

---

## 5. Risk Review Cadence

| Risk Category | Review Frequency | Owner |
|---|---|---|
| Technical risks | Fortnightly sprint retrospective | Engineering Lead |
| Business risks | Monthly leadership review | CEO + Product |
| Operational risks | Quarterly | CTO |
| Security risks | Monthly security review | Security Lead |
| All Critical risks | Weekly | CTO |
