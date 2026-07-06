# Business Requirements.md

# TravelMate AI — Business Requirements Document (BRD)

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Business Objectives

| ID | Objective | KPI | Target (Year 1) |
|---|---|---|---|
| BO-001 | Acquire 200,000 registered users | Monthly Active Users (MAU) | 200,000 by Month 12 |
| BO-002 | Generate ₹2 crore ARR | Annual Recurring Revenue | ₹2 crore by Month 12 |
| BO-003 | Become the #1 pilgrimage travel planner | NPS, App Store Rating | NPS > 50, Rating > 4.4 |
| BO-004 | Achieve 55% month-2 retention | D30 retention rate | 55% |
| BO-005 | Achieve 8% free-to-paid conversion | Conversion rate | 8% |
| BO-006 | Establish 3 transport data partnerships | Active API partnerships | 3 (IRCTC, GSRTC, Google) |

---

## 2. Business Rules

### 2.1 Data Integrity Rules

| Rule ID | Rule | Rationale |
|---|---|---|
| BR-001 | NEVER display invented transport data | Core product value is accuracy; hallucinated data destroys trust |
| BR-002 | ALL data must have a confidence score (HIGH/MEDIUM/LOW) | Transparency is a competitive differentiator |
| BR-003 | Data older than 24 hours must show a staleness warning | Transport schedules change; stale data causes missed connections |
| BR-004 | Temple timings must show "verify before visiting" if data > 30 days old | Temple schedules change for festivals |
| BR-005 | AI must never claim certainty about real-time data without API confirmation | Prevents user harm from acting on incorrect information |

### 2.2 Trip Planning Rules

| Rule ID | Rule | Rationale |
|---|---|---|
| BR-006 | Minimum transfer buffer: 15 minutes for trains, 10 minutes for buses | Prevents missed connections |
| BR-007 | Walking leg maximum: 2 km without user preference override | Beyond 2km, suggest alternative transport |
| BR-008 | Every itinerary must include first-mile and last-mile legs | Door-to-door completeness is core product promise |
| BR-009 | System must present at least one "fallback route" for every trip | User must never be left without an option |
| BR-010 | Itinerary must be available for download before user leaves the planning screen | Offline access is a core reliability feature |

### 2.3 User Account Rules

| Rule ID | Rule | Rationale |
|---|---|---|
| BR-011 | Free tier limited to 3 trip plans per calendar month | Freemium conversion driver |
| BR-012 | Trip planning limited without account for free tier | Drives registration |
| BR-013 | Emergency access (Rule BR-019) is NEVER blocked by subscription tier | Safety is non-negotiable |
| BR-014 | User data deletion request must be fulfilled within 72 hours | DPDP Act 2023 compliance |
| BR-015 | No advertising on Explorer tier or above | Value proposition of paid tiers |

### 2.4 Payment and Subscription Rules

| Rule ID | Rule | Rationale |
|---|---|---|
| BR-016 | All payments processed via Stripe India (INR) | RBI compliance, UPI support |
| BR-017 | Annual plans discounted 20% vs monthly | Incentivize longer commitment |
| BR-018 | Free trial: 14-day Pro trial for new users | Reduce purchase friction |
| BR-019 | No refunds after 30 days; 100% refund within 7 days | Standard SaaS policy |
| BR-020 | Corporate invoices must be GST-compliant | Mandatory for B2B sales |

### 2.5 Safety and Emergency Rules

| Rule ID | Rule | Rationale |
|---|---|---|
| BR-021 | Emergency contacts screen accessible without authentication | User safety priority |
| BR-022 | Emergency data cached offline always | Works in no-signal zones |
| BR-023 | Women's safety features never hidden behind paywall | Social responsibility |
| BR-024 | Location data never shared with third parties without explicit consent | Privacy principle |

---

## 3. Regulatory Compliance Requirements

### 3.1 DPDP Act 2023 (India)

| Requirement | Implementation |
|---|---|
| Informed consent for data collection | Consent modal on signup with clear data usage explanation |
| Right to access personal data | Data export functionality in user profile |
| Right to correction | Profile edit functionality |
| Right to erasure | Account deletion with 72h data purge |
| Data minimization | Collect only what is necessary (location only when needed) |
| Data localization | PostgreSQL hosted in India (AWS ap-south-1 Mumbai) |

### 3.2 IT Act 2000

| Requirement | Implementation |
|---|---|
| Security practices for sensitive data | AES-256 encryption at rest, TLS 1.3 in transit |
| Grievance officer designation | Contact email in privacy policy |
| Cybersecurity incident reporting | 72h breach notification to CERT-In |

### 3.3 Google Maps Platform ToS

| Requirement | Implementation |
|---|---|
| Attribution | "Map data © Google" shown on all map views |
| No data caching beyond ToS limits | Map tiles cached for offline per ToS |
| No reverse engineering | API used only for documented endpoints |

---

## 4. Operational Requirements

### 4.1 Support

| Tier | Response SLA | Channels |
|---|---|---|
| Free | 72 hours | Email only |
| Explorer | 24 hours | Email |
| Pro | 8 hours | Email, in-app chat |
| Business | 4 hours | Email, in-app chat, phone |

### 4.2 Monitoring and Alerting

| Event | Action | Responsible |
|---|---|---|
| Itinerary P95 > 10s | PagerDuty alert | Engineering on-call |
| Error rate > 1% | PagerDuty alert | Engineering on-call |
| AI API failure | Fallback to cached responses; alert engineering | Engineering on-call |
| Payment failure | Stripe webhook → retry; notify user | Engineering + Finance |
| Database replication lag > 30s | Alert | DBA |

---

## 5. Business Stakeholders

| Stakeholder | Interest | Involvement |
|---|---|---|
| Founder/CEO | Product vision, revenue | Strategic decisions |
| CTO | Technical architecture | Technical reviews |
| Product Manager | Feature prioritization | Sprint planning |
| Engineering Lead | Implementation | Daily development |
| QA Lead | Quality assurance | Release gating |
| Marketing | User acquisition | GTM coordination |
| Customer Success | User retention | Support and feedback |
