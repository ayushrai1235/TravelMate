from __future__ import annotations

import logging
from typing import Any

from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)


async def synthesis_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: OrchestratorAgent - synthesizes all agent results into final ItineraryResponse."""
    logger.info("Executing synthesis_node...")

    errors = list(state.get("errors", []))
    geocoded_origin = state.get("geocoded_origin", {})
    geocoded_destination = state.get("geocoded_destination", {})
    travel_date = state.get("travel_date", "")
    departure_preference = state.get("departure_preference", "morning")
    group = state.get("group", {"adults": 1, "children": 0, "seniors": 0})
    preferences = state.get("preferences", {})
    distance_km = state.get("distance_km", 0)

    legs = _build_legs(state)
    total_duration = _calculate_total_duration(legs)
    total_cost = _calculate_total_cost(legs)

    itinerary = {
        "itinerary_id": f"itin_{travel_date.replace('-', '')}_{geocoded_origin.get('name', '')[:3]}_{geocoded_destination.get('name', '')[:3]}",
        "origin": {
            "text": state.get("origin", {}).get("text", ""),
            "coordinates": geocoded_origin,
            "resolved_name": geocoded_origin.get("resolved_name", geocoded_origin.get("name", "")),
        },
        "destination": {
            "text": state.get("destination", {}).get("text", ""),
            "coordinates": geocoded_destination,
            "resolved_name": geocoded_destination.get("resolved_name", geocoded_destination.get("name", "")),
        },
        "travel_date": travel_date,
        "departure_preference": departure_preference,
        "group": group,
        "total_duration_minutes": total_duration,
        "total_cost_inr": total_cost,
        "distance_km": distance_km,
        "legs": legs,
        "contextual_data": _build_contextual_data(state),
        "confidence_summary": _compute_confidence_summary(legs),
        "data_timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }

    return {
        "itinerary": itinerary,
        "errors": errors,
    }


def _build_legs(state: TripPlanningState) -> list[dict[str, Any]]:
    """Build chronological leg list from all agent data."""
    legs = []
    sequence = 1

    # Auto first-mile
    distance_km = state.get("distance_km", 0)
    if distance_km and distance_km > 0.5:
        legs.append({
            "leg_id": f"leg_{sequence:03d}",
            "sequence": sequence,
            "mode": "AUTO",
            "origin": {"name": "Home", "coordinates": state.get("geocoded_origin", {})},
            "destination": {"name": "Nearest Transit Hub", "coordinates": state.get("geocoded_origin", {})},
            "duration_minutes": max(10, int(distance_km * 4)),
            "cost_inr": {"min": max(50, int(distance_km * 15)), "max": max(80, int(distance_km * 25))},
            "confidence": "MEDIUM",
            "data_source": "Google Maps Distance Matrix",
            "notes": "Auto fare is estimated. Negotiate with driver.",
        })
        sequence += 1

    # Train legs
    train_data = state.get("train_data")
    if train_data and isinstance(train_data, dict) and train_data.get("trains"):
        for train in train_data["trains"]:
            legs.append({
                "leg_id": f"leg_{sequence:03d}",
                "sequence": sequence,
                "mode": "TRAIN",
                "origin": {"name": train.get("source", {}).get("name", ""), "coordinates": {}},
                "destination": {"name": train.get("destination", {}).get("name", ""), "coordinates": {}},
                "departure_time": train.get("departure_time", ""),
                "arrival_time": train.get("arrival_time", ""),
                "duration_minutes": train.get("duration_minutes", 0),
                "train_number": train.get("number", ""),
                "train_name": train.get("name", ""),
                "cost_inr": _extract_train_cost(train),
                "confidence": "HIGH",
                "data_source": "RailRadar",
            })
            sequence += 1

    # Bus legs
    bus_data = state.get("bus_data")
    if bus_data and isinstance(bus_data, dict):
        routes = bus_data.get("routes", [])
        if routes:
            for route in routes:
                legs.append({
                    "leg_id": f"leg_{sequence:03d}",
                    "sequence": sequence,
                    "mode": "BUS",
                    "origin": {"name": route.get("origin_stop", "")},
                    "destination": {"name": route.get("destination_stop", "")},
                    "duration_minutes": route.get("duration_minutes", 60),
                    "cost_inr": route.get("fare_inr", {"min": 30, "max": 60}),
                    "confidence": route.get("confidence", "MEDIUM"),
                    "data_source": route.get("data_source", "GTFS"),
                    "notes": route.get("notes", ""),
                })
                sequence += 1
        elif bus_data.get("ai_guidance"):
            legs.append({
                "leg_id": f"leg_{sequence:03d}",
                "sequence": sequence,
                "mode": "BUS",
                "origin": {"name": state.get("geocoded_destination", {}).get("name", "")},
                "destination": {"name": state.get("destination", {}).get("text", "")},
                "duration_minutes": 45,
                "cost_inr": {"min": 30, "max": 60},
                "confidence": "LOW",
                "data_source": "AI-guided estimation",
                "notes": bus_data["ai_guidance"],
            })
            sequence += 1

    # Walking last-mile
    legs.append({
        "leg_id": f"leg_{sequence:03d}",
        "sequence": sequence,
        "mode": "WALK",
        "origin": {"name": "Arrival Point", "coordinates": state.get("geocoded_destination", {})},
        "destination": {"name": state.get("destination", {}).get("text", "")},
        "duration_minutes": max(10, int(distance_km * 12)) if distance_km else 15,
        "cost_inr": {"min": 0, "max": 0},
        "confidence": "HIGH",
        "data_source": "Estimated",
    })

    return legs


def _calculate_total_duration(legs: list[dict]) -> int:
    """Calculate total journey duration including transfer buffers."""
    total = sum(leg.get("duration_minutes", 0) for leg in legs)
    # Add 10 min transfer buffer between each leg
    total += max(0, len(legs) - 1) * 10
    return total


def _calculate_total_cost(legs: list[dict]) -> dict[str, int]:
    """Calculate total cost range from all legs."""
    min_total = sum(leg.get("cost_inr", {}).get("min", 0) for leg in legs)
    max_total = sum(leg.get("cost_inr", {}).get("max", 0) for leg in legs)
    return {"min": min_total, "max": max_total}


def _build_contextual_data(state: TripPlanningState) -> dict[str, Any]:
    """Build contextual data section from agent results."""
    context = {}

    weather_data = state.get("weather_data")
    if weather_data:
        context["weather"] = weather_data

    temple_data = state.get("temple_data")
    if temple_data:
        context["temple"] = temple_data

    hotel_data = state.get("hotel_data")
    if hotel_data:
        context["hotels"] = hotel_data

    budget_data = state.get("budget_data")
    if budget_data:
        context["budget_summary"] = budget_data

    return context


def _compute_confidence_summary(legs: list[dict]) -> dict[str, Any]:
    """Compute overall itinerary confidence (minimum across all legs)."""
    confidences = []
    low_confidence_legs = []

    for leg in legs:
        conf = leg.get("confidence", "MEDIUM")
        confidences.append(conf)
        if conf == "LOW":
            low_confidence_legs.append(leg.get("leg_id", ""))

    confidence_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if confidences:
        min_conf = min(confidences, key=lambda c: confidence_order.get(c, 0))
    else:
        min_conf = "MEDIUM"

    warnings = []
    if low_confidence_legs:
        warnings.append(f"{len(low_confidence_legs)} leg(s) have LOW confidence. Verify locally before travel.")

    return {
        "overall": min_conf,
        "low_confidence_legs": low_confidence_legs,
        "warnings": warnings,
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
