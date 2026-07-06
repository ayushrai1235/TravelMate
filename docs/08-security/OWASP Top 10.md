# OWASP Top 10.md

# TravelMate AI — OWASP Top 10 Mitigations

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

This document maps TravelMate AI's architecture against the OWASP Top 10 (2021) to ensure comprehensive vulnerability mitigation.

---

## 2. Mitigations

### A01:2021-Broken Access Control
- **Risk:** User A accessing User B's trips.
- **Mitigation:** The FastAPI backend strictly enforces ownership checks (`trip.user_id == current_user.id`) on all read/write operations via dependency injection. Supabase handles session invalidation.

### A02:2021-Cryptographic Failures
- **Risk:** Exposure of sensitive data in transit or at rest.
- **Mitigation:** TLS 1.3 enforced at the edge. HSTS header included. DB encrypted at rest. No passwords stored in our DB (delegated to Supabase).

### A03:2021-Injection
- **Risk:** SQL Injection or Prompt Injection.
- **Mitigation:** 
  - **SQL:** SQLAlchemy ORM used exclusively; parameterized queries prevent SQLi.
  - **Prompt:** System prompts use strict delimiters (`<context>...</context>`). AI Orchestrator validates user input against a Pydantic schema before passing it to the LLM.

### A04:2021-Insecure Design
- **Risk:** Business logic flaws (e.g., bypassing free tier limits).
- **Mitigation:** Rate limiting and tier checking enforced centrally via Redis. Threat modeling was conducted during the design phase (documented in `Security Architecture.md`).

### A05:2021-Security Misconfiguration
- **Risk:** Unnecessary ports open, default credentials.
- **Mitigation:** Infrastructure as Code (IaC) via Railway templates ensures consistent configuration. CI/CD runs misconfiguration scanners. No default accounts exist in production.

### A06:2021-Vulnerable and Outdated Components
- **Risk:** Vulnerabilities in npm or pip packages.
- **Mitigation:** GitHub Dependabot enabled. CI pipeline includes Snyk to block builds with critical CVEs.

### A07:2021-Identification and Authentication Failures
- **Risk:** Brute force attacks, credential stuffing.
- **Mitigation:** Delegated entirely to Supabase, which provides built-in brute-force protection, bot detection, and supports passwordless/MFA.

### A08:2021-Software and Data Integrity Failures
- **Risk:** CI/CD pipeline compromised, untrusted deserialization.
- **Mitigation:** GitHub Actions uses signed commits and strict permissions. No pickle deserialization used in Python (JSON only). Supabase and Stripe webhooks verify cryptographic signatures.

### A09:2021-Security Logging and Monitoring Failures
- **Risk:** Breach goes undetected.
- **Mitigation:** All API requests and auth events are logged centrally to Datadog. Alerts configured for spikes in 401/403 errors, rate limits, and 500 errors.

### A10:2021-Server-Side Request Forgery (SSRF)
- **Risk:** Attacker forces backend to request internal IPs.
- **Mitigation:** The backend only makes outbound requests to explicitly defined external APIs (Google, Gemini, RailwayAPI) using pre-configured base URLs. User-supplied URLs are never fetched by the backend.
