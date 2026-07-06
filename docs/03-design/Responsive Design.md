# Responsive Design.md

# TravelMate AI — Responsive Design

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Breakpoints

| Name | Range | Target Devices |
|---|---|---|
| `mobile` | 0–767px | Phones (portrait) |
| `tablet` | 768–1023px | Tablets, phones (landscape) |
| `desktop` | 1024–1439px | Laptops, desktops |
| `wide` | 1440px+ | Large monitors |

Tailwind config:
```
screens: {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1440px',
}
```

---

## 2. Layout Patterns by Breakpoint

### 2.1 Trip Planner Page

| Breakpoint | Layout |
|---|---|
| Mobile | Single column. Form at top → itinerary below → tabs for map/budget/info |
| Tablet | Two columns. Form+itinerary (60%) \| Map (40%) |
| Desktop | Three columns. Sidebar form (280px) \| Itinerary (flex) \| Map+context (400px) |
| Wide | Same as desktop, max-width 1440px centered |

### 2.2 Landing Page

| Breakpoint | Layout |
|---|---|
| Mobile | Stacked vertical. Hero → form → features (1 col) → pricing (scroll) |
| Tablet | Hero + form centered. Features 2-col grid. Pricing 2-col. |
| Desktop | Hero with form side-by-side. Features 4-col. Pricing 4-col. |

### 2.3 Trip History

| Breakpoint | Layout |
|---|---|
| Mobile | Single column trip cards, full width |
| Tablet | 2-column grid of trip cards |
| Desktop | 3-column grid of trip cards |

---

## 3. Component Responsive Behavior

### 3.1 Navigation

| Breakpoint | Behavior |
|---|---|
| Mobile | Bottom tab bar (5 items). Hamburger menu for additional items. |
| Tablet | Top navbar with all items visible. No bottom bar. |
| Desktop | Top navbar with all items. User dropdown menu. |

### 3.2 Trip Map

| Breakpoint | Behavior |
|---|---|
| Mobile | Full-width map accessed via "Map" tab. Height: 60vh. |
| Tablet | Right column, 40% width. Sticky position. |
| Desktop | Right column, 400px fixed width. Sticky position. |

### 3.3 AI Chat

| Breakpoint | Behavior |
|---|---|
| Mobile | Full-screen sheet sliding up from bottom (95vh) |
| Tablet | Right side panel, 400px width |
| Desktop | Right side panel, 400px width, collapsible |

### 3.4 Itinerary Legs

| Breakpoint | Behavior |
|---|---|
| Mobile | Full-width cards, stacked vertically with connector line |
| Tablet | Same as mobile but with more horizontal space for details |
| Desktop | Full-width within main content column, with expanded detail view |

### 3.5 Budget Panel

| Breakpoint | Behavior |
|---|---|
| Mobile | Accessible via "Budget" tab, full-width |
| Tablet | Below itinerary, full-width |
| Desktop | Below itinerary in main column, two-column layout (legs \| total) |

---

## 4. Typography Scaling

| Element | Mobile | Tablet | Desktop |
|---|---|---|---|
| Hero heading | 30px (text-3xl) | 36px (text-4xl) | 48px (text-5xl) |
| Page title | 24px (text-2xl) | 24px | 30px (text-3xl) |
| Section heading | 20px (text-xl) | 20px | 24px (text-2xl) |
| Body text | 16px (text-base) | 16px | 16px |
| Secondary text | 14px (text-sm) | 14px | 14px |
| Caption | 12px (text-xs) | 12px | 12px |

---

## 5. Image and Asset Handling

| Asset Type | Mobile | Tablet | Desktop |
|---|---|---|---|
| Hero image | 1x (640w) | 2x (1024w) | 2x (1440w) |
| Icons | 24px | 24px | 24px |
| Map tiles | Standard DPI | Standard DPI | Retina DPI |
| Temple images | 320w thumbnail | 480w | 640w |

All images via Cloudinary with automatic responsive format:
```html
<img src="https://res.cloudinary.com/.../w_auto,c_scale/temple.jpg" />
```

---

## 6. Touch vs. Pointer Behavior

| Interaction | Touch (Mobile) | Pointer (Desktop) |
|---|---|---|
| Location autocomplete | Tap to select | Click or Enter |
| Map interaction | Pinch zoom, pan | Scroll zoom, drag |
| Leg card details | Tap to toggle | Hover to preview, click to expand |
| Confidence badge info | Tap shows tooltip | Hover shows tooltip |
| Swipe to delete trip | Swipe left | Delete icon on hover |

---

## 7. Progressive Web App (PWA)

### 7.1 PWA Manifest

```json
{
  "name": "TravelMate AI",
  "short_name": "TravelMate",
  "description": "AI-powered door-to-door travel planning for India",
  "start_url": "/planner",
  "display": "standalone",
  "theme_color": "#3B82F6",
  "background_color": "#F9FAFB",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### 7.2 Service Worker Strategy

| Resource | Strategy | Rationale |
|---|---|---|
| App shell (HTML, CSS, JS) | Cache first, network fallback | Fast initial load |
| API responses | Network first, cache fallback | Fresh data preferred |
| Map tiles | Cache first (for visited areas) | Offline map support |
| Images | Cache first | Reduce bandwidth |
| Emergency data | Cache first (pre-cached on install) | Must work offline |
