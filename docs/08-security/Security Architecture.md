# Security Architecture.md

# TravelMate AI — Security Architecture

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Security Philosophy

1. **Zero Trust:** Do not trust the frontend. The BFF verifies the Supabase session; the FastAPI backend verifies the BFF request.
2. **Defense in Depth:** Multiple layers of security (WAF, Authentication, RBAC, DB constraints).
3. **Least Privilege:** Services, agents, and database roles only have access to what they explicitly need.
4. **Data Minimization:** Only collect PII that is absolutely necessary for travel planning.

---

## 2. Infrastructure Security

### 2.1 Network Layer
- All traffic over HTTPS (TLS 1.3). HTTP requests are strictly redirected to HTTPS at the edge.
- **Vercel Edge:** Acts as a Web Application Firewall (WAF) blocking basic volumetric DDoS attacks.
- **Backend Isolation:** FastAPI runs on Railway. It exposes a single public endpoint, but all requests MUST include a valid Next.js BFF signature or Supabase JWT. Database port is NOT exposed publicly.

### 2.2 Environment Segregation
- **Development:** Local environments connect to local DBs or isolated staging resources.
- **Staging:** Replicates production but uses mock data. No production customer data is ever copied to staging without anonymization.
- **Production:** Strictly isolated. SSH access to production containers is disabled.

---

## 3. Application Security

### 3.1 Authentication (AuthN)
Managed entirely by Supabase.
- Multi-factor authentication (MFA) supported.
- Passwordless login (OTP) preferred to eliminate credential stuffing risks.
- Session tokens are stored in `HttpOnly`, `Secure`, `SameSite=Lax` cookies.

### 3.2 Authorization (AuthZ)
- **Role-Based Access Control (RBAC):** Users are assigned roles (e.g., `user`, `admin`) in Supabase.
- **Resource Ownership:** The FastAPI backend enforces that a user can only read/modify trips where `trip.user_id == current_user.id`.

```python
# FastAPI Dependency
async def get_current_user_trip(
    trip_id: UUID, 
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Trip:
    trip = await db.execute(select(Trip).where(Trip.id == trip_id))
    if trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return trip
```

### 3.3 AI Security

- **Prompt Injection Defense:** 
  - System prompts clearly delineate instructions from user input.
  - The orchestrator validates all user input against expected structures before passing it to agents.
- **Tool Isolation:** Agents can only access data through strictly defined tools. The LLM cannot execute arbitrary code or SQL queries.
- **PII Scrubbing:** The ChatAgent scrubs PII (phone numbers, full names) before sending chat history to the Gemini API.

---

## 4. Data Security

### 4.1 Data in Transit
- Encrypted via TLS 1.2+ for all client-to-server and server-to-server communication.
- External API calls (Google Maps, Stripe) are strictly over HTTPS.

### 4.2 Data at Rest
- PostgreSQL data volumes are encrypted at rest (managed by Railway / AWS underlying storage).
- Backups in S3 are encrypted using SSE-S3.

### 4.3 Secrets Management
- No secrets in source control.
- Secrets injected at runtime via environment variables managed in the Vercel and Railway dashboards.
- API keys (Google Maps, Stripe, Gemini) are rotated every 180 days.

---

## 5. Third-Party Integrations

- **Stripe:** TravelMate AI never touches credit card data. The frontend uses Stripe Elements, and backend only processes webhook events. PCI compliance is handled by Stripe.
- **Supabase:** Identity data is handled by Supabase.
- **Gemini:** We have a zero-data-retention agreement (API data is not used for model training).

---

## 6. Audit & Logging

- All authentication events, subscription changes, and administrative actions are logged in the `audit_logs` table.
- Logs are shipped to Datadog.
- Alerts configured for multiple failed login attempts or unauthorized access patterns.
