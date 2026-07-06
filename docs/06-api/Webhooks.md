# Webhooks.md

# TravelMate AI — Webhooks

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

TravelMate AI consumes external webhooks to maintain system state (subscriptions, authentication). It does not currently emit webhooks to users.

All webhooks are received by the Next.js API Routes (BFF) which handles signature verification before forwarding the validated payload to the FastAPI backend.

---

## 2. Stripe Webhooks

**Endpoint:** `POST /api/webhooks/stripe`  
**Security:** Stripe-Signature header verification using `STRIPE_WEBHOOK_SECRET`

### 2.1 Handled Events

| Stripe Event | TravelMate Action |
|---|---|
| `checkout.session.completed` | Create/upgrade subscription, update user metadata |
| `customer.subscription.updated` | Update tier, period end date |
| `customer.subscription.deleted` | Downgrade to Free tier |
| `invoice.payment_failed` | Trigger notification to user |
| `invoice.paid` | Extend subscription period |

### 2.2 Processing Logic

1. Next.js route receives payload and `Stripe-Signature`
2. Uses Stripe Node.js SDK to construct event
3. If invalid signature: return `400 Bad Request`
4. If valid: forward JSON payload to FastAPI `POST /v1/webhooks/stripe`
5. FastAPI checks `processed_events` table for event ID (idempotency)
6. If already processed: return `200 OK`
7. If new: queue Celery task to process business logic, store event ID
8. Return `200 OK` to Next.js → Stripe

---

## 3. Supabase Webhooks

**Endpoint:** `POST /api/webhooks/supabase`  
**Security:** Svix signature verification using `CLERK_WEBHOOK_SECRET`

### 3.1 Handled Events

| Supabase Event | TravelMate Action |
|---|---|
| `user.created` | Create user record in PostgreSQL, initialize preferences |
| `user.updated` | Update email/name in PostgreSQL |
| `user.deleted` | Delete user record and all associated trips (hard delete) |
| `session.created` | Track active user count (analytics) |

### 3.2 Idempotency

Supabase webhooks may be delivered multiple times. The FastAPI endpoint must use the `id` from the payload to ensure operations (like user creation) are idempotent. `INSERT ... ON CONFLICT DO NOTHING`.

---

## 4. Local Development

To test webhooks locally:

**Stripe:**
```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

**Supabase:**
Use ngrok or LocalTunnel to expose port 3000, then configure the Supabase dashboard webhook endpoint to point to the ngrok URL.
