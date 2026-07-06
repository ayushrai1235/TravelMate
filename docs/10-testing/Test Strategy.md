# Test Strategy.md

# TravelMate AI — Test Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Testing Pyramid

TravelMate AI follows a standard testing pyramid:
1. **Unit Tests (70%)**: Fast, isolated tests for utilities, formatters, and logic.
2. **Integration Tests (20%)**: Tests API endpoints and database interactions.
3. **E2E Tests (10%)**: Simulates real user flows in a browser.

---

## 2. Backend Testing (Python/FastAPI)

**Framework:** `pytest`

### 2.1 Unit Tests
- **Scope:** Domain models, data validation, utility functions.
- **Mocking:** All external APIs (RailwayAPI, Gemini, Google Maps) MUST be mocked using `unittest.mock` or `pytest-httpx`.
- **Location:** `apps/api/tests/unit/`

### 2.2 Integration Tests
- **Scope:** FastAPI endpoints, database repositories.
- **Database:** Uses an ephemeral PostgreSQL database spun up via Docker Compose during the test run.
- **Mocking:** External APIs are mocked, but DB and Redis are REAL.
- **Location:** `apps/api/tests/integration/`

### 2.3 AI Agent Evaluation (Specialized)
Testing LLM agents requires a different approach since outputs are non-deterministic.
- **Framework:** `langsmith` (for trace evaluation) + custom assertions.
- **Approach:** We define 50 "Golden Scenarios" (e.g., "Navsari to Trimbak on Monday").
- **Assertions:** Instead of exact string matching, we assert structural rules:
  ```python
  def test_train_agent_output_structure(mock_tools):
      result = train_agent.invoke({"origin": "NVS", "dest": "NK"})
      assert "legs" in result
      assert result["legs"][0]["mode"] == "TRAIN"
      assert result["legs"][0]["confidence"] == "HIGH" # Based on mock tool response
  ```

---

## 3. Frontend Testing (Next.js/React)

**Framework:** `Vitest` + `React Testing Library`

### 3.1 Component Tests
- **Scope:** Reusable UI components (buttons, cards, forms).
- **Assertions:** Renders correctly, fires correct events on click, displays validation errors.
- **Location:** `apps/web/src/components/__tests__/`

### 3.2 Page/Hook Tests
- **Scope:** Complex state management (Zustand) and custom React hooks.
- **Mocking:** Network requests mocked via MSW (Mock Service Worker).

---

## 4. End-to-End (E2E) Testing

**Framework:** `Playwright`

- **Scope:** Critical user journeys (Login, Plan a Trip, Save Trip).
- **Environment:** Runs against the `staging` environment.
- **Mocking:** Minimal. Uses a dedicated test user account.

**Key E2E Flow:**
1. Navigate to homepage.
2. Enter "Surat" to "Mumbai".
3. Select "Tomorrow".
4. Click "Plan Trip".
5. Assert loading state appears.
6. Assert final itinerary renders with at least one transport leg.

---

## 5. Performance Testing

**Framework:** `k6`

- **Execution:** Run manually before major releases, targeting staging environment.
- **Metrics:** Ensure P95 latency remains under 8 seconds for 100 concurrent users.

```javascript
// k6 script example
import http from 'k6/http';
import { check } from 'k6';

export const options = { vus: 10, duration: '30s' };

export default function () {
  const res = http.get('https://staging-api.travelmate.ai/health/ready');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```
