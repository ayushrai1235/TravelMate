# Navigation.md

# TravelMate AI — Navigation Architecture

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Route Structure

| Route | Page | Auth Required | Tier Required |
|---|---|---|---|
| `/` | Landing page | No | None |
| `/sign-in` | Clerk sign-in | No | None |
| `/sign-up` | Clerk sign-up | No | None |
| `/planner` | Trip planner | No (3 free) | Free |
| `/trips` | Trip history | Yes | Free |
| `/trips/[id]` | Single trip view | Yes | Free |
| `/chat` | AI chat | Yes | Free (5 msgs) |
| `/emergency` | Emergency contacts | No | None |
| `/profile` | User profile | Yes | Free |
| `/settings` | App settings | Yes | Free |
| `/admin` | Admin dashboard | Yes (admin role) | Admin |

---

## 2. Desktop Navigation

### 2.1 Top Navbar (all pages)

```
[Logo] TravelMate AI    [Planner] [My Trips] [AI Chat]    [🔔] [👤 UserMenu]
```

- Logo links to `/` (landing) or `/planner` (if authenticated)
- Active page highlighted with primary color bottom border
- Notification bell shows unread count badge
- User menu dropdown: Profile, Settings, Subscription, Sign Out

### 2.2 App Sidebar (planner page only)

On the planner page (`/planner`), a collapsible left sidebar provides:
- Trip input form
- Filters (budget mode, accessibility)
- Contextual info toggles (weather, temple, hotels)

---

## 3. Mobile Navigation

### 3.1 Bottom Tab Bar (persistent, all app pages)

```
┌──────────────────────────────────┐
│  🏠      📋       🗺️      🚨     ⚙️  │
│ Home   Trips    Plan   SOS   More │
└──────────────────────────────────┘
```

| Tab | Icon | Route | Notes |
|---|---|---|---|
| Home | `Home` | `/` or `/planner` | Landing or planner based on auth state |
| Trips | `ClipboardList` | `/trips` | Badge shows saved trip count |
| Plan | `Map` | `/planner` | Primary action — slightly larger icon |
| SOS | `ShieldAlert` | `/emergency` | Always red; always accessible |
| More | `MoreHorizontal` | Sheet menu | Opens: Profile, Chat, Settings, Sign Out |

### 3.2 Mobile Header

```
[← Back]  [Page Title]  [Action Button]
```

- Back button on all pages except root
- Action button is context-specific: Chat icon on planner, Edit on profile

### 3.3 Swipe Gestures

| Gesture | Action | Context |
|---|---|---|
| Swipe left on trip card | Delete trip | Trip history |
| Swipe right | N/A | — |
| Pull down | Refresh data | Planner, trips |

---

## 4. Navigation Transitions

| Transition | Animation | Duration |
|---|---|---|
| Page → Page | Fade + slide up (150ms) | 200ms |
| Open modal | Scale up from center + backdrop fade | 250ms |
| Close modal | Fade out + scale down | 200ms |
| Open sheet (mobile) | Slide up from bottom | 300ms |
| Close sheet | Slide down | 250ms |
| Tab switch | Crossfade | 150ms |

---

## 5. Deep Linking

All routes are directly addressable URLs for:
- Sharing trip links: `https://travelmate.ai/trips/trip_abc123`
- SEO landing pages: `https://travelmate.ai/planner?from=navsari&to=trimbakeshwar`
- PWA launch: Opens last active route

---

## 6. Protected Route Strategy

```
Next.js Middleware (middleware.ts)
├── Check Clerk session
├── If not authenticated + route requires auth:
│   └── Redirect to /sign-in?redirect_url=[current_path]
├── If authenticated + route is /sign-in:
│   └── Redirect to /planner
├── If route is /admin + user is not admin:
│   └── Redirect to /planner (no error shown)
└── All other routes: Allow
```

**Implementation:** Clerk's `clerkMiddleware()` with `createRouteMatcher()` for protected paths.
