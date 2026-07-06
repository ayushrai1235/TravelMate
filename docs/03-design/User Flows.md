# User Flows.md

# TravelMate AI — User Flows

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## Flow 1: First-Time Trip Planning

```mermaid
flowchart TD
    A[User opens TravelMate AI] --> B{Authenticated?}
    B -->|No| C[Landing page shown]
    B -->|Yes| D[Redirect to /planner]
    C --> E[User enters origin + destination]
    E --> F[User selects date + time]
    F --> G[User clicks Plan My Trip]
    G --> H{Free trips remaining?}
    H -->|Yes| I[Loading state shown]
    H -->|No| J[Subscription paywall modal]
    J --> K{User subscribes?}
    K -->|Yes| L[Stripe Checkout]
    L --> M{Payment success?}
    M -->|Yes| I
    M -->|No| N[Payment error - retry]
    K -->|No| O[User dismisses - limited features]
    I --> P[AI agents process in parallel]
    P --> Q{All agents succeed?}
    Q -->|Yes| R[Full itinerary displayed]
    Q -->|Partial| S[Partial itinerary + degraded sections]
    Q -->|All fail| T[Error screen + retry button]
    R --> U{User satisfied?}
    U -->|Yes| V[Save / Download / Share]
    U -->|No| W[Open AI Chat for modifications]
    W --> X[ChatAgent modifies itinerary]
    X --> R
```

---

## Flow 2: Authentication

```mermaid
flowchart TD
    A[User clicks Sign In] --> B[Clerk sign-in modal opens]
    B --> C{Auth method?}
    C -->|Google OAuth| D[Google consent screen]
    D --> E{Consent granted?}
    E -->|Yes| F[Clerk creates session]
    E -->|No| G[Return to sign-in]
    C -->|Email OTP| H[User enters email]
    H --> I[OTP sent to email]
    I --> J[User enters OTP code]
    J --> K{OTP valid?}
    K -->|Yes| F
    K -->|No| L[Error: Invalid code - retry]
    L --> J
    F --> M{First-time user?}
    M -->|Yes| N[Welcome modal + preferences setup]
    N --> O[User sets home address + preferences]
    O --> P[Profile saved to PostgreSQL]
    M -->|No| Q[Load existing preferences]
    P --> R[Redirect to /planner]
    Q --> R
```

---

## Flow 3: Subscription Purchase

```mermaid
flowchart TD
    A[User hits free limit OR clicks Upgrade] --> B[Pricing modal shown]
    B --> C{User selects tier}
    C -->|Explorer ₹99| D[Selected plan: Explorer]
    C -->|Pro ₹249| E[Selected plan: Pro]
    C -->|Business ₹999| F[Selected plan: Business]
    D --> G[Create Stripe Checkout Session]
    E --> G
    F --> G
    G --> H[Redirect to Stripe Checkout]
    H --> I{Payment result?}
    I -->|Success| J[Stripe webhook: checkout.session.completed]
    J --> K[Backend updates user subscription in DB]
    K --> L[Clerk metadata updated with tier]
    L --> M[User redirected to /planner]
    M --> N[Full feature access enabled]
    I -->|Cancel| O[User returns to app - no change]
    I -->|Failure| P[Stripe shows error on checkout page]
    P --> Q[User retries or changes card]
    Q --> H
```

---

## Flow 4: AI Chat Modification

```mermaid
flowchart TD
    A[User opens AI Chat panel] --> B[Chat shows context: current itinerary]
    B --> C[User types or speaks a message]
    C --> D{Message type?}
    D -->|Question| E[ChatAgent searches itinerary context]
    E --> F{Answer in context?}
    F -->|Yes| G[Return answer with confidence]
    F -->|No| H[Return: Data not available + suggest official source]
    D -->|Modification| I[ChatAgent extracts modification intent]
    I --> J[Validate modification is feasible]
    J --> K{Feasible?}
    K -->|Yes| L[Re-invoke OrchestratorAgent for affected legs]
    L --> M[Updated legs replace old legs]
    M --> N[Changed legs highlighted in UI]
    N --> O[Chat confirms: Itinerary updated]
    K -->|No| P[Chat explains why not feasible + suggests alternative]
    D -->|General advice| Q[ChatAgent provides travel advice]
    Q --> R[Response shown with relevant context]
```

---

## Flow 5: Offline Download

```mermaid
flowchart TD
    A[User views itinerary] --> B[User clicks Download Offline]
    B --> C{Subscription tier?}
    C -->|Free| D[Upgrade prompt shown]
    C -->|Explorer+| E[Generate PDF]
    E --> F[PDF includes: all legs, timings, temple info, emergency contacts]
    F --> G[Browser downloads PDF]
    G --> H[Cache itinerary in IndexedDB]
    H --> I{Storage available?}
    I -->|Yes| J[Pre-cache map tiles for route area]
    J --> K[Toast: Trip saved for offline access ✓]
    I -->|No| L[Toast: PDF downloaded but offline cache failed - storage full]
```

---

## Flow 6: Emergency Access

```mermaid
flowchart TD
    A[User taps Emergency button] --> B[Emergency screen loads instantly]
    B --> C[Static emergency contacts displayed]
    C --> D{GPS permission?}
    D -->|Granted| E[Fetch nearest police station + hospital]
    E --> F[Display with distance + Navigate button]
    D -->|Denied| G[Show contacts only - no nearby services]
    F --> H{User taps Call?}
    H -->|Yes| I[Native phone dialer opens with number]
    H -->|No| J{User taps Navigate?}
    J -->|Yes| K[Google Maps opens with directions]
```

---

## Flow 7: Notification Lifecycle

```mermaid
flowchart TD
    A[User saves trip with future date] --> B[NotificationService creates scheduled notifications]
    B --> C[24h before: Celery task fires]
    C --> D{User has push notifications enabled?}
    D -->|Yes| E[Send PWA push notification]
    D -->|No| F[Send email notification]
    E --> G[2h before: second notification fires]
    F --> G
    G --> H[30min before: final notification fires]
    H --> I{Train delay detected?}
    I -->|Yes| J[Send delay alert with new ETA]
    J --> K{Delay breaks next connection?}
    K -->|Yes| L[Suggest revised connecting transport]
    K -->|No| M[Show updated time only]
    I -->|No| N[No additional notification]
```

---

## Flow 8: Return Trip Planning

```mermaid
flowchart TD
    A[User views completed outward itinerary] --> B[User clicks Plan Return Trip]
    B --> C[System pre-fills: origin = prev destination, dest = prev origin]
    C --> D[Date picker opens with next day selected]
    D --> E[User confirms or changes return date + time]
    E --> F[Standard trip planning flow executes]
    F --> G[Return itinerary generated]
    G --> H[Both trips linked as pair in trip history]
    H --> I[User can view outward + return side by side on desktop]
```
