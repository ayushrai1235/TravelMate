# Wireframes.md

# TravelMate AI — Wireframes

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Purpose:** Detailed wireframe specifications for every screen. These wireframes define layout, content hierarchy, and component placement — NOT visual styling (see Design System.md for styling).

---

## Screen 1: Landing Page (`/`)

### Purpose
First impression. Convert visitors into users. Communicate value proposition instantly.

### Desktop Layout (>1024px)

```
┌────────────────────────────────────────────────────────┐
│ [Logo] TravelMate AI          [Features] [Pricing] [Login] │
├────────────────────────────────────────────────────────┤
│                                                        │
│              "From your doorstep                       │
│               to your destination."                    │
│                                                        │
│     ┌─────────────────────────────────────────┐       │
│     │ From: [_____________] 📍                 │       │
│     │ To:   [_____________] 📍                 │       │
│     │ Date: [__/__/____]  Time: [Morning ▼]   │       │
│     │          [🔍 Plan My Trip]               │       │
│     └─────────────────────────────────────────┘       │
│                                                        │
│  [Animated route illustration: Home→Station→Train→    │
│   Station→Bus→Temple with colored mode indicators]    │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  "How it works"                                        │
│  [1. Enter destination] [2. AI plans route] [3. Go!]  │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  "What makes us different"                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                │
│  │Door  │ │Real  │ │Confi-│ │Offline│                │
│  │to    │ │Data  │ │dence │ │Ready  │                │
│  │Door  │ │Only  │ │Scores│ │       │                │
│  └──────┘ └──────┘ └──────┘ └──────┘                │
│                                                        │
├────────────────────────────────────────────────────────┤
│  "Trusted by 10,000+ travelers"                       │
│  [Testimonial carousel]                                │
├────────────────────────────────────────────────────────┤
│  Pricing                                               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                │
│  │Free  │ │Explor│ │Pro   │ │Biz   │                │
│  │₹0    │ │₹99   │ │₹249  │ │₹999  │                │
│  └──────┘ └──────┘ └──────┘ └──────┘                │
├────────────────────────────────────────────────────────┤
│  [Footer: About | Privacy | Terms | Contact | Social] │
└────────────────────────────────────────────────────────┘
```

### Mobile Layout (<768px)

```
┌────────────────────────┐
│ [☰] TravelMate AI [👤] │
├────────────────────────┤
│                        │
│ "From your doorstep    │
│  to your destination." │
│                        │
│ From: [__________] 📍  │
│ To:   [__________] 📍  │
│ Date: [__/__/____]     │
│ Time: [Morning ▼]      │
│                        │
│ [🔍 Plan My Trip]      │
│  (full width button)   │
│                        │
│ [Animated illustration]│
│                        │
│ "How it works"         │
│ (vertical cards)       │
│                        │
│ "Features"             │
│ (vertical cards)       │
│                        │
│ [Pricing cards]        │
│ (horizontal scroll)    │
│                        │
├────────────────────────┤
│ [Bottom Nav:           │
│  Home | Plan | Trips   │
│  | Emergency | More]   │
└────────────────────────┘
```

---

## Screen 2: Trip Planner (`/planner`)

### Purpose
Core planning interface. User enters trip details and views the AI-generated itinerary.

### Desktop Layout (3-column)

```
┌────────────────────────────────────────────────────────────┐
│ [Logo]  [← Back]  Trip Planner              [👤 Profile]   │
├─────────┬──────────────────────────────┬───────────────────┤
│ SIDEBAR │       MAIN CONTENT           │    MAP PANEL      │
│ (280px) │       (flexible)             │    (400px)        │
│         │                              │                   │
│ Trip    │  ┌────────────────────────┐  │  ┌─────────────┐ │
│ Form:   │  │ ITINERARY TIMELINE     │  │  │             │ │
│         │  │                        │  │  │   Mapbox     │ │
│ From:   │  │ Leg 1: 🚗 Auto        │  │  │   Map View   │ │
│ [____]  │  │ Home → Navsari Station │  │  │             │ │
│         │  │ 07:00 - 07:20 (20min)  │  │  │  [colored   │ │
│ To:     │  │ ₹50-80 | ⚠ MEDIUM     │  │  │   route     │ │
│ [____]  │  │                        │  │  │   lines]    │ │
│         │  │ ---- Transfer (15min) -│  │  │             │ │
│ Date:   │  │                        │  │  │             │ │
│ [____]  │  │ Leg 2: 🚂 Train       │  │  │             │ │
│         │  │ Navsari → Nashik Road  │  │  │             │ │
│ Time:   │  │ 07:45 - 12:30 (4h45m) │  │  │             │ │
│ [____]  │  │ ₹180 | ✓ HIGH         │  │  │             │ │
│         │  │                        │  │  │             │ │
│ [Replan]│  │ ---- Transfer (15min) -│  │  │             │ │
│         │  │                        │  │  │             │ │
│ ──────  │  │ Leg 3: 🚌 Bus         │  │  │             │ │
│ Filters:│  │ Nashik Rd → Trimbak   │  │  │             │ │
│ Budget  │  │ 12:45 - 13:45 (60min) │  │  │             │ │
│ Mode □  │  │ ₹40-55 | ⚠ MEDIUM    │  │  └─────────────┘ │
│         │  │                        │  │                   │
│ ──────  │  │ Leg 4: 🚶 Walking     │  │  CONTEXTUAL CARDS │
│ Context:│  │ Trimbak BS → Temple   │  │  ┌─────────────┐ │
│ Weather │  │ 13:45 - 14:00 (15min) │  │  │ 🌧️ Weather   │ │
│ Temple  │  │ 0km | ✓ HIGH          │  │  │ 32°C, Rain  │ │
│ Hotels  │  │                        │  │  └─────────────┘ │
│ Budget  │  └────────────────────────┘  │  ┌─────────────┐ │
│         │                              │  │ 🛕 Temple    │ │
│         │  BUDGET PANEL                │  │ Open 5:30-21│ │
│         │  ┌────────────────────────┐  │  └─────────────┘ │
│         │  │ Transport: ₹270-315   │  │  ┌─────────────┐ │
│         │  │ Food est:  ₹150-400   │  │  │ 🏨 Hotels    │ │
│         │  │ TOTAL:     ₹420-715   │  │  │ From ₹800/n │ │
│         │  └────────────────────────┘  │  └─────────────┘ │
│         │                              │                   │
│         │  [📥 Download] [💬 AI Chat]  │                   │
├─────────┴──────────────────────────────┴───────────────────┤
│  [Emergency 🚨]                                            │
└────────────────────────────────────────────────────────────┘
```

### Mobile Layout (single column)

```
┌────────────────────────┐
│ [←] Trip Planner  [💬] │
├────────────────────────┤
│ From: [Navsari      📍]│
│ To:   [Trimbakeshwar📍]│
│ Date: [15 Jul 2026]    │
│ Time: [Morning ▼]      │
│ [🔍 Plan My Trip]      │
├────────────────────────┤
│                        │
│ ┌────── TABS ────────┐ │
│ │[Timeline] [Map]    │ │
│ │[Budget] [Info]     │ │
│ └────────────────────┘ │
│                        │
│ TIMELINE TAB:          │
│ ┌────────────────────┐ │
│ │ 🚗 Auto            │ │
│ │ Home → Station     │ │
│ │ 07:00-07:20        │ │
│ │ ₹50-80 ⚠ MEDIUM   │ │
│ └────────────────────┘ │
│     │ Transfer 15min   │
│ ┌────────────────────┐ │
│ │ 🚂 Train           │ │
│ │ Navsari → Nashik   │ │
│ │ 07:45-12:30        │ │
│ │ ₹180 ✓ HIGH        │ │
│ └────────────────────┘ │
│     │ Transfer 15min   │
│ ┌────────────────────┐ │
│ │ 🚌 Bus             │ │
│ │ Nashik → Trimbak   │ │
│ │ 12:45-13:45        │ │
│ │ ₹40-55 ⚠ MEDIUM   │ │
│ └────────────────────┘ │
│     │                  │
│ ┌────────────────────┐ │
│ │ 🚶 Walking         │ │
│ │ Bus Stand → Temple │ │
│ │ 13:45-14:00        │ │
│ │ 0km ✓ HIGH         │ │
│ └────────────────────┘ │
│                        │
│ [📥 Download PDF]      │
│                        │
├────────────────────────┤
│ 🏠 | 📋 | 🗺️ | 🚨 | ⚙️  │
└────────────────────────┘
```

---

## Screen 3: AI Chat (`/chat` or slide-over panel)

### Purpose
Conversational interface for itinerary Q&A and modification.

### Layout

```
┌────────────────────────────┐
│ [←] AI Chat        [X]    │
├────────────────────────────┤
│                            │
│  ┌──────────────────────┐  │
│  │ 🤖 Hi! I'm your      │  │
│  │ TravelMate AI.        │  │
│  │ I've planned your     │  │
│  │ Navsari → Trimbak     │  │
│  │ trip. Ask me anything! │  │
│  └──────────────────────┘  │
│                            │
│         ┌──────────────┐   │
│         │ What platform │   │
│         │ does my train  │   │
│         │ depart from?   │   │
│         └──────────────┘   │
│                            │
│  ┌──────────────────────┐  │
│  │ 🤖 Train 11057       │  │
│  │ departs from          │  │
│  │ Platform 2 at         │  │
│  │ Navsari station.      │  │
│  │                       │  │
│  │ ⚠️ MEDIUM confidence  │  │
│  │ Source: RailwayAPI     │  │
│  │ (cached 25 min ago)   │  │
│  │                       │  │
│  │ 💡 Check NTES app     │  │
│  │ on day of travel for  │  │
│  │ confirmed platform.   │  │
│  └──────────────────────┘  │
│                            │
├────────────────────────────┤
│ [🎤] [Type a message... ] [→] │
└────────────────────────────┘
```

---

## Screen 4: Emergency (`/emergency`)

```
┌──────────────────────────────┐
│ 🚨 EMERGENCY CONTACTS        │
├──────────────────────────────┤
│                              │
│ ┌──────────────────────────┐ │
│ │ 🚔 Police          100  │ │
│ │               [📞 Call]  │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ 🚑 Ambulance       108  │ │
│ │               [📞 Call]  │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ 🚒 Fire            101  │ │
│ │               [📞 Call]  │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ 🚆 Railway Police  1512 │ │
│ │               [📞 Call]  │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ 👩 Women Helpline  1091 │ │
│ │               [📞 Call]  │ │
│ └──────────────────────────┘ │
│                              │
│ ── Nearby Services ──        │
│ 📍 Nearest Police Station    │
│    Navsari Town PS (1.2km)   │
│    [Navigate →]              │
│                              │
│ 📍 Nearest Hospital          │
│    Civil Hospital (0.8km)    │
│    [Navigate →]              │
│                              │
│ Works offline ✓              │
└──────────────────────────────┘
```

---

## Screen 5: Profile (`/profile`)

```
┌────────────────────────────────┐
│ [←]  My Profile         [✏️]  │
├────────────────────────────────┤
│                                │
│   [Avatar]                     │
│   Rameshbhai Patel             │
│   ramesh@example.com           │
│   Explorer Plan (Active)       │
│                                │
│ ── Home Address ──             │
│ [123, Gandhi Road, Navsari...] │
│                                │
│ ── Travel Preferences ──       │
│ Preferred class: Sleeper [▼]   │
│ Budget tier:     Mid     [▼]   │
│ Accessibility:   Senior  [✓]   │
│                                │
│ ── Subscription ──             │
│ Plan: Explorer (₹99/month)    │
│ Next billing: Aug 3, 2026     │
│ [Manage Subscription]          │
│                                │
│ ── Trip History ──             │
│ ┌────────────────────────────┐ │
│ │ Navsari → Trimbakeshwar    │ │
│ │ Jul 15, 2026 | 4 legs      │ │
│ │ [View] [Download]          │ │
│ └────────────────────────────┘ │
│ ┌────────────────────────────┐ │
│ │ Navsari → Somnath          │ │
│ │ Jun 20, 2026 | 3 legs      │ │
│ │ [View] [Download]          │ │
│ └────────────────────────────┘ │
│                                │
│ [🗑️ Delete Account]           │
│                                │
└────────────────────────────────┘
```

---

## Screen 6: Admin Dashboard (`/admin`)

```
┌──────────────────────────────────────────────────────────┐
│ [Logo] TravelMate AI — Admin                 [👤 Admin]  │
├──────────┬───────────────────────────────────────────────┤
│ SIDEBAR  │  Dashboard Overview                          │
│          │                                               │
│ Overview │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐       │
│ Users    │  │MAU   │ │Trips │ │MRR   │ │Error │       │
│ Trips    │  │12,450│ │3,200 │ │₹5.2L │ │0.3%  │       │
│ Revenue  │  └──────┘ └──────┘ └──────┘ └──────┘       │
│ Temples  │                                               │
│ AI Perf  │  ┌─────────────────────────────────────────┐ │
│ Errors   │  │ Trips Planned (Last 30 Days)             │ │
│ Audit    │  │ [Line chart]                             │ │
│          │  └─────────────────────────────────────────┘ │
│          │                                               │
│          │  ┌─────────────────────────────────────────┐ │
│          │  │ Top Routes                               │ │
│          │  │ 1. Mumbai → Pune          (2,450 plans) │ │
│          │  │ 2. Delhi → Agra           (1,890 plans) │ │
│          │  │ 3. Navsari → Trimbakeshwar (1,200 plans) │ │
│          │  └─────────────────────────────────────────┘ │
│          │                                               │
│          │  ┌─────────────────────────────────────────┐ │
│          │  │ AI Agent Performance                     │ │
│          │  │ Avg Response: 4.2s | Failure: 0.5%     │ │
│          │  └─────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────┘
```

---

## Screen States Summary

For every screen, these states must be designed:

| State | Behavior |
|---|---|
| **Empty** | First visit, no data. Show CTA and illustration. |
| **Loading** | Skeleton loader matching final layout structure. |
| **Loaded** | Full data displayed. |
| **Error** | Error message with retry button and alternative action. |
| **Offline** | Cached data shown with offline banner. |
| **Partial** | Some API calls failed; available data shown, failed sections show degraded state. |
