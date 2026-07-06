# Scalability.md

# TravelMate AI — Scalability Plan

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Scale Targets

| Phase | Concurrent Users | Requests/sec | Database Size | Redis Memory |
|---|---|---|---|---|
| v1.0 Launch | 1,000 | 50 | < 10 GB | 256 MB |
| v1.5 (Month 6) | 10,000 | 200 | 50 GB | 512 MB |
| v2.0 (Month 12) | 100,000 | 2,000 | 500 GB | 2 GB |

---

## 2. Horizontal Scaling

### 2.1 Frontend (Vercel)
- Vercel auto-scales Next.js serverless functions globally
- Edge Functions run at 30+ PoPs worldwide
- No manual scaling required
- CDN caches static assets automatically

### 2.2 Backend (Railway)
- Railway supports horizontal auto-scaling based on CPU/memory metrics
- FastAPI pods are completely stateless — scale from 1 to N with no code changes
- Auto-scale trigger: CPU > 70% sustained for 5 minutes → add pod
- Scale-down: CPU < 30% sustained for 15 minutes → remove pod
- Minimum pods: 2 (high availability)
- Maximum pods: 10 (budget-constrained for v1.0)

### 2.3 Celery Workers
- Workers scale independently from API pods
- Scale trigger: Queue depth > 100 tasks → add worker
- Dedicated workers for AI tasks (higher memory allocation)

---

## 3. Vertical Scaling

| Component | v1.0 | v2.0 | Scaling Trigger |
|---|---|---|---|
| FastAPI pod | 1 vCPU, 1 GB RAM | 2 vCPU, 4 GB RAM | P99 > 15 seconds |
| PostgreSQL | 2 vCPU, 4 GB RAM | 4 vCPU, 16 GB RAM | Query time P99 > 1 second |
| Redis | 1 vCPU, 512 MB | 2 vCPU, 2 GB | Memory usage > 80% |
| Celery worker | 1 vCPU, 2 GB RAM | 2 vCPU, 4 GB RAM | Task backlog > 500 |

---

## 4. Database Scaling

### 4.1 Read Replicas
- Add read replicas for query-heavy operations (trip history, search)
- Application routes reads to replicas via SQLAlchemy bind configurations
- Writes always go to primary

### 4.2 Connection Pooling
- SQLAlchemy connection pool: min 10, max 100 connections
- PgBouncer for external connection pooling if needed beyond max

### 4.3 Table Partitioning (v2.0)
- `trip_plans` table partitioned by `created_at` (monthly partitions)
- `notifications` table partitioned by `scheduled_at`
- `audit_logs` table partitioned by `created_at` (monthly, with automatic old partition archival)

### 4.4 Indexing Strategy
See `07-database/Indexes.md` for complete index definitions.

---

## 5. AI Agent Scaling

### 5.1 Token Budget Management
- Per-request token limit: 8,000 tokens (input + output)
- Per-user daily token limit: 50,000 tokens (Pro), 200,000 (Business)
- Circuit breaker: If Gemini API error rate > 5% in 1 minute, pause new requests for 30 seconds

### 5.2 AI Request Queue
At high load, AI planning requests enter a Redis-backed FIFO queue:
- Queue size limit: 500 pending requests
- Queue position communicated to user: "Your trip is #X in queue. Estimated wait: ~Y seconds."
- If queue full: "Our AI is very busy right now. Please try again in a few minutes."

### 5.3 Response Caching
- Identical trip queries within 30 minutes return cached results (no AI invocation)
- Cache hit rate target: ≥ 70% for popular routes

---

## 6. CDN and Static Asset Scaling

| Asset | CDN | Strategy |
|---|---|---|
| Next.js pages | Vercel Edge | ISR (Incremental Static Regeneration) for landing pages |
| JS/CSS bundles | Vercel Edge | Immutable cache (content-hashed filenames) |
| Map tiles | Mapbox CDN | Globally distributed tile servers |
| Images | Cloudinary CDN | Auto-format (WebP), auto-resize |

---

## 7. Load Testing Targets

| Scenario | Load | Duration | Success Criteria |
|---|---|---|---|
| Normal load | 100 concurrent users | 30 minutes | P95 < 8s, 0% errors |
| Peak load | 1,000 concurrent users | 15 minutes | P95 < 12s, < 1% errors |
| Stress test | 5,000 concurrent users | 10 minutes | Graceful degradation; no crash |
| Soak test | 500 concurrent users | 4 hours | No memory leaks; stable P95 |
