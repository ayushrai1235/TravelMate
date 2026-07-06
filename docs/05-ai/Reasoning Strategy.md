# Reasoning Strategy.md

# TravelMate AI — Reasoning Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Overview

The AI reasoning strategy defines HOW the system makes decisions when planning a trip. This is not about what data to fetch (that's tool-calling), but about how to combine data into coherent, optimal plans.

---

## 2. Reasoning Modes

### 2.1 Tool-Augmented Reasoning

The primary reasoning mode. The LLM reasons by:
1. Analyzing the user's request (origin, destination, date, preferences)
2. Calling tools to retrieve real data (trains, buses, weather)
3. Interpreting tool results to construct a plan
4. Combining multiple data sources into a coherent itinerary

**Key principle:** The LLM NEVER reasons about transport specifics from its training data. All transport claims come from tool calls.

### 2.2 Rule-Based Reasoning (Fallback)

When the LLM is unavailable or produces invalid output, a deterministic rule-based system takes over:

```
Input: origin_coords, dest_coords, date

1. Calculate straight-line distance
2. Find nearest railway station to origin (cached data)
3. Find nearest railway station to destination (cached data)
4. Look up cached train schedules between stations
5. Estimate first-mile (auto: distance * ₹15/km)
6. Estimate last-mile (auto: distance * ₹15/km)
7. Combine into itinerary
```

---

## 3. Decision Making Framework

### 3.1 Transport Mode Selection

```
given: origin, destination, distance, user_preferences

if distance < 2km:
    → WALK
elif distance < 5km:
    → AUTO (or WALK if user prefers budget)
elif distance < 50km:
    → Check BUS availability
    → If no bus: AUTO
elif distance < 300km:
    → Check TRAIN availability
    → First/last mile: AUTO
    → If no train: BUS (inter-city)
elif distance < 800km:
    → Check TRAIN availability
    → Check FLIGHT availability
    → Choose based on user preference:
        → speed: FLIGHT
        → budget: TRAIN
        → comfort: TRAIN (2A/1A)
else (>800km):
    → Prefer FLIGHT
    → TRAIN (overnight) as alternative
    → First/last mile: AUTO/CAB
```

### 3.2 Train Selection Logic

When multiple trains are available:

```
Priority 1: Runs on the requested date
Priority 2: Departs within ±2 hours of user's preferred time
Priority 3: User's preferred class is available
Priority 4: Shortest travel time
Priority 5: Fewest stops
```

### 3.3 Transfer Buffer Calculation

```
Train → Bus:  15 minutes minimum + (5 min walking to bus stand if different location)
Train → Train: 30 minutes minimum (different station), 15 minutes (same station)
Bus → Walk:   5 minutes buffer
Flight → Cab: 30 minutes (airport exit + cab wait)
Any → Any:    MAX(mode_minimum_buffer, walking_time_between_points + 5 min)
```

### 3.4 Cost Estimation Logic

| Mode | Estimation Method | Confidence |
|---|---|---|
| Train | Fixed fare from Railway API (class-specific) | HIGH |
| Bus | GTFS fare if available; else ₹1.5-2/km estimate | MEDIUM/LOW |
| Auto | Google Distance Matrix → ₹15/km base + ₹30 base fare | MEDIUM |
| Cab | Google Distance Matrix → ₹12/km base + ₹50 base fare | MEDIUM |
| Flight | Amadeus API fare | HIGH |
| Walking | ₹0 | HIGH |
| Metro | GTFS fare data | HIGH |

---

## 4. Multi-Objective Optimization

When generating alternatives (fastest, cheapest, most comfortable), the system optimizes across:

| Objective | Metric | Optimization |
|---|---|---|
| Fastest | Total door-to-door time (minutes) | Minimize |
| Cheapest | Total cost (INR) | Minimize |
| Comfortable | Number of transfers + total walking distance | Minimize |

These are NOT Pareto-optimal in general — the system produces three distinct plans, each optimized for one objective.

---

## 5. Context-Aware Reasoning

### 5.1 Time-of-Day Awareness

```
if departure_time is between 22:00 and 05:00:
    → Prefer overnight trains (sleeper class)
    → Warn: "Limited local transport available late night"
    → Suggest auto/cab for first mile instead of bus

if arrival at destination is after 20:00:
    → Warn: "Arriving late. Temple may be closed."
    → Suggest nearby hotel for overnight stay
```

### 5.2 Season and Festival Awareness

```
if travel_date is during Maha Shivaratri AND destination is Shiva temple:
    → Warning: "Very high crowds expected"
    → Suggest arriving before 5 AM for darshan
    → Hotels likely fully booked — show warning

if travel_date is during monsoon (June-September) AND destination is Western Ghats:
    → Weather warning: Heavy rainfall likely
    → Road travel may be disrupted
    → Train preferred over bus (safer in rain)
```

### 5.3 Accessibility-Aware Reasoning

```
if group contains senior citizens:
    → Prefer trains with lower berth availability (SL/3A)
    → Reduce maximum walking distance to 500m
    → Prefer direct routes (fewer transfers)
    → Prioritize wheelchair-accessible hotels

if group contains children:
    → Prefer AC classes (comfort for children)
    → Add food stop suggestions at each transfer point
    → Suggest child-friendly POIs en route
```
