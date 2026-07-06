# Component Library.md

# TravelMate AI — Component Library

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Component Architecture

Components are organized in three tiers:

| Tier | Description | Example |
|---|---|---|
| **Primitives** | shadcn/ui base components; never modified directly | `Button`, `Card`, `Dialog`, `Input`, `Badge` |
| **Domain Components** | TravelMate-specific composed components | `LegCard`, `ConfidenceBadge`, `TempleCard` |
| **Page Components** | Full page layouts composed of domain components | `TripPlanner`, `ItineraryView`, `AdminDashboard` |

---

## 2. Primitive Components (shadcn/ui)

Installed via `npx shadcn-ui@latest add <component>`:

| Component | Installed | Usage |
|---|---|---|
| `Button` | ✅ | All interactive buttons |
| `Card` | ✅ | Leg cards, info cards |
| `Dialog` | ✅ | Modals (disambiguation, subscription) |
| `Input` | ✅ | Text inputs |
| `Label` | ✅ | Form labels |
| `Select` | ✅ | Dropdowns (time, class preference) |
| `Badge` | ✅ | Confidence badges, status labels |
| `Tabs` | ✅ | Mobile view switching (Timeline/Map/Budget) |
| `Sheet` | ✅ | Mobile slide-over panels (AI Chat) |
| `Skeleton` | ✅ | Loading states |
| `Toast` | ✅ | Notifications, confirmations |
| `Tooltip` | ✅ | Hover info on confidence scores |
| `Separator` | ✅ | Visual dividers |
| `Avatar` | ✅ | User profile |
| `DropdownMenu` | ✅ | User menu, settings |
| `ScrollArea` | ✅ | Chat message list |
| `Alert` | ✅ | Warning messages |
| `Calendar` | ✅ | Date picker |
| `Popover` | ✅ | Calendar popup |
| `Command` | ✅ | Location search with autocomplete |

---

## 3. Domain Components

### 3.1 LocationInput

**File:** `src/components/planner/LocationInput.tsx`

**Purpose:** Autocomplete text input for entering origin or destination locations.

**Props:**
| Prop | Type | Required | Description |
|---|---|---|---|
| `label` | string | Yes | "From" or "To" |
| `value` | string | Yes | Current text value |
| `onChange` | (value: string) => void | Yes | Text change handler |
| `onSelect` | (location: GeocodedLocation) => void | Yes | When autocomplete suggestion selected |
| `placeholder` | string | No | Input placeholder text |
| `showCurrentLocation` | boolean | No | Show "Use Current Location" button |

**States:**
| State | Display |
|---|---|
| Empty | Placeholder text + GPS button (if enabled) |
| Typing | Autocomplete dropdown with top 5 suggestions |
| Selected | Confirmed location name with ✓ icon |
| Error | Red border + "Location not found" message |
| Loading | Spinner in input while geocoding |

**Accessibility:**
- `role="combobox"` with `aria-expanded`, `aria-controls`
- Arrow keys navigate suggestions
- Enter selects highlighted suggestion
- Escape closes dropdown

---

### 3.2 LegCard

**File:** `src/components/itinerary/LegCard.tsx`

**Purpose:** Displays a single transport leg in the itinerary timeline.

**Props:**
| Prop | Type | Required | Description |
|---|---|---|---|
| `leg` | TransportLeg | Yes | Full leg data |
| `isHighlighted` | boolean | No | True when leg was recently modified |
| `showDetails` | boolean | No | Expanded or collapsed state |

**Visual Structure:**
```
┌──────────────────────────────────────┐
│ [Mode Icon] [Mode Name]  [ConfBadge] │
│                                      │
│ [Origin Name]          [Dep Time]    │
│     │                                │
│     │  [Duration Badge]              │
│     │                                │
│ [Destination Name]     [Arr Time]    │
│                                      │
│ [Cost Badge]  [Source Label]         │
│ [Notes — expandable]                 │
└──────────────────────────────────────┘
```

**Mode-specific styling:** Background tint and left border color match transport mode (Train = amber, Bus = emerald, etc.)

---

### 3.3 ConfidenceBadge

**File:** `src/components/shared/ConfidenceIndicator.tsx`

**Purpose:** Pill badge displaying data confidence level with tooltip.

**Props:**
| Prop | Type | Required |
|---|---|---|
| `level` | "HIGH" \| "MEDIUM" \| "LOW" | Yes |
| `source` | string | Yes |
| `timestamp` | string | No |

**Rendering:**
| Level | Color | Icon | Text |
|---|---|---|---|
| HIGH | Green badge | ✓ | "Confirmed" |
| MEDIUM | Amber badge | ⚠ | "Estimated" |
| LOW | Red badge | ! | "Verify locally" |

**Tooltip:** On hover, shows source and timestamp: "Source: RailwayAPI.in | Updated: 25 minutes ago"

---

### 3.4 TempleCard

**File:** `src/components/itinerary/TempleCard.tsx`

**Purpose:** Contextual card showing temple information when destination is a religious site.

**Props:**
| Prop | Type |
|---|---|
| `temple` | TempleData |

**Content Sections:**
1. Temple name + image (Cloudinary)
2. Opening hours (formatted with status: Open Now / Closed)
3. Puja/aarti schedule list
4. Darshan info (free vs paid, queue estimate)
5. Dress code
6. Photography policy
7. Data freshness badge
8. External links (Google Maps, official website)

---

### 3.5 WeatherCard

**File:** `src/components/itinerary/WeatherCard.tsx`

**Props:**
| Prop | Type |
|---|---|
| `forecasts` | WeatherForecast[] |
| `alerts` | WeatherAlert[] |

**Content:** Weather icon + temp + condition per day. Alert banner (red) if severe weather.

---

### 3.6 HotelCard

**File:** `src/components/itinerary/HotelCard.tsx`

**Props:**
| Prop | Type |
|---|---|
| `hotel` | HotelSuggestion |

**Content:** Hotel name, star rating, price/night, distance, veg food indicator, booking link button.

---

### 3.7 BudgetPanel

**File:** `src/components/itinerary/BudgetPanel.tsx`

**Props:**
| Prop | Type |
|---|---|
| `budget` | BudgetBreakdown |
| `showMode` | "summary" \| "detailed" |

**Content:**
- Per-leg cost row items
- Subtotals: Transport / Food / Accommodation
- Grand total range (min–max)
- Budget mode toggle

---

### 3.8 ChatPanel

**File:** `src/components/chat/ChatPanel.tsx`

**Props:**
| Prop | Type |
|---|---|
| `itineraryContext` | Itinerary |
| `onItineraryUpdate` | (updatedItinerary: Itinerary) => void |

**States:**
| State | Display |
|---|---|
| Empty | Welcome message + suggested questions |
| Active | Message list + input |
| Loading | Typing indicator (animated dots) |
| Error | Error message + retry button |

---

### 3.9 TripMap

**File:** `src/components/map/TripMap.tsx`

**Props:**
| Prop | Type |
|---|---|
| `legs` | TransportLeg[] |
| `center` | [number, number] |
| `zoom` | number |

**Features:**
- Mapbox GL JS interactive map
- Each leg drawn as colored polyline (color = transport mode)
- Markers at each transit point
- Click marker to see leg details in popup
- Zoom to fit entire route on load
- Dark mode map style support

---

### 3.10 EmptyState

**File:** `src/components/shared/EmptyState.tsx`

**Props:**
| Prop | Type |
|---|---|
| `icon` | React.ReactNode |
| `title` | string |
| `description` | string |
| `actionLabel` | string (optional) |
| `onAction` | () => void (optional) |

**Usage:** Displayed when no trips, no chat history, no saved trips. Provides illustration + CTA.

---

## 4. Component State Matrix

| Component | Empty | Loading | Loaded | Error | Offline |
|---|---|---|---|---|---|
| TripForm | ✅ (blank form) | N/A | ✅ (pre-filled) | ✅ (field errors) | ✅ (cached) |
| ItineraryTimeline | ✅ (no trip yet) | ✅ (skeleton) | ✅ (full data) | ✅ (error + retry) | ✅ (cached trip) |
| LegCard | N/A | ✅ (skeleton) | ✅ (full data) | ✅ (degraded leg) | ✅ (cached) |
| TripMap | ✅ (no route) | ✅ (loading tiles) | ✅ (full route) | ✅ (fallback msg) | ✅ (cached tiles) |
| ChatPanel | ✅ (welcome) | ✅ (typing dots) | ✅ (messages) | ✅ (error in chat) | ❌ (requires net) |
| TempleCard | ✅ (not found) | ✅ (skeleton) | ✅ (full data) | ✅ (ext links) | ✅ (cached) |
| WeatherCard | N/A | ✅ (skeleton) | ✅ (forecast) | ✅ (hidden) | ❌ |
| HotelCard | N/A | ✅ (skeleton) | ✅ (hotel data) | ✅ (hidden) | ❌ |
| BudgetPanel | N/A | ✅ (skeleton) | ✅ (breakdown) | ✅ (partial) | ✅ (cached) |
| EmergencyContacts | N/A | N/A | ✅ (always) | N/A | ✅ (cached) |
