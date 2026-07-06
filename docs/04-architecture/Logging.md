# Logging.md

# TravelMate AI — Logging Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Logging Standards

All logs are **structured JSON**. No plaintext log lines. Every log entry includes:

```json
{
  "timestamp": "2026-07-03T14:00:00.000Z",
  "level": "INFO",
  "service": "travelmate-api",
  "request_id": "req_abc123",
  "user_id": "usr_def456",
  "message": "Trip plan completed",
  "data": {
    "origin": "Navsari",
    "destination": "Trimbakeshwar",
    "duration_ms": 4200,
    "legs_count": 4,
    "cache_hit": false
  }
}
```

---

## 2. Log Levels

| Level | Usage | Example | Destination |
|---|---|---|---|
| **DEBUG** | Detailed flow tracing; dev only | "RouteAgent: calling RailwayAPI with params {origin: NVS, dest: NK}" | Local console only; NEVER in production |
| **INFO** | Normal business events | "Trip planned: Navsari→Trimbakeshwar, 4 legs, 4.2s" | Datadog Logs |
| **WARN** | Non-critical issues | "GTFS feed for MSRTC is stale (48h); using cached data" | Datadog Logs + Slack |
| **ERROR** | Exceptions, failures | "RailwayAPI returned 500 after 3 retries" | Datadog Logs + Sentry + PagerDuty |
| **CRITICAL** | System-down events | "Database connection pool exhausted" | Datadog + Sentry + PagerDuty immediate |

---

## 3. What to Log

### 3.1 Always Log

| Event | Level | Data to Include |
|---|---|---|
| API request received | INFO | method, path, user_id, request_id |
| API response sent | INFO | status_code, response_time_ms, request_id |
| Trip plan started | INFO | origin, destination, date |
| Trip plan completed | INFO | duration_ms, legs_count, cache_hit, confidence_summary |
| Agent invoked | INFO | agent_name, start_time |
| Agent completed | INFO | agent_name, duration_ms, token_count, success |
| External API called | INFO | api_name, endpoint, response_time_ms, status |
| Cache hit/miss | INFO | cache_key_prefix, hit (true/false) |
| Authentication event | INFO | user_id, event_type (sign_in/sign_up/sign_out) |
| Subscription event | INFO | user_id, event_type, plan_name |
| Error occurred | ERROR | error_type, error_message, stack_trace, request_id |

### 3.2 Never Log

| Data | Reason |
|---|---|
| Full JWT tokens | Security — token theft risk |
| Raw user passwords | Supabase handles auth; we never see passwords |
| Full email addresses | PII — mask as `r***@example.com` |
| Full phone numbers | PII — mask as `+91****1234` |
| Credit card numbers | PCI compliance (Stripe handles directly) |
| Full location history | Privacy — log only city names, not coordinates |
| AI conversation content | Privacy — log metadata only (message count, topic) |
| API keys | Security — never, ever |

---

## 4. Request ID Tracing

Every request entering the system receives a unique `request_id`:

1. Generated at the **Next.js BFF layer** as `req_{uuid4()}`
2. Passed to FastAPI via `X-Request-ID` header
3. Included in every log entry within that request's scope
4. Returned to client in response header `X-Request-ID`
5. If user reports an issue, support asks for the request ID from browser DevTools

This enables **end-to-end request tracing** across:
- Next.js API route logs
- FastAPI application logs
- LangGraph agent logs
- External API call logs
- Database query logs

---

## 5. Log Shipping

```
FastAPI (Python logging) → JSON formatter → stdout → Railway log collector → Datadog Log Intake
Next.js (console.log) → Vercel log drain → Datadog Log Intake
```

### 5.1 Python Logging Configuration

```python
# Structured JSON logging setup (structlog)
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
```

---

## 6. Log Retention

| Log Type | Retention | Storage |
|---|---|---|
| Application logs (INFO+) | 30 days in Datadog; 90 days in S3 archive | Datadog + S3 |
| Error logs (ERROR+) | 90 days in Datadog | Datadog |
| Audit logs | 12 months in PostgreSQL | PostgreSQL `audit_logs` table |
| AI agent logs | 30 days | Datadog |
| Access logs | 30 days | Datadog |

---

## 7. Log-Based Alerts

| Alert | Log Query | Threshold |
|---|---|---|
| High error rate | `level:ERROR service:travelmate-api` | > 50 per 5-min window |
| AI hallucination detected | `message:"hallucination detected"` | > 0 (any occurrence) |
| External API down | `message:"external API failure" api_name:*` | > 10 per minute for same API |
| Slow query | `message:"slow query" duration_ms:>1000` | > 5 per minute |
