from __future__ import annotations

import logging
from typing import Any

from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

REQUIRED_LEG_FIELDS = {"mode", "origin", "destination", "confidence", "data_source"}


async def validate_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: ConfidenceValidator - validates all itinerary claims for hallucination, chronology, and completeness."""
    logger.info("Executing validate_node...")

    errors = list(state.get("errors", []))
    itinerary = state.get("itinerary")

    if not itinerary or not isinstance(itinerary, dict):
        errors.append({"agent": "validate", "message": "No itinerary to validate.", "recoverable": True})
        return {"itinerary": itinerary, "errors": errors, "validation_passed": False}

    legs = itinerary.get("legs", [])
    validation_errors = []
    validation_warnings = []

    # Step 1: Check all transport entities against known data
    for leg in legs:
        mode = leg.get("mode", "")
        train_number = leg.get("train_number")
        bus_number = leg.get("bus_number")

        if mode == "TRAIN" and train_number:
            train_data = state.get("train_data")
            if train_data and isinstance(train_data, dict):
                known_trains = train_data.get("trains", [])
                known_numbers = [t.get("number") for t in known_trains if isinstance(t, dict)]
                if known_numbers and train_number not in known_numbers:
                    validation_errors.append({
                        "type": "hallucination",
                        "leg_id": leg.get("leg_id"),
                        "message": f"Hallucinated train number: {train_number}. Not found in RailRadar data.",
                        "critical": True,
                    })

        if mode == "BUS" and bus_number:
            bus_data = state.get("bus_data")
            if bus_data and isinstance(bus_data, dict):
                known_routes = bus_data.get("routes", [])
                known_numbers = [r.get("bus_number") for r in known_routes if isinstance(r, dict)]
                if known_numbers and bus_number not in known_numbers:
                    validation_errors.append({
                        "type": "hallucination",
                        "leg_id": leg.get("leg_id"),
                        "message": f"Hallucinated bus number: {bus_number}. Not found in GTFS data.",
                        "critical": True,
                    })

    # Step 2: Check chronological ordering
    for i in range(len(legs) - 1):
        leg_current = legs[i]
        leg_next = legs[i + 1]

        arrival = leg_current.get("arrival_time")
        departure_next = leg_next.get("departure_time")

        if arrival and departure_next:
            if arrival > departure_next:
                validation_errors.append({
                    "type": "chronology",
                    "leg_id": leg_current.get("leg_id"),
                    "message": f"Chronology error: Leg {i+1} arrives at {arrival} but Leg {i+2} departs at {departure_next}.",
                    "critical": True,
                })

    # Step 3: Check required fields
    for leg in legs:
        for field in REQUIRED_LEG_FIELDS:
            if field not in leg or not leg[field]:
                validation_warnings.append({
                    "type": "missing_field",
                    "leg_id": leg.get("leg_id"),
                    "field": field,
                    "message": f"Missing required field '{field}' in leg {leg.get('leg_id')}.",
                    "critical": False,
                })

    # Step 4: Verify confidence assignment
    for leg in legs:
        confidence = leg.get("confidence", "MEDIUM")
        data_source = leg.get("data_source", "")

        if "AI-guided" in data_source or "Estimated" in data_source:
            if confidence not in ("LOW",):
                leg["confidence"] = "LOW"
                validation_warnings.append({
                    "type": "confidence_correction",
                    "leg_id": leg.get("leg_id"),
                    "message": f"Auto-corrected confidence to LOW for AI-estimated data.",
                    "critical": False,
                })

        if "RailRadar" in data_source:
            if confidence not in ("HIGH", "MEDIUM"):
                leg["confidence"] = "HIGH"

        if "GTFS" in data_source or "Google Maps" in data_source:
            if confidence not in ("HIGH", "MEDIUM"):
                leg["confidence"] = "MEDIUM"

    # Determine validation outcome
    critical_errors = [e for e in validation_errors if e.get("critical", False)]
    non_critical_errors = [e for e in validation_errors if not e.get("critical", False)]

    if critical_errors:
        for err in critical_errors:
            errors.append({"agent": "validate", "message": f"Critical validation error: {err['message']}", "recoverable": True})
        return {
            "itinerary": itinerary,
            "errors": errors,
            "validation_passed": False,
            "validation_errors": validation_errors,
        }

    if non_critical_errors:
        for err in non_critical_errors:
            errors.append({"agent": "validate", "message": f"Validation warning: {err['message']}", "recoverable": False})

    for warning in validation_warnings:
        errors.append({"agent": "validate", "message": f"Validation warning: {warning['message']}", "recoverable": False})

    return {
        "itinerary": itinerary,
        "errors": errors,
        "validation_passed": True,
        "validation_errors": [],
    }
