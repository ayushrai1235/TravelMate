# Infrastructure.md

# TravelMate AI — Infrastructure as Code

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

TravelMate AI uses Platform-as-a-Service (PaaS) providers to minimize infrastructure management overhead. We do not use Terraform or Kubernetes for v1.0. Instead, infrastructure is defined via configuration files native to Vercel and Railway.

---

## 2. Infrastructure Providers

| Component | Provider | Region | Rationale |
|---|---|---|---|
| **Frontend App** | Vercel | Global Edge | Best-in-class Next.js support, zero-config CDN |
| **Backend API** | Railway | ap-south-1 (Mumbai) | Easy Docker deployments, auto-scaling, DB managed |
| **PostgreSQL** | Railway | ap-south-1 (Mumbai) | Fully managed, automated backups |
| **Redis** | Railway | ap-south-1 (Mumbai) | Low latency to backend API |
| **DNS / Domain** | Cloudflare | Global | DDoS protection, strict SSL, fast propagation |
| **Blob Storage** | AWS S3 | ap-south-1 (Mumbai) | Backups, PDF storage |

---

## 3. Configuration Files

### 3.1 `railway.json` (Backend Infrastructure)

Defines the build and deploy instructions for Railway.

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "apps/api/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4",
    "healthcheckPath": "/health/ready",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 3.2 `vercel.json` (Frontend Infrastructure)

Defines routing and edge configurations for Vercel.

```json
{
  "framework": "nextjs",
  "regions": ["bom1"], 
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

---

## 4. Containerization (Docker)

The FastAPI backend is containerized for consistency across local development, staging, and production.

**`apps/api/Dockerfile`:**
```dockerfile
# Use official lightweight Python image
FROM python:3.12-slim as requirements-stage

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12-slim
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

# Run as non-root user for security
RUN useradd -m myuser
USER myuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
