# CI-CD Pipeline.md

# TravelMate AI — CI/CD Pipeline

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

TravelMate AI uses **GitHub Actions** for Continuous Integration (CI) and a combination of Vercel and Railway for Continuous Deployment (CD).

**Goals:**
1. Block broken code from merging to `main`.
2. Ensure automated testing covers both frontend and backend.
3. Automate zero-downtime deployments.

---

## 2. Branching Strategy

- `main`: Production-ready code. Commits here automatically deploy to production.
- `staging`: Pre-production environment for final QA.
- `feature/*`: Developer branches.

**Workflow:**
1. Developer creates `feature/add-weather-agent`.
2. Developer opens PR against `staging`.
3. CI runs on PR.
4. Merge to `staging` → Deploys to Staging Environment.
5. QA validates Staging.
6. Open PR from `staging` to `main`.
7. Merge to `main` → Deploys to Production Environment.

---

## 3. Continuous Integration (CI)

Triggered on: Pull Requests to `main` or `staging`.

### 3.1 Backend CI Job (FastAPI)
1. **Setup:** Checkout code, setup Python 3.12.
2. **Linting:** Run `ruff check .` and `ruff format --check .`
3. **Type Checking:** Run `mypy .`
4. **Testing:** 
   - Start ephemeral PostgreSQL and Redis using Docker Compose.
   - Run `pytest` with coverage.
   - Fail if coverage drops below 80%.
5. **Security:** Run `bandit -r .` for Python security issues.

### 3.2 Frontend CI Job (Next.js)
1. **Setup:** Checkout code, setup Node.js 20.
2. **Install:** `npm ci`
3. **Linting:** `npm run lint` (ESLint + Prettier).
4. **Type Checking:** `npm run type-check` (tsc).
5. **Testing:** `npm run test` (Vitest for unit/components).
6. **Build Test:** `npm run build` (Ensures Next.js compiles successfully).

---

## 4. Continuous Deployment (CD)

Triggered on: Push to `main` (Production) or `staging` (Staging).

### 4.1 Frontend CD (Vercel)
Vercel is natively integrated with GitHub.
1. Vercel detects push to `main`.
2. Vercel builds the Next.js app.
3. Vercel deploys globally to the Edge Network.
4. Vercel automatically handles cache invalidation for updated assets.

### 4.2 Backend CD (Railway)
Railway is natively integrated with GitHub.
1. Railway detects push to `main`.
2. **Phase 1: Build.** Railway uses the `Dockerfile` to build the API container.
3. **Phase 2: Database Migration.** Railway runs the pre-deploy command: `alembic upgrade head`.
4. **Phase 3: Rollout.** Railway spins up new containers, waits for health checks (`/health/ready`) to pass, then routes traffic to the new containers and shuts down the old ones (Zero Downtime).

---

## 5. Environment Variables

Secrets are NOT stored in GitHub. 
- GitHub Actions only has access to test keys.
- Production environment variables are managed securely within the Vercel (Frontend) and Railway (Backend) dashboards.
