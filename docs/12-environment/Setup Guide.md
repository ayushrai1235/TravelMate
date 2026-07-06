# Setup Guide.md

# TravelMate AI — Local Environment Setup

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Prerequisites

Ensure you have the following installed on your machine:
- **Node.js:** v20.x or higher
- **Python:** v3.12.x
- **Docker:** (Docker Desktop or Colima)
- **Git:** Latest version
- **Poetry:** For Python dependency management (`pip install poetry`)

---

## 2. Repository Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:travelmate-ai/travelmate.git
   cd travelmate
   ```

2. **Initialize Frontend:**
   ```bash
   cd apps/web
   npm install
   ```

3. **Initialize Backend:**
   ```bash
   cd apps/api
   poetry install
   ```

---

## 3. Environment Variables

We use different `.env` files for the frontend and backend. 
Copy the example files and ask your engineering lead for the development API keys.

**Frontend (`apps/web/.env.local`):**
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

**Backend (`apps/api/.env`):**
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/travelmate
REDIS_URL=redis://localhost:6379/0

# Auth
CLERK_SECRET_KEY=sk_test_...

# AI & APIs
GEMINI_API_KEY=AIzaSy...
GOOGLE_MAPS_API_KEY=AIzaSy...
RAILWAY_API_KEY=...
OPENWEATHER_API_KEY=...
```

---

## 4. Starting Infrastructure (Docker)

To run the PostgreSQL database and Redis locally:

```bash
cd apps/api
docker-compose up -d
```

Verify they are running:
```bash
docker ps
```

---

## 5. Database Migrations

Before starting the API, run the database migrations:

```bash
cd apps/api
poetry run alembic upgrade head
```

(Optional) Seed the database with local test data:
```bash
poetry run python scripts/seed_db.py
```

---

## 6. Running the Application

You need two terminal windows.

**Terminal 1 (Backend API):**
```bash
cd apps/api
poetry run uvicorn app.main:app --reload --port 8000
```
API will be available at `http://localhost:8000/docs`

**Terminal 2 (Frontend Web):**
```bash
cd apps/web
npm run dev
```
Web app will be available at `http://localhost:3000`

---

## 7. Troubleshooting

**Q: Database connection refused?**
A: Ensure Docker is running and you executed `docker-compose up -d`. Check if port 5432 is already in use by a local Postgres installation.

**Q: Supabase Auth failing locally?**
A: Ensure your `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is correct in `.env.local` and that you are accessing the app via `localhost:3000` (Supabase requires specific origins).

**Q: Alembic migrations throwing errors?**
A: Ensure your `DATABASE_URL` uses the `+asyncpg` driver locally (as defined in the `.env` example).
