# KPIs.md

# TravelMate AI — Key Performance Indicators

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Acquisition KPIs

| KPI | Description | Measurement | Target M3 | Target M6 | Target M12 |
|---|---|---|---|---|---|
| **New Registrations / Month** | Users completing signup | Auth DB count | 5,000 | 15,000 | 30,000 |
| **Monthly Active Users (MAU)** | Users who plan ≥1 trip in month | Event tracking | 10,000 | 50,000 | 200,000 |
| **App Store Rating** | iOS/Android PWA ratings | Store reviews | 4.2 | 4.4 | 4.5 |
| **Organic Search Traffic** | Users from SEO | Google Analytics | 5,000/mo | 20,000/mo | 80,000/mo |
| **Referral Rate** | Users who invited others | Referral tracking | 8% | 12% | 18% |

---

## 2. Engagement KPIs

| KPI | Description | Measurement | Target M3 | Target M6 | Target M12 |
|---|---|---|---|---|---|
| **Trips Planned / MAU** | Average trip plans per active user | Event count / MAU | 2.5 | 3.5 | 4.5 |
| **AI Chat Messages / Session** | Engagement with AI assistant | Event tracking | 3 | 4.5 | 6 |
| **Trip Download Rate** | % of trips downloaded offline | Event tracking | 15% | 25% | 40% |
| **Session Duration** | Average time in app | Analytics | 6 min | 8 min | 10 min |
| **D7 Retention** | Users returning after 7 days | Cohort analysis | 40% | 48% | 55% |
| **D30 Retention** | Users returning after 30 days | Cohort analysis | 25% | 35% | 45% |
| **Voice Input Usage** | % of queries using voice | Feature flag events | 8% | 15% | 25% |
| **Notification Open Rate** | % of push notifs opened | Push analytics | 25% | 30% | 35% |

---

## 3. Revenue KPIs

| KPI | Description | Measurement | Target M3 | Target M6 | Target M12 |
|---|---|---|---|---|---|
| **MRR (Monthly Recurring Revenue)** | Monthly subscription revenue | Stripe MRR | ₹5L | ₹15L | ₹40L |
| **ARR** | Annual run rate | MRR × 12 | ₹60L | ₹1.8Cr | ₹4.8Cr |
| **Free → Paid Conversion** | % of free users converting | Stripe / Auth join | 5% | 8% | 12% |
| **Average Revenue Per User (ARPU)** | MRR / Paying users | Stripe / DB | ₹180 | ₹200 | ₹220 |
| **Churn Rate** | % of paying users cancelling/month | Stripe events | < 8% | < 6% | < 4% |
| **LTV (Lifetime Value)** | ARPU / Churn Rate | Calculated | ₹2,250 | ₹3,333 | ₹5,500 |
| **CAC (Customer Acquisition Cost)** | Total marketing spend / New paid users | Finance | ₹500 | ₹400 | ₹300 |
| **LTV/CAC Ratio** | LTV / CAC | Calculated | 4.5x | 8.3x | 18.3x |
| **Affiliate Revenue** | Hotel/transport referral commissions | Affiliate platform | ₹50K | ₹2L | ₹10L |

---

## 4. Product Quality KPIs

| KPI | Description | Measurement | Target |
|---|---|---|---|
| **Itinerary P50 Response Time** | Median response time | Backend timing | < 4 seconds |
| **Itinerary P95 Response Time** | 95th percentile response | Backend timing | < 8 seconds |
| **API Uptime** | Backend availability | Uptime monitoring | ≥ 99.9% |
| **AI Accuracy Rate** | Plans rated accurate by users | User feedback | ≥ 90% |
| **Hallucination Rate** | AI-generated fake transport data | Manual audit | < 0.1% |
| **Data Freshness** | % of transport data < 24h old | Data pipeline audit | ≥ 95% |
| **Lighthouse Score (Mobile)** | Overall Lighthouse performance | CI/CD Lighthouse | ≥ 85 |
| **WCAG 2.1 AA Compliance** | Accessibility compliance | Axe audit | 100% for P0 screens |
| **Error Rate (API)** | % of API requests returning 5xx | Datadog | < 0.5% |

---

## 5. Support KPIs

| KPI | Description | Target |
|---|---|---|
| **CSAT Score** | Customer satisfaction (1–5 scale) | ≥ 4.2 |
| **NPS (Net Promoter Score)** | Promoters - Detractors | ≥ 45 |
| **Median First Response Time** | Time to first support response | < 24h (Explorer), < 8h (Pro) |
| **Resolution Rate (First Contact)** | Issues resolved in first interaction | ≥ 75% |
| **Support Ticket Volume / 1000 Users** | Support load per user base | < 15 tickets/1000 users/month |

---

## 6. KPI Dashboard and Reporting

### 6.1 Tracking Frequency

| Category | Frequency | Audience |
|---|---|---|
| Revenue (MRR, ARR, Churn) | Weekly | CEO, Finance |
| Engagement (MAU, Retention) | Weekly | Product, Engineering |
| Performance (Response time, Uptime) | Real-time | Engineering |
| Quality (Accuracy, Hallucination) | Monthly | Product, AI Team |
| Support (CSAT, NPS) | Monthly | Customer Success |

### 6.2 Tooling

| Tool | Purpose |
|---|---|
| **Stripe Dashboard** | Revenue, subscription, churn metrics |
| **PostHog** | User behavior, funnel analytics, session recording |
| **Datadog** | API performance, error rates, uptime |
| **Google Search Console** | SEO, organic traffic |
| **Custom Admin Dashboard** | Aggregated KPI view for leadership |

---

## 7. KPI Targets by Release

| KPI | v1.0 Launch | v1.5 (Month 6) | v2.0 (Month 12) |
|---|---|---|---|
| MAU | 10,000 | 50,000 | 200,000 |
| Paid Users | 500 | 4,000 | 16,000 |
| MRR | ₹5L | ₹8L | ₹40L |
| Trip Plans Generated | 50,000 cumulative | 500,000 | 2,000,000 |
| Itinerary P95 | < 8s | < 6s | < 5s |
| Uptime | 99.9% | 99.9% | 99.95% |
