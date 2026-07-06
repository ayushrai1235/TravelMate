# Non Functional Requirements.md

# TravelMate AI — Non-Functional Requirements (NFR)

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Performance

### 1.1 Response Time

| NFR ID | Requirement | Target | Measurement |
|---|---|---|---|
| NFR-PERF-001 | Trip planning API P50 response time | < 4 seconds | Backend timing logs |
| NFR-PERF-002 | Trip planning API P95 response time | < 8 seconds | Backend timing logs |
| NFR-PERF-003 | Trip planning API P99 response time | < 12 seconds | Backend timing logs |
| NFR-PERF-004 | All non-AI API endpoints P95 | < 500ms | Datadog APM |
| NFR-PERF-005 | AI chat first token stream | < 2 seconds | Frontend timing |
| NFR-PERF-006 | Page First Contentful Paint (FCP) | < 1.5 seconds | Lighthouse (mobile) |
| NFR-PERF-007 | Largest Contentful Paint (LCP) | < 2.5 seconds | Lighthouse (mobile) |
| NFR-PERF-008 | Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| NFR-PERF-009 | Time to Interactive (TTI) | < 3.5 seconds | Lighthouse (mobile) |
| NFR-PERF-010 | Map initial render time | < 2 seconds | Custom timing |

### 1.2 Throughput

| NFR ID | Requirement | Target |
|---|---|---|
| NFR-TPUT-001 | Concurrent user capacity (v1.0) | 10,000 users |
| NFR-TPUT-002 | Concurrent user capacity (v2.0) | 100,000 users |
| NFR-TPUT-003 | Trip planning requests per minute | 500 (v1.0) |
| NFR-TPUT-004 | API requests per second (total) | 200 (v1.0) |
| NFR-TPUT-005 | Database connections | Max 100 (connection pooling) |

### 1.3 Resource Efficiency

| NFR ID | Requirement | Target |
|---|---|---|
| NFR-RES-001 | Maximum AI token usage per trip plan | 8,000 tokens (input + output) |
| NFR-RES-002 | Cache hit rate for repeated queries | ≥ 70% |
| NFR-RES-003 | Frontend bundle size (gzipped) | < 500KB initial load |
| NFR-RES-004 | Image assets (Cloudinary auto-optimize) | WebP format, < 100KB per image |

---

## 2. Availability and Reliability

| NFR ID | Requirement | Target | Measurement |
|---|---|---|---|
| NFR-AVAIL-001 | API service uptime | 99.9% | Uptime robot / Datadog |
| NFR-AVAIL-002 | Planned maintenance window | Max 2 hours/month; off-peak hours only | Change management log |
| NFR-AVAIL-003 | Recovery Time Objective (RTO) | < 4 hours (complete service restoration) | Incident log |
| NFR-AVAIL-004 | Recovery Point Objective (RPO) | < 1 hour data loss | Backup verification |
| NFR-AVAIL-005 | External API failure handling | Graceful degradation; partial results shown | Chaos testing |
| NFR-AVAIL-006 | Database failover time | < 30 seconds (replica promotion) | Failover test |

---

## 3. Scalability

| NFR ID | Requirement | Design Approach |
|---|---|---|
| NFR-SCALE-001 | Horizontal scaling of API | Stateless FastAPI pods behind load balancer |
| NFR-SCALE-002 | Database read scaling | Read replicas for query-heavy endpoints |
| NFR-SCALE-003 | Cache scaling | Redis Cluster for high-throughput caching |
| NFR-SCALE-004 | CDN for static assets | Vercel Edge Network (global CDN) |
| NFR-SCALE-005 | AI token budget scaling | Request queue with Celery; token rate limiting per user |
| NFR-SCALE-006 | Auto-scaling triggers | CPU > 70% or queue depth > 100 items → scale up |

---

## 4. Security

| NFR ID | Requirement | Implementation |
|---|---|---|
| NFR-SEC-001 | Authentication for protected endpoints | Clerk JWT verification in FastAPI middleware |
| NFR-SEC-002 | Transport Layer Security | TLS 1.3 minimum; HSTS enabled |
| NFR-SEC-003 | Data encryption at rest | AES-256 for sensitive fields; PostgreSQL encrypted tablespace |
| NFR-SEC-004 | API rate limiting | 100 req/min per authenticated user; 10 req/min per IP (unauth) |
| NFR-SEC-005 | OWASP Top 10 compliance | Verified by security audit before v1.0 launch |
| NFR-SEC-006 | Dependency vulnerability scanning | Dependabot + Snyk in CI; block merge on critical CVEs |
| NFR-SEC-007 | Secret management | All secrets in environment variables; never in code |
| NFR-SEC-008 | SQL injection prevention | SQLAlchemy ORM only; no raw SQL string interpolation |
| NFR-SEC-009 | XSS prevention | React escaping + Content-Security-Policy headers |
| NFR-SEC-010 | CSRF protection | SameSite=Strict cookies; CSRF tokens on state-changing operations |
| NFR-SEC-011 | Audit logging | All admin actions and auth events logged to audit_logs table |
| NFR-SEC-012 | PII handling | Location data minimized; never logged in plaintext |

---

## 5. Maintainability

| NFR ID | Requirement | Target |
|---|---|---|
| NFR-MAINT-001 | Code test coverage | ≥ 80% for business logic; ≥ 60% overall |
| NFR-MAINT-002 | API documentation | Auto-generated OpenAPI spec (FastAPI); always current |
| NFR-MAINT-003 | Code style enforcement | ESLint + Prettier (TS); Ruff + Black (Python); enforced in CI |
| NFR-MAINT-004 | Deployment frequency | Capable of multiple deployments per day |
| NFR-MAINT-005 | Mean Time to Recovery (MTTR) | < 2 hours for P1 incidents |
| NFR-MAINT-006 | Hotfix deployment time | < 30 minutes from code merge to production |
| NFR-MAINT-007 | Database migration safety | All migrations reversible; tested in staging before production |

---

## 6. Usability

| NFR ID | Requirement | Target |
|---|---|---|
| NFR-USE-001 | Learnability | New user generates first itinerary in < 3 minutes, no training |
| NFR-USE-002 | Error recovery | All error states provide actionable next steps |
| NFR-USE-003 | Loading feedback | Every operation > 1 second shows a loading indicator |
| NFR-USE-004 | Mobile-first design | Primary design target is 375px–414px viewport |
| NFR-USE-005 | Touch targets | Minimum 44×44px touch targets (iOS HIG / WCAG) |
| NFR-USE-006 | Offline behavior | Clearly communicated offline state with available offline features |

---

## 7. Accessibility

| NFR ID | Requirement | Standard | Scope |
|---|---|---|---|
| NFR-A11Y-001 | Color contrast | WCAG 2.1 AA (4.5:1 text; 3:1 UI components) | All screens |
| NFR-A11Y-002 | Keyboard navigation | All features operable via keyboard alone | Core flows |
| NFR-A11Y-003 | Screen reader compatibility | ARIA roles and labels on all interactive elements | All screens |
| NFR-A11Y-004 | Focus management | Focus order logical; focus trapped in modals | All screens |
| NFR-A11Y-005 | Text resize | Interface functional at 200% text zoom | All screens |
| NFR-A11Y-006 | Motion sensitivity | Animations respect prefers-reduced-motion | All animations |
| NFR-A11Y-007 | Form accessibility | All form inputs have associated labels and error messages | All forms |
| NFR-A11Y-008 | Alternative text | All informational images have descriptive alt text | All images |

---

## 8. Localization and Internationalization

| NFR ID | Requirement |
|---|---|
| NFR-I18N-001 | All UI strings extracted to locale files from day 1 |
| NFR-I18N-002 | Date format: DD/MM/YYYY (Indian standard) |
| NFR-I18N-003 | Currency: INR (₹) displayed with Indian number formatting (lakhs, crores) |
| NFR-I18N-004 | Time format: 12-hour AM/PM by default; 24-hour as preference option |
| NFR-I18N-005 | Number formatting: Indian system (1,00,000 not 100,000) |
| NFR-I18N-006 | RTL layout not required for v1.0 (no Urdu/Arabic target) |

---

## 9. Observability

| NFR ID | Requirement | Tool |
|---|---|---|
| NFR-OBS-001 | All API requests logged with request ID, duration, status | Datadog |
| NFR-OBS-002 | All AI agent steps logged with token count and duration | Datadog + custom |
| NFR-OBS-003 | Frontend errors captured with stack trace | Sentry |
| NFR-OBS-004 | Business event tracking (trip planned, user signed up) | PostHog |
| NFR-OBS-005 | Uptime monitoring with alerts | Datadog Synthetics |
| NFR-OBS-006 | Database slow query alerts (> 1 second) | PostgreSQL pg_stat_statements |
| NFR-OBS-007 | Distributed tracing for multi-service requests | Datadog APM |

---

## 10. Compliance

| NFR ID | Requirement | Regulation |
|---|---|---|
| NFR-COMP-001 | User consent for data collection | DPDP Act 2023 |
| NFR-COMP-002 | Right to erasure implementation (72h) | DPDP Act 2023 |
| NFR-COMP-003 | Data stored in India (AWS ap-south-1) | DPDP Act 2023 |
| NFR-COMP-004 | GST-compliant invoices for B2B | GST Act |
| NFR-COMP-005 | Payment processing via RBI-licensed processor (Stripe India) | RBI guidelines |
| NFR-COMP-006 | Terms of Service and Privacy Policy linked from all pages | IT Act 2000 |
| NFR-COMP-007 | CERT-In breach notification within 72 hours | CERT-In directive |
