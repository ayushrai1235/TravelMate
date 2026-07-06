# Design System.md

# TravelMate AI — Design System

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Design Philosophy

TravelMate AI's design system is built on four pillars:

1. **Clarity** — Travel data is complex. The UI must make complexity simple.
2. **Trust** — Confidence indicators, source labels, and real data build user trust.
3. **Accessibility** — From 22-year-old students to 67-year-old pilgrims, the UI works for everyone.
4. **Delight** — Smooth animations and thoughtful micro-interactions make travel planning enjoyable.

---

## 2. Color Palette

### 2.1 Primary Colors

| Token | HSL | Hex | Usage |
|---|---|---|---|
| `--color-primary-50` | hsl(215, 100%, 97%) | #EFF6FF | Subtle backgrounds |
| `--color-primary-100` | hsl(215, 95%, 93%) | #DBEAFE | Hover states |
| `--color-primary-200` | hsl(215, 93%, 84%) | #BFDBFE | Borders |
| `--color-primary-300` | hsl(215, 90%, 72%) | #93C5FD | Icons |
| `--color-primary-400` | hsl(215, 85%, 60%) | #60A5FA | Active states |
| `--color-primary-500` | hsl(215, 80%, 50%) | #3B82F6 | **Primary brand color** |
| `--color-primary-600` | hsl(215, 80%, 42%) | #2563EB | Primary buttons |
| `--color-primary-700` | hsl(215, 80%, 35%) | #1D4ED8 | Pressed states |
| `--color-primary-800` | hsl(215, 75%, 28%) | #1E40AF | Dark accents |
| `--color-primary-900` | hsl(215, 70%, 20%) | #1E3A8A | Text on light |

### 2.2 Accent Colors (Transport Modes)

Each transport mode has a unique, consistent color:

| Mode | Hex | Token | Usage |
|---|---|---|---|
| Train | #F59E0B | `--color-train` | Train leg cards, map lines |
| Bus | #10B981 | `--color-bus` | Bus leg cards, map lines |
| Flight | #8B5CF6 | `--color-flight` | Flight leg cards, map lines |
| Walking | #6B7280 | `--color-walk` | Walking leg cards, map lines |
| Auto/Cab | #F97316 | `--color-cab` | Cab leg cards, map lines |
| Metro | #EC4899 | `--color-metro` | Metro leg cards, map lines |

### 2.3 Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `--color-success` | #22C55E | Confirmation, HIGH confidence |
| `--color-warning` | #F59E0B | Warnings, MEDIUM confidence |
| `--color-error` | #EF4444 | Errors, LOW confidence, emergency |
| `--color-info` | #3B82F6 | Informational badges |

### 2.4 Neutral Colors

| Token | Hex | Usage |
|---|---|---|
| `--color-neutral-50` | #F9FAFB | Page background (light mode) |
| `--color-neutral-100` | #F3F4F6 | Card background (light mode) |
| `--color-neutral-200` | #E5E7EB | Borders, dividers |
| `--color-neutral-300` | #D1D5DB | Disabled states |
| `--color-neutral-400` | #9CA3AF | Placeholder text |
| `--color-neutral-500` | #6B7280 | Secondary text |
| `--color-neutral-600` | #4B5563 | Body text |
| `--color-neutral-700` | #374151 | Heading text |
| `--color-neutral-800` | #1F2937 | Page background (dark mode) |
| `--color-neutral-900` | #111827 | Card background (dark mode) |
| `--color-neutral-950` | #030712 | Deepest dark |

### 2.5 Dark Mode

TravelMate AI supports system-preference dark mode. All components use CSS custom properties that swap automatically:

| Element | Light Mode | Dark Mode |
|---|---|---|
| Page background | `--color-neutral-50` | `--color-neutral-900` |
| Card background | `white` | `--color-neutral-800` |
| Primary text | `--color-neutral-700` | `--color-neutral-100` |
| Secondary text | `--color-neutral-500` | `--color-neutral-400` |
| Borders | `--color-neutral-200` | `--color-neutral-700` |

---

## 3. Typography

### 3.1 Font Stack

| Usage | Font | Weight | Fallback |
|---|---|---|---|
| Headings | **Inter** | 600 (Semibold), 700 (Bold) | system-ui, -apple-system, sans-serif |
| Body text | **Inter** | 400 (Regular), 500 (Medium) | system-ui, -apple-system, sans-serif |
| Monospace (data) | **JetBrains Mono** | 400 | monospace |

**Loading strategy:** Google Fonts with `display=swap` and preconnect link.

### 3.2 Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---|---|---|---|
| `--text-xs` | 12px | 16px | 400 | Captions, timestamps |
| `--text-sm` | 14px | 20px | 400 | Secondary text, labels |
| `--text-base` | 16px | 24px | 400 | Body text |
| `--text-lg` | 18px | 28px | 500 | Emphasized body |
| `--text-xl` | 20px | 28px | 600 | Section headers |
| `--text-2xl` | 24px | 32px | 600 | Page titles |
| `--text-3xl` | 30px | 36px | 700 | Hero headings |
| `--text-4xl` | 36px | 40px | 700 | Landing hero |
| `--text-5xl` | 48px | 48px | 700 | Marketing display |

---

## 4. Spacing

Based on a 4px grid system:

| Token | Value | Usage |
|---|---|---|
| `--space-1` | 4px | Tight gaps (icon + label) |
| `--space-2` | 8px | Inline element spacing |
| `--space-3` | 12px | Small component padding |
| `--space-4` | 16px | Standard component padding |
| `--space-5` | 20px | Card padding |
| `--space-6` | 24px | Section spacing |
| `--space-8` | 32px | Large section gaps |
| `--space-10` | 40px | Page section margins |
| `--space-12` | 48px | Major layout sections |
| `--space-16` | 64px | Hero section vertical padding |

---

## 5. Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 4px | Small badges, tags |
| `--radius-md` | 8px | Buttons, inputs |
| `--radius-lg` | 12px | Cards, panels |
| `--radius-xl` | 16px | Large cards, modals |
| `--radius-2xl` | 24px | Pill shapes |
| `--radius-full` | 9999px | Circular elements (avatars) |

---

## 6. Shadows

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `--shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)` | Cards |
| `--shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)` | Modals, dropdowns |
| `--shadow-xl` | `0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)` | Floating elements |

---

## 7. Iconography

**Icon Library:** Lucide Icons (open source, consistent with shadcn/ui)

### Transport Mode Icons

| Mode | Lucide Icon | Usage |
|---|---|---|
| Train | `Train` | Leg card, map marker |
| Bus | `Bus` | Leg card, map marker |
| Flight | `Plane` | Leg card, map marker |
| Walking | `Footprints` | Leg card, map marker |
| Auto/Cab | `Car` | Leg card, map marker |
| Metro | `TrainFront` | Leg card, map marker |
| Bike | `Bike` | Leg card, map marker |

### UI Icons

| Action | Icon |
|---|---|
| Search | `Search` |
| Calendar | `Calendar` |
| Clock | `Clock` |
| Location | `MapPin` |
| Download | `Download` |
| Share | `Share2` |
| Settings | `Settings` |
| User | `User` |
| Emergency | `ShieldAlert` |
| Chat | `MessageCircle` |
| Microphone | `Mic` |
| Notification | `Bell` |

---

## 8. Component Design Tokens

### 8.1 Buttons

| Variant | Background | Text | Border | Hover | Usage |
|---|---|---|---|---|---|
| Primary | `--primary-600` | White | None | `--primary-700` | Main CTA |
| Secondary | `--primary-50` | `--primary-600` | `--primary-200` | `--primary-100` | Secondary actions |
| Ghost | Transparent | `--neutral-600` | None | `--neutral-100` | Tertiary actions |
| Destructive | `--error` | White | None | Darker red | Delete actions |
| Outline | Transparent | `--neutral-700` | `--neutral-300` | `--neutral-100` | Form actions |

**Sizes:**

| Size | Height | Padding | Font Size |
|---|---|---|---|
| sm | 32px | 12px 16px | 14px |
| md | 40px | 16px 24px | 16px |
| lg | 48px | 20px 32px | 18px |

### 8.2 Cards

| Property | Value |
|---|---|
| Background | White (light) / `--neutral-800` (dark) |
| Border | `1px solid --neutral-200` |
| Border Radius | `--radius-lg` (12px) |
| Padding | `--space-5` (20px) |
| Shadow | `--shadow-md` |
| Hover Shadow | `--shadow-lg` |
| Transition | `box-shadow 200ms ease` |

### 8.3 Inputs

| Property | Value |
|---|---|
| Height | 44px (mobile touch target compliant) |
| Border | `1px solid --neutral-300` |
| Border Radius | `--radius-md` (8px) |
| Padding | `12px 16px` |
| Focus Ring | `2px solid --primary-500` with 2px offset |
| Error State | Border `--color-error`, error message below |
| Placeholder Color | `--neutral-400` |

---

## 9. Confidence Badge Design

The confidence badge is one of TravelMate AI's most important design elements — it communicates data trustworthiness:

| Level | Color | Icon | Label | Background |
|---|---|---|---|---|
| HIGH | `--color-success` | ✓ checkmark | "Confirmed" | Green/10% opacity |
| MEDIUM | `--color-warning` | ⚠ triangle | "Estimated" | Amber/10% opacity |
| LOW | `--color-error` | ! exclamation | "Verify locally" | Red/10% opacity |

**Design:** Pill-shaped badge, 24px height, 12px font, icon + text.

---

## 10. Motion and Animation

See `Animations.md` for complete animation specifications. Summary:

| Property | Value |
|---|---|
| Default duration | 200ms |
| Easing | `ease-out` for entrances, `ease-in` for exits |
| Page transitions | 300ms fade + slide up |
| Card hover | 200ms shadow lift |
| Loading skeleton | 1.5s pulse cycle |
| Map route draw | 1000ms animated polyline |
| Respect prefers-reduced-motion | Yes — disable all non-essential animation |
