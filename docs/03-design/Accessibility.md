# Accessibility.md

# TravelMate AI — Accessibility Specification

**Version:** 1.0.0  
**Date:** 2026-07-03  
**Standard:** WCAG 2.1 Level AA

---

## 1. Accessibility Commitment

TravelMate AI serves users from tech-savvy 22-year-old students to 67-year-old pilgrimage travelers. Accessibility is not optional — it is a core product requirement. Every P0 screen must pass WCAG 2.1 AA before launch.

---

## 2. Perceivable

### 2.1 Color Contrast

| Element | Minimum Ratio | Measured Against |
|---|---|---|
| Body text (16px+) | 4.5:1 | Background |
| Large text (24px+ or 18px bold) | 3:1 | Background |
| UI component borders | 3:1 | Adjacent colors |
| Focus indicators | 3:1 | Adjacent colors |
| Confidence badges | Text within badge meets 4.5:1 | Badge background |

**Dark mode:** All contrast ratios verified independently for dark mode palette.

**Color-blind safety:** Transport mode colors are distinguishable by deuteranopia, protanopia, and tritanopia simulations. Additionally, every mode has a unique icon — color is never the sole differentiator.

### 2.2 Text Alternatives

| Element | Requirement |
|---|---|
| Transport mode icons | `aria-label="Train"`, `aria-label="Bus"`, etc. |
| Confidence badge | `aria-label="Confidence: High. Source: RailwayAPI"` |
| Map markers | `aria-label="Stop: Nashik Road Railway Station"` |
| Weather icons | `aria-label="Rainy, 32 degrees Celsius"` |
| Decorative images | `aria-hidden="true"`, empty `alt=""` |
| Informational images | Descriptive `alt` text |

### 2.3 Text Resizing

- Base font: 16px minimum
- All text scales with browser zoom up to 200% without layout breakage
- No text in images (all text rendered as HTML)
- Senior citizen mode increases base font to 20px and line height to 1.8

---

## 3. Operable

### 3.1 Keyboard Navigation

| Component | Tab Order | Keyboard Interaction |
|---|---|---|
| Location input | Sequential in form | Type to search; Arrow keys to navigate suggestions; Enter to select; Escape to close |
| Date picker | After location inputs | Arrow keys navigate dates; Enter selects; Escape closes |
| "Plan My Trip" button | After date/time | Enter or Space activates |
| Itinerary legs | Sequential (top to bottom) | Enter expands details; Escape collapses |
| Map | After itinerary | Arrow keys pan; +/- zoom; Tab to markers |
| AI Chat input | After main content | Enter sends message; Shift+Enter for newline |
| Emergency contacts | Sequential | Enter activates call link |
| Bottom nav (mobile) | Sequential | Enter navigates |

### 3.2 Focus Management

| Scenario | Focus Behavior |
|---|---|
| Page load | Focus on first interactive element (skip-to-content link available) |
| Modal open | Focus trapped inside modal; first focusable element receives focus |
| Modal close | Focus returns to trigger element |
| Itinerary loads | Focus moves to first leg card (announced by screen reader) |
| Error appears | Focus moves to error message |
| Toast notification | `role="alert"` announces; focus stays on current element |

### 3.3 Skip Navigation

Every page includes a visually hidden (but focusable) "Skip to main content" link as the first tab stop:
```html
<a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>
```

### 3.4 Touch Targets

- Minimum touch target: 44×44px (iOS HIG + WCAG 2.5.5)
- Emergency call buttons: 48×48px minimum
- Spacing between touch targets: ≥ 8px

---

## 4. Understandable

### 4.1 Form Errors

| Requirement | Implementation |
|---|---|
| Inline error messages | Error text appears below invalid field |
| Error summary | On form submission, error summary above form lists all errors |
| Focus on error | Focus moves to first invalid field |
| Screen reader announcement | `aria-invalid="true"` + `aria-describedby` pointing to error message |
| Clear error text | "Please enter a valid city name" (not "Error 400") |

### 4.2 Language

- HTML `lang="en"` attribute on root element
- Language switcher updates `lang` attribute for Hindi/Gujarati content
- Abbreviations have `<abbr>` tags with `title` attributes

### 4.3 Predictable Behavior

- No auto-advancing content without user control
- No unexpected context changes on focus
- Form submissions require explicit button click/Enter press
- Auto-save triggers show a non-intrusive toast (not a modal)

---

## 5. Robust

### 5.1 Semantic HTML

| UI Element | Semantic HTML |
|---|---|
| Page header | `<header>` with `role="banner"` |
| Navigation | `<nav>` with `aria-label` |
| Main content | `<main>` with `id="main-content"` |
| Sidebar | `<aside>` |
| Footer | `<footer>` |
| Itinerary list | `<ol>` (ordered list of legs) |
| Leg card | `<article>` |
| Chat messages | `<ul>` with `role="log"` and `aria-live="polite"` |
| Modals | `<dialog>` or `role="dialog"` with `aria-modal="true"` |

### 5.2 ARIA Landmarks

Every page has these landmarks:
```html
<header role="banner">          <!-- Top navigation -->
<nav role="navigation">          <!-- Primary nav -->
<main role="main">               <!-- Page content -->
<aside role="complementary">     <!-- Sidebar/Map panel -->
<footer role="contentinfo">      <!-- Footer -->
```

### 5.3 Live Regions

| Element | ARIA Live | Purpose |
|---|---|---|
| Loading status messages | `aria-live="polite"` | "Planning your journey... Checking train schedules..." |
| Chat messages | `aria-live="polite"` | New messages announced |
| Error notifications | `aria-live="assertive"` | Errors interrupt immediately |
| Toast notifications | `role="alert"` | Confirmations announced |

---

## 6. Senior Citizen Mode

When enabled (via profile settings or accessibility toggle):

| Modification | Default | Senior Mode |
|---|---|---|
| Base font size | 16px | 20px |
| Line height | 1.5 | 1.8 |
| Button size | 40px height | 52px height |
| Touch targets | 44×44px | 52×52px |
| Color contrast | 4.5:1 | 7:1 (WCAG AAA) |
| Animation | Enabled | Reduced |
| Navigation | Standard | Simplified (fewer options) |
| AI Chat | Standard | Larger input, voice input prominent |

---

## 7. Accessibility Testing Plan

| Test Type | Tool | Frequency |
|---|---|---|
| Automated scan | axe-core (CI pipeline) | Every PR |
| Color contrast | Lighthouse + axe | Every PR |
| Keyboard navigation | Manual testing | Every sprint |
| Screen reader | NVDA (Windows), VoiceOver (macOS/iOS) | Every release |
| Touch target audit | Manual measurement | Every sprint |
| Cognitive load review | UX team review | Every major feature |
| User testing | 2 users with disabilities per quarter | Quarterly |
