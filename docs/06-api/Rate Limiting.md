# Rate Limiting.md

# TravelMate AI — Rate Limiting Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

Rate limiting protects TravelMate AI from abuse, cost overruns (LLM tokens, Google Maps billing), and DDoS attacks. Rate limiting is enforced at two layers:
1. **Edge (Vercel):** IP-based DDoS and spam protection.
2. **Backend (FastAPI + Redis):** User-based business logic limits.

---

## 2. Limits by Endpoint

### 2.1 Trip Planning (`POST /v1/trips/plan`)

| Tier | Limit | Window | Action if Exceeded |
|---|---|---|---|
| Unauthenticated | 3 requests | Per month | 403 (Paywall) |
| Free | 3 requests | Per month | 403 (Paywall) |
| Explorer | 20 requests | Per month | 403 (Upgrade prompt) |
| Pro | 100 requests | Per month | 403 (Upgrade prompt) |
| Business | 500 requests | Per month | 403 (Contact sales) |
| ALL | 5 requests | Per minute | 429 (Cooldown) |

### 2.2 AI Chat (`POST /v1/chat`)

| Tier | Limit | Window | Action if Exceeded |
|---|---|---|---|
| Unauthenticated | 0 requests | N/A | 401 |
| Free | 10 messages | Per trip | 403 (Upgrade prompt) |
| Explorer | 50 messages | Per trip | 403 (Upgrade prompt) |
| Pro / Business | Unlimited* | N/A | *Subject to fair use |
| ALL | 10 requests | Per minute | 429 (Cooldown) |

### 2.3 General API Endpoints (`GET /v1/*`)

- **Limit:** 120 requests per minute per IP address.
- **Action:** 429 Too Many Requests.

---

## 3. Implementation (FastAPI + Redis)

We use a sliding window algorithm implemented via Redis and FastAPI middleware.

```python
# Redis Key format
# rate_limit:endpoint:{user_id_or_ip}:{timestamp_minute}

async def rate_limit_middleware(request: Request, call_next):
    client_id = request.headers.get("X-User-ID") or request.client.host
    endpoint = request.url.path
    
    # Check limit against Redis
    is_allowed = await redis_rate_limiter.check(client_id, endpoint)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later."
                }
            }
        )
        
    return await call_next(request)
```

---

## 4. HTTP Headers

When a request is rate-limited (429), the following headers are included in the response:

- `Retry-After`: Number of seconds to wait before retrying (e.g., `60`).
- `X-RateLimit-Limit`: The maximum number of requests allowed in the current window.
- `X-RateLimit-Remaining`: The number of requests remaining in the current window (0 when limited).
- `X-RateLimit-Reset`: UNIX timestamp when the limit resets.

---

## 5. Cost-Protection Circuit Breakers

In addition to per-user rate limiting, global circuit breakers protect against system-wide cost spikes:

1. **Gemini API Spend Limit:** If backend detects > $50 spend in 1 hour, it triggers a global circuit breaker. AI requests return `503 Service Unavailable` until manually reviewed by an admin.
2. **Google Maps Volume Limit:** If > 5,000 API calls in 1 hour, switch to Mapbox fallback automatically.
