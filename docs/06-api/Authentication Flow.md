# Authentication Flow.md

# TravelMate AI — Authentication Flow

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Identity Provider

TravelMate AI uses **Supabase** as the Identity Provider (IdP) for all authentication and user management. We do not store passwords or manage MFA logic ourselves.

---

## 2. Authentication Architecture

### 2.1 Component Responsibilities

1. **Supabase Hosted UI / SDK:** Handles login, signup, OTP, OAuth (Google), and password resets.
2. **Next.js Middleware:** Checks session cookies for page routing protection at the edge.
3. **Next.js BFF (API Routes):** Extracts the Supabase JWT, validates it, and proxies the request to FastAPI with an `X-User-ID` header.
4. **FastAPI Backend:** Trusts the `X-User-ID` header (because the BFF is the only entry point) or validates the Supabase JWT directly for defense-in-depth.

---

## 3. Flows

### 3.1 Sign In / Sign Up Flow (Frontend)

1. User clicks "Sign In" on Next.js frontend.
2. Next.js redirects to Supabase's Hosted UI (or renders Supabase `<SignIn />` component).
3. User authenticates via Google OAuth or Email + OTP.
4. Supabase issues a session cookie (`__session`) to the browser.
5. Supabase redirects back to TravelMate AI `/planner`.

### 3.2 Backend Request Flow (BFF Pattern)

When the user makes an API request from the browser:

1. Browser sends `POST /api/trips/plan` to Next.js BFF (includes `__session` cookie automatically).
2. Next.js API route uses Supabase SDK: `const { userId } = auth();`
3. If `userId` is missing, return `401 Unauthorized`.
4. If valid, Next.js attaches the user ID to the FastAPI request:
   ```javascript
   fetch('https://api.railway.internal/v1/trips/plan', {
     headers: { 'X-User-ID': userId }
   });
   ```
5. FastAPI middleware reads `X-User-ID`.
6. FastAPI request context is populated with the user ID for downstream services.

### 3.3 Defense-in-Depth (FastAPI JWT Validation)

For enhanced security (in case the FastAPI service is ever exposed directly), FastAPI can validate the Supabase JWT directly:

1. Next.js passes the Supabase JWT token in the `Authorization: Bearer <token>` header.
2. FastAPI uses `PyJWT` to fetch Supabase's JWKS (JSON Web Key Set).
3. FastAPI verifies the token signature, audience, and expiration.

---

## 4. User Synchronization

Since Supabase holds the identity data, but we need user data in our PostgreSQL database for foreign keys (trips, preferences), we sync via Webhooks.

1. User signs up in Supabase.
2. Supabase sends `user.created` webhook to TravelMate AI.
3. FastAPI creates a row in the `users` table:
   ```sql
   INSERT INTO users (id, email, full_name, subscription_tier)
   VALUES ('user_2aB...', 'test@example.com', 'Test User', 'free');
   ```
4. FastAPI creates a row in the `user_preferences` table with defaults.

---

## 5. Unauthenticated Usage (Free Trial)

TravelMate AI allows unauthenticated users to plan up to 3 trips.

**Mechanism:**
1. Unauthenticated request hits `/api/trips/plan`.
2. Next.js BFF generates an anonymous session ID and sets an HTTP-only cookie.
3. Next.js passes `X-Anon-Session-ID` to FastAPI.
4. FastAPI uses Redis to track trip count for that session ID.
5. If trip count >= 3, FastAPI returns `403 TIER_LIMIT_REACHED`.
6. Frontend prompts user to sign up.

*Note: If the anonymous user signs up, their trip history is NOT automatically migrated to their new account in v1.0.*
