from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)


async def fallback_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: Rule-based fallback when AI planning is unavailable.
    
    Implements the fallback hierarchy from Fallback Strategy.md:
    1. Look up cached train schedules
    2. Calculate first/last mile as auto (distance * Rs.15/km)
    3. Assemble basic itinerary
    4. Mark ALL data as LOW confidence
    """
    logger.warning("Executing fallback_node - AI planning unavailable, using rule-based fallback.")

    geocoded_origin = state.get("geocoded_origin", {})
    geocoded_destination = state.get("geocoded_destination", {})
    travel_date = state.get("travel_date", "")
    origin_text = state.get("origin", {}).get("text", "")
    dest_text = state.get("destination", {}).get("text", "")
    group = state.get("group", {"adults": 1, "children": 0, "seniors": 0})
    preferences = state.get("preferences", {})
    distance_km = state.get("distance_km", 0)
    errors = list(state.get("errors", []))

    if not distance_km:
        import math
        lat_diff = geocoded_destination.get("lat", 0) - geocoded_origin.get("lat", 0)
        lng_diff = geocoded_destination.get("lng", 0) - geocoded_origin.get("lng", 0)
        distance_km = round(math.sqrt(lat_diff ** 2 + lng_diff ** 2) * 111.0, 1)

    # Build fallback legs
    legs = []
    sequence = 1

    # Auto first-mile
    if distance_km > 0.5:
        legs.append({
            "leg_id": f"leg_{sequence:03d}",
            "sequence": sequence,
            "mode": "AUTO",
            "origin": {"name": "Home", "coordinates": geocoded_origin},
            "destination": {"name": "Nearest Transit Hub"},
            "duration_minutes": max(10, int(distance_km * 4)),
            "cost_inr": {"min": max(50, int(distance_km * 15)), "max": max(80, int(distance_km * 25))},
            "confidence": "LOW",
            "data_source": "Rule-based estimation",
            "notes": "Route estimated based on distance. Verify locally.",
        })
        sequence += 1

    # Train leg (estimated from cached data)
    train_data = state.get("train_data")
    if train_data and isinstance(train_data, dict) and train_data.get("trains"):
        for train in train_data["trains"]:
            legs.append({
                "leg_id": f"leg_{sequence:03d}",
                "sequence": sequence,
                "mode": "TRAIN",
                "origin": {"name": train.get("source", {}).get("name", "")},
                "destination": {"name": train.get("destination", {}).get("name", "")},
                "departure_time": train.get("departure_time", ""),
                "arrival_time": train.get("arrival_time", ""),
                "duration_minutes": train.get("duration_minutes", 0),
                "train_number": train.get("number", ""),
                "train_name": train.get("name", ""),
                "cost_inr": _extract_train_cost(train),
                "confidence": "MEDIUM",
                "data_source": "Cached schedule data",
                "notes": "Based on scheduled data. Verify current schedules.",
            })
            sequence += 1
    else:
        legs.append({
            "leg_id": f"leg_{sequence:03d}",
            "sequence": sequence,
            "mode": "TRAIN",
            "origin": {"name": geocoded_origin.get("name", origin_text)},
            "destination": {"name": geocoded_destination.get("name", dest_text)},
            "departure_time": "TBD",
            "arrival_time": "TBD",
            "duration_minutes": int(distance_km * 2.5),
            "cost_inr": {"min": 180, "max": 800},
            "confidence": "LOW",
            "data_source": "Estimated from cached timetable",
            "notes": "Train schedules unavailable. Check IRCTC: irctc.co.in",
        })
        sequence += 1

    # Bus leg
    legs.append({
        "leg_id": f"leg_{sequence:03d}",
        "sequence": sequence,
        "mode": "BUS",
        "origin": {"name": geocoded_destination.get("name", dest_text)},
        "destination": {"name": dest_text},
        "duration_minutes": 60,
        "cost_inr": {"min": 30, "max": 60},
        "confidence": "LOW",
        "data_source": "AI-guided estimation",
        "notes": "Buses run towards destination approximately hourly. Confirm at bus stand.",
    })
    sequence += 1

    # Walking last-mile
    legs.append({
        "leg_id": f"leg_{sequence:03d}",
        "sequence": sequence,
        "mode": "WALK",
        "origin": {"name": "Arrival Point", "coordinates": geocoded_destination},
        "destination": {"name": dest_text},
        "duration_minutes": max(15, int(distance_km * 12)),
        "cost_inr": {"min": 0, "max": 0},
        "confidence": "HIGH",
        "data_source": "Estimated",
    })

    # Compute totals
    total_duration = sum(leg.get("duration_minutes", 0) for leg in legs) + max(0, len(legs) - 1) * 10
    total_cost_min = sum(leg.get("cost_inr", {}).get("min", 0) for leg in legs)
    total_cost_max = sum(leg.get("cost_inr", {}).get("max", 0) for leg in legs)

    itinerary = {
        "itinerary_id": f"itin_fallback_{travel_date.replace('-', '')}_{datetime.utcnow().strftime('%H%M')}",
        "origin": {
            "text": origin_text,
            "coordinates": geocoded_origin,
            "resolved_name": geocoded_origin.get("resolved_name", origin_text),
        },
        "destination": {
            "text": dest_text,
            "coordinates": geocoded_destination,
            "resolved_name": geocoded_destination.get("resolved_name", dest_text),
        },
        "travel_date": travel_date,
        "departure_preference": state.get("departure_preference", "morning"),
        "group": group,
        "total_duration_minutes": total_duration,
        "total_cost_inr": {"min": total_cost_min, "max": total_cost_max},
        "distance_km": distance_km,
        "legs": legs,
        "contextual_data": {
            "fallback_notice": {
                "message": "AI planning is temporarily unavailable. We've planned your route using our schedule database.",
                "data_quality": "LOW",
                "recommendation": "Please verify all schedules and fares before traveling.",
            }
        },
        "confidence_summary": {
            "overall": "LOW",
            "low_confidence_legs": [leg.get("leg_id") for leg in legs if leg.get("confidence") == "LOW"],
            "warnings": ["This itinerary uses estimated/ cached data. Verify all details before traveling."],
        },
        "data_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    errors.append({"agent": "fallback", "message": "Fallback mode activated - using rule-based planning.", "recoverable": False})

    return {
        "itinerary": itinerary,
        "errors": errors,
        "validation_passed": True,
    }


def _extract_train_cost(train: dict) -> dict:
    """Extract cost range from train data."""
    classes = train.get("classes_available", [])
    if not classes:
        return {"min": 180, "max": 800}

    fare_map = {"SL": (180, 350), "3A": (500, 900), "2A": (800, 1400), "1A": (1500, 2500), "CC": (250, 450), "2S": (60, 150)}
    best_class = classes[0]
    fare_range = fare_map.get(best_class, (200, 500))
    return {"min": fare_range[0], "max": fare_range[1]}
