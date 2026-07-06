# REST Guidelines.md

# TravelMate AI — REST API Guidelines

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Naming Conventions

1. **Resources are plural nouns:** `/trips`, `/users`, `/temples`
2. **Kebab-case for URLs:** `/trip-plans` (not `/tripPlans` or `/trip_plans`)
3. **Snake_case for JSON fields:** `{"trip_id": "123", "created_at": "..."}`
4. **No trailing slashes:** `/v1/trips` (not `/v1/trips/`)

---

## 2. HTTP Methods

| Method | Idempotent | Usage |
|---|---|---|
| `GET` | Yes | Retrieve resource(s). No side effects. |
| `POST` | No | Create new resource or initiate process (e.g., plan trip). |
| `PUT` | Yes | Completely replace a resource. |
| `PATCH` | No | Partially update a resource (e.g., change preference). |
| `DELETE`| Yes | Remove a resource. |

---

## 3. Standard Response Format

All responses follow a consistent envelope structure.

### 3.1 Success Response

```json
{
  "success": true,
  "data": { ... },
  "meta": { ... } // Optional: pagination, rate limits
}
```

### 3.2 Error Response

See `Error Codes.md` for full details.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid date format",
    "details": {
      "field": "travel_date",
      "expected": "YYYY-MM-DD"
    }
  },
  "request_id": "req_abc123"
}
```

---

## 4. Pagination

Collections use offset/limit pagination (cursor pagination reserved for v2.0).

**Query Parameters:**
- `limit`: Default 20, max 100
- `offset`: Default 0

**Response Meta Object:**
```json
"meta": {
  "total_count": 145,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

---

## 5. Filtering and Sorting

**Filtering:** Uses query parameters.
`GET /trips?status=completed&mode=train`

**Sorting:** Uses `sort` parameter. Prefix with `-` for descending.
`GET /trips?sort=-created_at,origin_name`

---

## 6. HTTP Status Codes

| Code | Usage |
|---|---|
| **200 OK** | Successful GET, PUT, PATCH |
| **201 Created** | Successful POST (resource created) |
| **202 Accepted** | Background task accepted (e.g., PDF generation) |
| **204 No Content** | Successful DELETE |
| **400 Bad Request** | Validation error (client error) |
| **401 Unauthorized** | Missing or invalid auth token |
| **403 Forbidden** | Authenticated, but lacks permission (e.g., Free tier limit hit) |
| **404 Not Found** | Resource doesn't exist |
| **429 Too Many Requests** | Rate limit exceeded |
| **500 Internal Server Error** | Unexpected server crash (log & alert) |
| **502 Bad Gateway** | Upstream API failure (e.g., RailwayAPI down) |
| **503 Service Unavailable** | Maintenance or overload |

---

## 7. Versioning

- Version is always in the URL path: `/v1/`
- Breaking changes require a new major version (`/v2/`)
- Non-breaking additions (new fields, new optional endpoints) do not change version
- Sunset period for old versions: 6 months minimum

---

## 8. Data Types and Formats

- **Dates:** ISO 8601 string (`YYYY-MM-DD`)
- **Timestamps:** ISO 8601 string with UTC Z offset (`YYYY-MM-DDThh:mm:ssZ`)
- **Currency:** Numeric minor units (e.g., paise) if exact, OR object `{"currency": "INR", "amount": 100}`
- **Coordinates:** Object `{"lat": 19.9386, "lng": 73.5302}`
- **Distance:** Meters (integer)
- **Duration:** Minutes (integer)
