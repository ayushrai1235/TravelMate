# Data Privacy.md

# TravelMate AI — Data Privacy & Compliance

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Compliance Framework

TravelMate AI is designed to comply with the **Digital Personal Data Protection (DPDP) Act 2023 (India)**.

### 1.1 Core Principles
1. **Consent:** Clear, affirmative consent required before collecting home address or tracking location.
2. **Purpose Limitation:** Travel data is only used for planning trips, not sold to third-party advertisers.
3. **Data Minimization:** We only collect name, email, home address, and travel dates.
4. **Data Residency:** All databases and backups are hosted in AWS `ap-south-1` (Mumbai) via Railway/Vercel.

---

## 2. PII Data Handling

### 2.1 What We Collect
| Data Point | Purpose | Storage |
|---|---|---|
| Name & Email | Account creation, communications | Clerk + PostgreSQL |
| Home Address | Default origin for trips | PostgreSQL (`user_preferences`) |
| Current Location (GPS) | "Plan from here" feature | Never stored; used ephemerally in browser |
| Travel Routes | Core service | PostgreSQL (`trip_plans`) |

### 2.2 Right to Erasure (Account Deletion)

Users can delete their account from the `/profile` page.

**Deletion Flow:**
1. User requests deletion.
2. Webhook triggers `UserAccountDeleted` event.
3. Stripe subscription is immediately cancelled.
4. User record in PostgreSQL is soft-deleted (`deleted_at` = NOW()).
5. User is immediately logged out and Clerk identity is deleted.
6. A background task runs after 72 hours to permanently anonymize the data:
   - `email` → `deleted_user_{uuid}`
   - `full_name` → `Deleted User`
   - `home_address` → NULL
   - Associated trips are kept for aggregate analytics, but stripped of user identity.

### 2.3 Right to Access (Data Export)

Users can request an export of their data via the profile page.
The system generates a JSON file containing their profile, preferences, and complete trip history, provided as a download link valid for 24 hours.

---

## 3. Third-Party Data Sharing

We share data with third parties *only* to fulfill the core service. We have signed DPAs (Data Processing Agreements) with these vendors.

| Vendor | Data Shared | Purpose |
|---|---|---|
| Clerk | Email, Name | Authentication |
| Stripe | Email | Billing |
| Google Gemini | Origin, Destination, Dates | AI trip planning |
| Google Maps | Origin/Dest text strings | Geocoding |

**Critical AI Rule:** User email, name, and exact home street address (house number) are NEVER sent to the Gemini API. The BFF scrubs exact addresses to just the neighborhood/city level before passing to the AI orchestrator.

---

## 4. Privacy by Design Features

1. **Incognito Mode / Free Trial:** Users can plan up to 3 trips without creating an account. The data is tied only to a transient session cookie, not an identity.
2. **Location Spoofing Prevention:** The app does not rely on continuous background location tracking. GPS is only requested explicitly when the user clicks the "Use Current Location" button.
3. **Notification Control:** Users have granular toggles for promotional emails, transactional emails, and push notifications. Delay alerts are opt-in per trip.
