# Error Handling.md

# TravelMate AI — Error Handling Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Error Handling Philosophy

TravelMate AI follows these principles for error handling:

1. **Never leave the user stranded.** Every error must provide a next step or alternative.
2. **Distinguish user errors from system errors.** Don't apologize for a user typo; don't blame the user for a server crash.
3. **Graceful degradation over hard failure.** A partial result with clear labels is better than an error screen.
4. **Transparency about confidence.** If data is uncertain or unavailable, say so explicitly.
5. **Log everything; expose nothing sensitive.** Full error context in logs; sanitized messages to users.
6. **Fail fast at boundaries; recover late.** Validate at input; catch at service boundaries.

---

## 2. Error Classification

### 2.1 Severity Levels

| Level | Code | Description | User Impact | Response |
|---|---|---|---|---|
| **P0 — Critical** | 500, 503 | Service completely down | Cannot use app | PagerDuty immediate alert |
| **P1 — High** | AI agent failure, DB failure | Core feature broken | Cannot plan trip | PagerDuty 5-min alert |
| **P2 — Medium** | External API failure | Partial functionality lost | Degraded itinerary | Slack alert, next business hour fix |
| **P3 — Low** | Optional feature failure | Minor inconvenience | Weather unavailable, etc. | Logged; backlog ticket |
| **P4 — Info** | User input errors, validation | No system fault | User sees helpful message | Logged only |

---

## 3. Error Categories and Handling

### 3.1 HTTP Error Codes (API)

| Code | Meaning | User Message | Engineering Action |
|---|---|---|---|
| 400 Bad Request | Invalid input parameters | "Please check your input and try again." | Log + return validation details |
| 401 Unauthorized | Missing/invalid JWT | Redirect to login | Log auth failure |
| 403 Forbidden | Valid JWT but insufficient permissions | "You don't have access to this feature." | Log access attempt |
| 404 Not Found | Resource doesn't exist | "We couldn't find what you're looking for." | Log |
| 422 Unprocessable Entity | Valid JSON but invalid business logic | Specific validation errors returned | Log |
| 429 Too Many Requests | Rate limit exceeded | "You're making too many requests. Please wait a moment." | Log; return Retry-After header |
| 500 Internal Server Error | Unhandled exception | "Something went wrong on our end. We're working on it." | PagerDuty alert; full error in logs |
| 503 Service Unavailable | Service overloaded or down | "TravelMate AI is temporarily unavailable. Please try again in a few minutes." | PagerDuty immediate |

### 3.2 AI Agent Errors

| Error Type | Detection | Behavior |
|---|---|---|
| LLM API timeout (> 30s) | httpx timeout | Retry up to 3x with backoff; fall back to rule-based |
| LLM rate limit | 429 from Google Gemini | Exponential backoff; queue request |
| Malformed LLM response | JSON parse failure | Re-prompt once; if fails, return error with suggestion to retry |
| Context window exceeded | Token count > limit | Summarize context and retry; if still fails, plan in segments |
| Tool call failure | Transport API returns error | Use cached data or fallback; label affected leg with LOW confidence |
| Hallucination detected | Confidence validator rejects output | Discard output; return error "AI could not generate a valid plan. Try again." |

### 3.3 External API Errors

| API | Error | Retry Strategy | Fallback |
|---|---|---|---|
| Google Maps Geocoding | 429 / 500 | Exponential backoff (3 retries) | Mapbox Geocoding |
| Google Maps Distance Matrix | 429 / 500 | Exponential backoff | Estimate from straight-line distance × 1.3 factor |
| RailwayAPI (Trains) | 500 / timeout | Retry 2x; 5s timeout | Show "Schedule unavailable — check IRCTC" |
| GTFS Bus feeds | Parse error / 404 | Try next available feed | Google Transit API |
| Amadeus Flights | 401 / 500 | Re-auth + retry | Show "Flight search unavailable" |
| OpenWeatherMap | 500 / timeout | Retry once | Hide weather widget gracefully |
| Supabase Auth | 500 | Retry twice | Show "Auth service temporarily down" |
| Stripe | 500 | Retry; Stripe has high reliability | "Payment processing unavailable — try again" |

---

## 4. Frontend Error Handling

### 4.1 Error Boundary Strategy

React Error Boundaries wrap all major page sections:

```
App Root
├── GlobalErrorBoundary (catches everything)
│   ├── Layout (nav, footer)
│   └── PageContent
│       ├── TripPlannerErrorBoundary
│       │   ├── SearchForm
│       │   └── ItineraryDisplay
│       ├── MapErrorBoundary
│       │   └── MapView
│       └── ChatErrorBoundary
│           └── AIChatPanel
```

**Behavior per boundary:**
- `TripPlannerErrorBoundary`: Shows "Trip planner encountered an error. [Retry] [Contact Support]"
- `MapErrorBoundary`: Shows "Map unavailable. [View text itinerary instead]"
- `ChatErrorBoundary`: Shows "AI chat unavailable. Your itinerary is still displayed above."
- `GlobalErrorBoundary`: Full-page error with "Return to Home" button

### 4.2 Network Error Handling (React Query)

All API calls use React Query with:
- `retry: 3` for read operations
- `retry: 1` for mutations
- `onError` callback logs to Sentry
- Error states render specific error components per query type

### 4.3 Form Validation Errors

| Scenario | Display Method |
|---|---|
| Empty required field | Inline error under field on submit |
| Invalid location | "We couldn't find this location" inline |
| Date in past | "Please select a future date" inline |
| API returns 422 | Field-level errors mapped from API response |

---

## 5. Backend Error Handling

### 5.1 FastAPI Global Exception Handler

```python
# Error handler structure (not implementation)
@app.exception_handler(RequestValidationError)
→ Returns 422 with field-level validation errors in standard format

@app.exception_handler(HTTPException)  
→ Returns standard HTTP error with error code + user message

@app.exception_handler(ExternalAPIError)
→ Logs full error; returns 503 with user-friendly message

@app.exception_handler(Exception)
→ Logs full traceback to Datadog; returns 500 with generic message
→ Triggers PagerDuty if error rate > 1%
```

### 5.2 Standard Error Response Format

All API errors return this JSON structure:

```json
{
  "error": {
    "code": "TRAIN_SCHEDULE_UNAVAILABLE",
    "message": "Train schedule data is currently unavailable for this route.",
    "user_message": "We couldn't retrieve train schedules right now. Please check IRCTC directly or try again.",
    "suggestion": "Check IRCTC for train availability: https://www.irctc.co.in",
    "retry_after_seconds": 30,
    "request_id": "req_abc123",
    "timestamp": "2026-07-03T14:00:00Z"
  }
}
```

**Fields:**
- `code`: Machine-readable error code for frontend to map to specific UI
- `message`: Technical description (for logs/debugging)
- `user_message`: Safe, friendly message shown to user
- `suggestion`: Actionable next step for the user
- `retry_after_seconds`: When to retry (null if not applicable)
- `request_id`: For correlating with server logs in support

### 5.3 Error Codes Reference

| Code | HTTP Status | Meaning |
|---|---|---|
| INVALID_LOCATION | 400 | Location could not be geocoded |
| AMBIGUOUS_LOCATION | 400 | Multiple locations match; disambiguation needed |
| SAME_ORIGIN_DESTINATION | 400 | Origin and destination are same |
| NO_ROUTE_FOUND | 404 | No transport route exists between points |
| TRAIN_SCHEDULE_UNAVAILABLE | 503 | Train API failure |
| BUS_ROUTE_NOT_FOUND | 404 | No bus route data available |
| WEATHER_UNAVAILABLE | 503 | Weather API failure |
| AI_PLAN_FAILED | 500 | LLM failed to generate valid plan |
| RATE_LIMIT_EXCEEDED | 429 | User has exceeded request limit |
| SUBSCRIPTION_REQUIRED | 402 | Feature requires paid subscription |
| TRIP_LIMIT_REACHED | 402 | Free tier trip limit reached |
| AUTH_REQUIRED | 401 | Authentication required |
| UNAUTHORIZED | 403 | Insufficient permissions |
| INTERNAL_ERROR | 500 | Unhandled server error |

---

## 6. AI Agent Error Handling

### 6.1 Retry Strategy

```
Attempt 1: Call LLM with full context
    └── Failure → Wait 1 second
Attempt 2: Retry with simplified context
    └── Failure → Wait 3 seconds  
Attempt 3: Retry with minimal prompt
    └── Failure → Activate fallback
Fallback: Rule-based route planning from cached data
    └── Return partial plan with LOW confidence labels
```

### 6.2 Confidence Validator

After every AI agent response, a confidence validator runs:

1. **Schema validation:** Response matches required JSON schema
2. **Data cross-reference:** Train numbers checked against RailwayAPI cache
3. **Logic validation:** Times are chronologically ordered; no negative durations
4. **Hallucination check:** Any transport entity not in data sources is flagged

If validation fails:
- Re-prompt AI with explicit: "The previous response had errors: [error list]. Please correct."
- If second attempt fails: return error to user

---

## 7. Logging and Monitoring

### 7.1 Log Levels

| Level | Usage | Example |
|---|---|---|
| DEBUG | Detailed flow tracing (dev only) | "RouteAgent: calling RailwayAPI with params..." |
| INFO | Normal business events | "Trip planned: user_id=123, route=Navsari→Nashik, duration=6h" |
| WARN | Non-critical issues | "GTFS feed for MSRTC is stale (48h); using cached data" |
| ERROR | Exceptions, API failures | "RailwayAPI returned 500; retrying..." |
| CRITICAL | System down, data breach | "Database connection lost; all writes failing" |

### 7.2 Sensitive Data in Logs

**NEVER log:**
- Full location history
- Payment card details (Stripe handles these; never touch raw card data)
- Auth tokens or session IDs in full
- User email or phone in unmasked form

**Safe to log:**
- User ID (hashed)
- City names (origin/destination)
- Error codes and messages
- Performance timings
- Request IDs

### 7.3 Alerting Rules

| Condition | Alert Channel | Response Time |
|---|---|---|
| Error rate > 1% (5-min window) | PagerDuty + Slack | 5 minutes |
| API P99 > 15 seconds | PagerDuty + Slack | 10 minutes |
| 0 successful trip plans in 5 minutes | PagerDuty | Immediate |
| Database replication lag > 30s | Slack | 30 minutes |
| AI API failure (all retries exhausted) | Slack | 30 minutes |
| Stripe webhook failures > 3 | Slack | 1 hour |
