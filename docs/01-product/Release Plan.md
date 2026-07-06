# Release Plan.md

# TravelMate AI — Release Plan

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## Release Strategy

TravelMate AI follows a **progressive release model**:

1. **Internal Alpha** — Engineering team + founders only
2. **Closed Beta** — 100 invited users (pilgrimage travel communities)
3. **Open Beta** — Public access, clearly marked as Beta
4. **v1.0 GA** — Full public launch with subscription monetization
5. **Patch Releases** — Bug fixes and minor improvements (weekly)
6. **Minor Releases** — New features (bi-weekly)
7. **Major Releases** — Significant feature milestones (quarterly)

---

## Release v0.1 — Internal Alpha

**Date:** Week 2 of Month 1  
**Audience:** Engineering team (5 people)  
**Scope:**
- Basic trip planning UI (non-functional, UI only)
- API scaffolding running locally
- Database schema deployed
- Authentication flow working (Supabase)

**Exit Criteria:**
- All engineers can log in and navigate the app
- Backend API returns placeholder responses
- No critical build errors

---

## Release v0.2 — Feature Alpha

**Date:** Week 6 of Month 2  
**Audience:** Engineering + 10 internal testers  
**Scope:**
- Train planning via RailwayAPI (real data)
- Google Maps geocoding working
- Basic itinerary display (no map)
- Weather widget functional
- LangGraph TrainAgent and RouteAgent working

**Exit Criteria:**
- "Navsari → Trimbakeshwar" returns a real itinerary
- Train schedule data is accurate
- No P0 bugs

---

## Release v0.5 — Closed Beta

**Date:** Week 10 of Month 3  
**Audience:** 100 invited users (pilgrimage travel community via WhatsApp outreach)  
**Scope:**
- Full multi-modal itinerary (train + bus + walking)
- Temple timings displayed
- Budget breakdown
- Basic AI chat
- User accounts (Supabase)
- Offline PDF export
- Subscription (Free tier only)

**Gate Criteria:**
- P95 response time < 10 seconds (relaxed for beta)
- CSAT from beta users ≥ 3.5/5
- No critical security vulnerabilities
- Offline PDF works on Android Chrome and iOS Safari

**Feedback Channels:**
- In-app feedback form
- WhatsApp group with beta users
- Fortnightly user interviews (6 sessions)

---

## Release v1.0 — General Availability (GA)

**Date:** End of Month 3  
**Audience:** Public  
**Scope:**
- All P0 features complete (see Feature Matrix)
- Subscription tiers: Free, Explorer, Pro
- Stripe payment processing
- Real transport data with confidence scoring
- Temple database (500 temples)
- Weather for all Indian states
- Hotel suggestions (affiliate links)
- Notifications (email + PWA push)
- Emergency screen
- Responsive design (mobile, tablet, desktop)
- WCAG 2.1 AA for core screens
- Lighthouse score ≥ 85

**Launch Gate Criteria:**
- [ ] P95 itinerary response time < 8 seconds
- [ ] API uptime test: 99.9% over 72-hour load test
- [ ] Security audit completed (no critical/high vulnerabilities)
- [ ] Stripe payment tested in production with ₹1 test charge
- [ ] Offline PDF tested on 10 device types
- [ ] WCAG audit passed for all P0 screens
- [ ] Privacy policy and Terms of Service live
- [ ] DPDP consent flow live
- [ ] Emergency screen accessible without login
- [ ] Production monitoring (Datadog) configured
- [ ] Error alerting (PagerDuty) configured
- [ ] Database backups verified

---

## Release v1.5 — Growth Release

**Date:** Month 6  
**Scope:**
- Flight leg planning (Amadeus API)
- Metro GTFS integration
- Return trip planning
- Voice input (English + Hindi)
- Senior citizen mode
- Real-time train delay alerts
- Itinerary sharing via link

---

## Release v2.0 — Monetization Release

**Date:** Month 9  
**Scope:**
- Business tier
- B2B API
- Expense export
- Admin dashboard
- Affiliate hotel booking
- Multi-city planning

---

## Versioning Scheme

TravelMate AI follows **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

| Component | Meaning | Example |
|---|---|---|
| MAJOR | Breaking changes or major feature milestones | v1.0.0 → v2.0.0 |
| MINOR | New features, backward compatible | v1.0.0 → v1.1.0 |
| PATCH | Bug fixes, security patches | v1.0.0 → v1.0.1 |

---

## Rollback Plan

Every production deployment includes an automatic rollback trigger:

1. **Automatic rollback** if:
   - Error rate increases > 2% within 5 minutes of deployment
   - API P99 response time > 15 seconds post-deploy

2. **Manual rollback** command:
   - Vercel: `vercel rollback` (frontend)
   - Railway: Previous deployment promotion (backend)

3. **Database migrations:**
   - All migrations are reversible
   - Rollback migration runs automatically on deployment failure
   - Data migrations require manual review before rollback

---

## Communication Plan

| Audience | Channel | Frequency | Content |
|---|---|---|---|
| Users | In-app announcement | Per release | "What's new in TravelMate AI" |
| Users | Email newsletter | Per major/minor release | Feature highlights |
| Beta users | WhatsApp group | Every 2 weeks | Beta updates, feedback requests |
| Engineering | Slack #releases | Per release | Technical notes, deployment status |
| Support team | Slack #support-updates | Per release | Changes affecting support topics |
