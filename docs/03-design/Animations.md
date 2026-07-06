# Animations.md

# TravelMate AI — Animations

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Library:** Framer Motion 11.x

---

## 1. Animation Principles

1. **Purpose:** Every animation must serve a purpose — guide attention, provide feedback, or communicate state.
2. **Performance:** Use `transform` and `opacity` only (GPU-composited). Never animate `width`, `height`, `top`, `left`.
3. **Accessibility:** All animations respect `prefers-reduced-motion`. When reduced motion is preferred, use instant state changes (no transition).
4. **Duration:** 150–300ms for UI feedback; 500–1000ms for illustrative/decorative animations.

---

## 2. Animation Catalog

### 2.1 Page Transitions

| Transition | Animation | Duration | Easing |
|---|---|---|---|
| Page enter | Fade in (0→1 opacity) + slide up (20px→0) | 250ms | `ease-out` |
| Page exit | Fade out (1→0 opacity) | 150ms | `ease-in` |

Framer Motion: `<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}`

### 2.2 Itinerary Loading

| Phase | Animation | Duration |
|---|---|---|
| Skeleton pulse | Background shimmer (light-to-dark sweep) | 1.5s loop |
| Progress messages | Fade swap between messages ("Checking trains...", "Fetching weather...") | 2s per message |
| Leg cards appear | Stagger children — each card fades in + slides up, 100ms delay between | 200ms per card |

### 2.3 Route Map Drawing

| Animation | Description | Duration |
|---|---|---|
| Route polyline | Animated dash offset draws the route from origin to destination | 1500ms |
| Leg transition | When moving to next leg, polyline color changes with 300ms crossfade | 300ms |
| Marker drop | Transport stop markers drop in with spring bounce | 400ms |

### 2.4 Card Interactions

| Interaction | Animation | Duration |
|---|---|---|
| Card hover (desktop) | Shadow lift + subtle scale (1.0 → 1.01) | 200ms |
| Card press | Scale down (1.0 → 0.98) | 100ms |
| Card expand | Height grows with content fade-in | 250ms |
| Card collapse | Height shrinks with content fade-out | 200ms |

### 2.5 Confidence Badge

| Animation | Description |
|---|---|
| HIGH badge | Subtle green pulse on first render (attention-grabbing) |
| LOW badge | Gentle red pulse (2 cycles) to draw attention to risk |
| Tooltip appear | Fade + scale from badge origin point | 150ms |

### 2.6 AI Chat

| Element | Animation |
|---|---|
| User message send | Slide in from right + fade | 200ms |
| AI response appear | Slide in from left + fade, staggered by sentence | 200ms |
| Typing indicator | Three dots bouncing in sequence | 600ms loop |
| Chat panel open | Slide in from right (desktop) or up (mobile) | 300ms |

### 2.7 Notification Toast

| Animation | Description | Duration |
|---|---|---|
| Enter | Slide in from top-right + fade | 300ms |
| Stay | Static (no animation) | 4000ms |
| Exit | Slide out to right + fade | 200ms |

### 2.8 Emergency Button

| Animation | Description |
|---|---|
| Idle | Subtle pulse (opacity 0.9 → 1.0 → 0.9) every 3 seconds |
| Press | Scale down (0.95) + red flash | 100ms |

### 2.9 Landing Page Hero

| Element | Animation |
|---|---|
| Tagline text | Typewriter effect — characters appear one by one | 2000ms |
| Route illustration | Animated SVG — dotted line draws from "Home" to "Temple" | 3000ms |
| Transport mode icons | Pop in sequentially along the route line | 200ms each, staggered |

---

## 3. Reduced Motion Mode

When `prefers-reduced-motion: reduce` is detected:

| Default Animation | Reduced Motion Alternative |
|---|---|
| Slide + fade transitions | Instant state change (no animation) |
| Skeleton shimmer | Static gray placeholder |
| Route polyline draw | Polyline shown immediately (no drawing animation) |
| Card hover lift | No transform; only border color change |
| Typing indicator | Static "..." text |
| Landing typewriter | All text shown immediately |
| Emergency button pulse | Static button (no pulse) |

Implementation: Check `useReducedMotion()` hook from Framer Motion. All `motion.*` components receive `transition={{ duration: 0 }}` when reduced motion is preferred.

---

## 4. Performance Guidelines

| Guideline | Rule |
|---|---|
| Animatable properties only | Only `transform` (translate, scale, rotate) and `opacity` |
| No layout thrashing | Never animate `width`, `height`, `margin`, `padding` |
| GPU acceleration | Use `will-change: transform` on animated elements (sparingly) |
| Limit concurrent animations | Max 5 simultaneous animations on screen |
| Frame budget | All animations must maintain 60fps on mid-range Android device |
| Stagger delays | Use 50–100ms stagger; never 0ms (causes jank) |
