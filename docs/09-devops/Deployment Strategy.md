# Deployment Strategy.md

# TravelMate AI — Deployment Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Deployment Environments

| Environment | URL | Purpose |
|---|---|---|
| **Local** | `localhost:3000` | Developer iteration |
| **Preview** | `*.vercel.app` | Ephemeral environments per PR |
| **Staging** | `staging.travelmate.ai` | Pre-production QA and final integration testing |
| **Production** | `travelmate.ai` | Live customer traffic |

---

## 2. Zero-Downtime Deployments

### 2.1 Backend (Railway)
Railway natively supports zero-downtime deployments via health checks.

1. New image is built.
2. New container spins up alongside the existing one.
3. Railway routes an internal health check to `GET /health/ready`.
4. If health check fails, the deployment aborts and the old container remains active.
5. If health check passes, Railway flips the internal router to point to the new container.
6. Existing requests on the old container are given 30 seconds to drain gracefully before the old container is killed.

### 2.2 Frontend (Vercel)
Vercel deployments are inherently zero-downtime. Assets are uploaded to the edge network, and a symlink-like pointer is instantly flipped once the build completes.

---

## 3. Database Migration Strategy

Database migrations are the biggest risk to zero-downtime deployments.

**Rule:** Deployments and database migrations must be decoupled logically, even if run in the same pipeline.

1. **Pre-deploy step:** Alembic applies migrations before new code is rolled out.
2. **Schema constraint:** Migrations must NOT drop tables, drop columns, or rename columns in a way that breaks the *currently running* version of the application.
3. **Phased rollout for breaking DB changes:**
   - Deploy 1: Add new column (nullable).
   - Deploy 2: Application writes to both old and new columns.
   - Deploy 3: Backfill data.
   - Deploy 4: Application reads/writes only to new column.
   - Deploy 5: Drop old column.

---

## 4. Rollback Procedure

If a critical bug is discovered in production:

1. **Frontend Bug:** In Vercel, click "Instant Rollback" to the previous deployment. (Takes < 5 seconds).
2. **Backend Bug (Code only):** In Railway, click "Rollback" on the previous successful deployment.
3. **Backend Bug (with DB changes):**
   - **DO NOT automatically roll back the code**, because the database schema has already changed and rolling back the code will cause the old code to crash against the new schema.
   - **Action:** Write a "roll-forward" fix (e.g., a hotfix branch) and deploy it immediately, OR manually revert the DB migration (if safe) and then rollback the code.

---

## 5. Preview Environments

Every Pull Request automatically generates a Vercel Preview URL.
- These connect to a shared staging database, NOT production.
- Allows PMs and Designers to review UI changes before merging to `main`.
