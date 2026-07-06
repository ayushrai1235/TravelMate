# Error Codes.md

# TravelMate AI — API Error Codes

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Standard Error Format

All API errors return a JSON response in the following format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {} // Optional object with specific error details
  },
  "request_id": "req_abc123"
}
```

---

## 2. Client Errors (HTTP 4xx)

### 2.1 Validation Errors (400 Bad Request)

| Code | Message Example | Details Example |
|---|---|---|
| `VALIDATION_ERROR` | "Invalid request parameters" | `{"field": "travel_date", "issue": "must be in future"}` |
| `INVALID_LOCATION` | "Unrecognized location name" | `{"location": "XyzAbc"}` |
| `MALFORMED_JSON` | "Invalid JSON payload" | null |

### 2.2 Authentication & Authorization (401, 403)

| Code | HTTP | Message Example |
|---|---|---|
| `UNAUTHORIZED` | 401 | "Missing or invalid authentication token" |
| `SESSION_EXPIRED` | 401 | "Session has expired" |
| `FORBIDDEN` | 403 | "You do not have permission to perform this action" |
| `TIER_LIMIT_REACHED` | 403 | "Monthly trip limit reached for free tier" |

### 2.3 Resource Errors (404, 409)

| Code | HTTP | Message Example |
|---|---|---|
| `NOT_FOUND` | 404 | "Trip not found" |
| `CONFLICT` | 409 | "Resource state conflict" |

### 2.4 Rate Limiting (429)

| Code | HTTP | Message Example | Details |
|---|---|---|---|
| `RATE_LIMIT_EXCEEDED` | 429 | "Too many requests" | `{"retry_after": 60}` |
| `CONCURRENCY_LIMIT` | 429 | "Too many simultaneous AI requests" | `{"retry_after": 30}` |

---

## 5. Server Errors (HTTP 5xx)

### 5.1 Internal Errors (500)

| Code | HTTP | Message Example | Note |
|---|---|---|---|
| `INTERNAL_ERROR` | 500 | "An unexpected error occurred" | Details are NEVER exposed to client. Logged internally. |
| `DATABASE_ERROR` | 500 | "Database operation failed" | Mapped to INTERNAL_ERROR in prod. |

### 5.2 Upstream Errors (502, 503, 504)

| Code | HTTP | Message Example | Details |
|---|---|---|---|
| `AI_SERVICE_UNAVAILABLE` | 503 | "AI planning service is overloaded" | `{"provider": "gemini"}` |
| `TRANSPORT_API_FAILED` | 502 | "Failed to fetch transport data" | `{"provider": "railway_api"}` |
| `UPSTREAM_TIMEOUT` | 504 | "Request to upstream service timed out" | `{"provider": "google_maps"}` |

---

## 6. Frontend Handling Strategy

The Next.js frontend has a centralized `apiClient` (Axios wrapper) that intercepts errors:

1. **401 Unauthorized:** Automatically triggers Clerk re-authentication or redirects to `/sign-in`.
2. **403 TIER_LIMIT_REACHED:** Pops up the subscription modal.
3. **429 Rate Limit:** Automatically retries once with exponential backoff before showing an error toast.
4. **5xx Server Errors:** Shows generic "Something went wrong" toast with the `request_id` for support.
5. **Validation Errors:** Maps `details` fields directly to form input errors.
