# Monitoring.md

# TravelMate AI — Monitoring & Observability

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Observability Stack

| Layer | Tool | Purpose |
|---|---|---|
| **APM / Tracing** | Datadog APM | Distributed request tracing, latency breakdown |
| **Metrics** | Datadog Metrics | Custom business and infrastructure metrics |
| **Logging** | Datadog Logs | Structured JSON logs, centralized search |
| **Error Tracking** | Sentry | Frontend and backend exception tracking |
| **User Analytics** | PostHog | Behavioral analytics, funnel analysis |
| **Uptime** | Datadog Synthetics | Endpoint health checks from multiple regions |
| **Alerting** | PagerDuty | On-call escalation for critical alerts |
| **Dashboards** | Datadog Dashboards | Real-time operational visibility |

---

## 2. Key Metrics

### 2.1 System Metrics (Infrastructure)

| Metric | Source | Alert Threshold |
|---|---|---|
| CPU utilization (per pod) | Railway / Datadog | > 80% sustained 5 min |
| Memory utilization (per pod) | Railway / Datadog | > 85% |
| Disk usage (PostgreSQL) | Railway | > 80% |
| Redis memory usage | Railway | > 80% of maxmemory |
| Network I/O | Railway | > 100 MB/s sustained |

### 2.2 Application Metrics

| Metric | Collection Method | Alert Threshold |
|---|---|---|
| API request rate (req/sec) | Datadog APM | Unusual spike > 3x normal |
| API error rate (5xx/total) | Datadog APM | > 1% in 5-min window |
| API P50 latency | Datadog APM | — (monitoring only) |
| API P95 latency | Datadog APM | > 8 seconds for /v1/trips/plan |
| API P99 latency | Datadog APM | > 15 seconds for any endpoint |
| Trip planning success rate | Custom metric | < 95% |
| Cache hit rate | Custom metric | < 50% (investigate cache config) |
| Active WebSocket connections | Custom metric | > 10,000 (capacity concern) |

### 2.3 AI Agent Metrics

| Metric | Source | Alert Threshold |
|---|---|---|
| Agent response time (P50, P95) | Custom timing | P95 > 10 seconds |
| Token consumption per request | Custom counter | Average > 10,000 tokens |
| Agent failure rate | Custom counter | > 5% |
| Hallucination rate (post-validation) | Confidence validator logs | > 0.5% |
| LLM API latency (Gemini) | httpx timing | P95 > 5 seconds |
| LLM API error rate | httpx response codes | > 2% |

### 2.4 Business Metrics

| Metric | Source | Dashboard |
|---|---|---|
| Daily Active Users (DAU) | PostHog | Executive Dashboard |
| Trips planned per day | Custom metric | Product Dashboard |
| Subscription conversions | Stripe webhook events | Revenue Dashboard |
| Churn events | Stripe webhook events | Revenue Dashboard |
| Top routes | Database query | Product Dashboard |
| Feature usage (chat, voice, PDF) | PostHog events | Product Dashboard |

---

## 3. Alerting Rules

### 3.1 Critical (PagerDuty — immediate)

| Alert | Condition | Action |
|---|---|---|
| Service Down | Health check fails 3 consecutive times | Page on-call engineer |
| Error Rate Spike | 5xx rate > 5% for 5 minutes | Page on-call engineer |
| Database Down | PostgreSQL connection failed | Page on-call + DBA |
| 0 Trip Plans | No successful trip plans for 10 minutes (during business hours) | Page on-call engineer |

### 3.2 High (PagerDuty — 15 min)

| Alert | Condition |
|---|---|
| P95 latency spike | Trip planning P95 > 15 seconds for 5 minutes |
| AI API failure | Gemini API returning errors > 10% for 5 minutes |
| Redis connection lost | Redis unavailable for > 1 minute |

### 3.3 Warning (Slack #alerts)

| Alert | Condition |
|---|---|
| P95 latency elevated | Trip planning P95 > 10 seconds for 15 minutes |
| Cache hit rate low | < 40% for 1 hour |
| Disk usage high | PostgreSQL disk > 70% |
| Celery queue backing up | Queue depth > 200 tasks |
| Stripe webhook failures | > 3 failed webhook deliveries in 1 hour |

### 3.4 Info (Slack #engineering)

| Alert | Condition |
|---|---|
| New deployment | CI/CD pipeline completes |
| Daily KPI summary | Automated daily at 09:00 IST |
| Dependency update available | Dependabot PR opened |

---

## 4. Dashboards

### 4.1 Operational Dashboard (real-time, always-on)

```
┌──────────────────────────────────────────────┐
│        TravelMate AI — Operations            │
├──────────┬──────────┬──────────┬─────────────┤
│ API RPS  │ Error %  │ P95 (ms) │ Uptime      │
│ [graph]  │ [graph]  │ [graph]  │ [99.9%]     │
├──────────┴──────────┴──────────┴─────────────┤
│ Active Users    │ Trips/hour    │ Cache Hit % │
│ [gauge]         │ [counter]     │ [gauge]     │
├─────────────────┴───────────────┴─────────────┤
│ AI Agent Performance                          │
│ [response time heatmap by agent]              │
├───────────────────────────────────────────────┤
│ Recent Errors (last 1 hour)                   │
│ [error list with stack trace links]           │
└───────────────────────────────────────────────┘
```

### 4.2 Revenue Dashboard (daily refresh)

Metrics from Stripe Dashboard + PostHog:
- MRR trend (30 days)
- New subscriptions this week
- Churn events this week
- Conversion funnel: Visit → Sign Up → Free Trial → Paid

---

## 5. Health Check Endpoints

| Endpoint | Purpose | Checks | Expected Response Time |
|---|---|---|---|
| `GET /health` | Basic liveness | App running | < 50ms |
| `GET /health/ready` | Full readiness | DB + Redis + External APIs | < 2 seconds |

`/health/ready` response format:
```json
{
  "status": "healthy",
  "checks": {
    "database": { "status": "ok", "latency_ms": 12 },
    "redis": { "status": "ok", "latency_ms": 3 },
    "railway_api": { "status": "ok", "latency_ms": 245 },
    "gemini": { "status": "ok", "latency_ms": 180 }
  },
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```
