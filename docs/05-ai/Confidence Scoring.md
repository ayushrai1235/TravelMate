# Confidence Scoring.md

# TravelMate AI — Confidence Scoring System

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Purpose

The Confidence Scoring System is TravelMate AI's trust mechanism. Every data point displayed to the user carries a confidence label so users know how much to rely on each piece of information.

---

## 2. Confidence Levels

| Level | Numeric Range | Label | Color | Meaning |
|---|---|---|---|---|
| **HIGH** | 0.8 – 1.0 | "Confirmed" | Green | Data from official API, fresh, verified |
| **MEDIUM** | 0.5 – 0.79 | "Estimated" | Amber | Scheduled data, estimates, or slightly stale |
| **LOW** | 0.0 – 0.49 | "Verify locally" | Red | AI-inferred, unverified, or stale |

---

## 3. Confidence Assignment Rules

### 3.1 Train Data

| Scenario | Confidence | Score |
|---|---|---|
| Train schedule from RailwayAPI (< 30 min old) | HIGH | 0.95 |
| Train schedule from RailwayAPI (30-60 min old) | MEDIUM | 0.7 |
| Train schedule from static GTFS cache (> 1 day old) | MEDIUM | 0.6 |
| Real-time running status from NTES | HIGH | 0.9 |
| Running status unavailable | null | — (not displayed) |
| Train number NOT found in any source | REJECT | — (hallucination alert) |

### 3.2 Bus Data

| Scenario | Confidence | Score |
|---|---|---|
| GTFS feed, updated within 7 days | MEDIUM | 0.7 |
| GTFS feed, last update > 30 days ago | MEDIUM | 0.55 |
| Google Transit Directions result | MEDIUM | 0.65 |
| AI-estimated route guidance (no confirmed data) | LOW | 0.3 |
| Bus number not in any data source | REJECT | — (never display) |

### 3.3 Cab/Auto Estimates

| Scenario | Confidence | Score |
|---|---|---|
| Google Distance Matrix estimate | MEDIUM | 0.7 |
| Straight-line distance × factor estimate | LOW | 0.4 |

### 3.4 Weather

| Scenario | Confidence | Score |
|---|---|---|
| OpenWeatherMap forecast, 1-3 day horizon | HIGH | 0.9 |
| OpenWeatherMap forecast, 4-7 day horizon | MEDIUM | 0.7 |
| Forecast > 7 days | LOW | 0.4 |

### 3.5 Temple Data

| Scenario | Confidence | Score |
|---|---|---|
| Curated database, updated < 30 days | HIGH | 0.9 |
| Curated database, updated 30-90 days | MEDIUM | 0.6 |
| Curated database, updated > 90 days | LOW | 0.4 |
| Temple not in database | null | Not displayed |

### 3.6 Hotel Data

| Scenario | Confidence | Score |
|---|---|---|
| Google Places API result, < 6 hours old | MEDIUM | 0.7 |
| Google Places cached > 24 hours | LOW | 0.5 |

### 3.7 Cost Estimates

| Scenario | Confidence | Score |
|---|---|---|
| Fixed fare from API (train, metro) | HIGH | 0.9 |
| Distance-based estimate | MEDIUM | 0.6 |
| AI-generated estimate | LOW | 0.4 |

---

## 4. Overall Itinerary Confidence

The itinerary-level confidence is the MINIMUM confidence across all transport legs:

```
itinerary_confidence = min(leg.confidence for leg in legs if leg.confidence is not null)
```

**Rationale:** A trip is only as reliable as its weakest link. If one bus leg is LOW confidence, the user should know the overall plan has uncertainty.

---

## 5. Confidence Validator (Post-Agent)

After each agent returns data, the `ConfidenceValidator` runs:

### 5.1 Validation Steps

```python
class ConfidenceValidator:
    def validate(self, agent_output: dict, tool_call_log: list) -> ValidationResult:
        errors = []
        
        # 1. Check all transport entities against tool call results
        for entity in extract_transport_entities(agent_output):
            if not entity_in_tool_results(entity, tool_call_log):
                errors.append(HallucinationError(entity))
        
        # 2. Check chronological ordering
        legs = agent_output.get("legs", [])
        for i in range(len(legs) - 1):
            if legs[i]["arrival_time"] > legs[i+1]["departure_time"]:
                errors.append(ChronologyError(legs[i], legs[i+1]))
        
        # 3. Check required fields
        for leg in legs:
            for field in REQUIRED_FIELDS:
                if field not in leg:
                    errors.append(MissingFieldError(leg, field))
        
        # 4. Verify confidence assignment
        for leg in legs:
            expected = self.compute_expected_confidence(leg, tool_call_log)
            if leg["confidence"] != expected:
                leg["confidence"] = expected  # Auto-correct
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
```

### 5.2 Validation Outcomes

| Outcome | Action |
|---|---|
| All valid | Proceed to synthesis |
| Non-critical errors (missing optional field) | Fix and continue |
| Hallucination detected | Re-prompt agent once; if fails again, use fallback |
| Chronology error | Re-prompt with explicit correction instruction |
| Multiple critical errors | Activate fallback_node |

---

## 6. Data Provenance

Every data point includes provenance metadata:

```json
{
  "value": "07:45",
  "field": "departure_time",
  "confidence": 0.95,
  "confidence_level": "HIGH",
  "data_source": "RailwayAPI.in",
  "data_retrieved_at": "2026-07-03T14:00:00Z",
  "data_freshness_seconds": 300,
  "cache_hit": true
}
```

The UI displays a simplified version: `✓ Confirmed — RailwayAPI (5 min ago)`
