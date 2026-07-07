from __future__ import annotations

import logging
from typing import Any

from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)


def plan_transport_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: Determines transport mode combinations based on distance (RouteAgent)."""
    logger.info("Executing plan_transport_node...")

    geocoded_origin = state.get("geocoded_origin", {})
    geocoded_destination = state.get("geocoded_destination", {})
    errors = list(state.get("errors", []))

    origin_lat = geocoded_origin.get("lat", 0)
    origin_lng = geocoded_origin.get("lng", 0)
    dest_lat = geocoded_destination.get("lat", 0)
    dest_lng = geocoded_destination.get("lng", 0)

    import math
    lat_diff = dest_lat - origin_lat
    lng_diff = dest_lng - origin_lng
    distance_km = math.sqrt(lat_diff ** 2 + lng_diff ** 2) * 111.0

    distance_km = round(distance_km, 1)
    logger.info(f"Calculated distance: {distance_km} km")

    mode_plan: list[str] = ["AUTO"]

    if distance_km < 5:
        mode_plan = ["WALK"]
        logger.info("Distance < 5km: Walking only")
    elif distance_km < 50:
        mode_plan = ["AUTO", "BUS", "WALK"]
        logger.info("Distance 5-50km: Auto + Bus + Walk")
    elif distance_km < 300:
        mode_plan = ["AUTO", "TRAIN", "BUS", "WALK"]
        logger.info("Distance 50-300km: Auto + Train + Bus + Walk")
    elif distance_km < 800:
        mode_plan = ["AUTO", "TRAIN", "BUS", "WALK"]
        also_consider_flight = True
        logger.info(f"Distance 300-800km: Auto + Train + Bus + Walk (also considering flight)")
    else:
        mode_plan = ["AUTO", "FLIGHT", "WALK"]
        also_consider_train = True
        logger.info(f"Distance > 800km: Auto + Flight + Walk (also considering train)")

    return {
        "distance_km": distance_km,
        "transport_mode_plan": mode_plan,
        "errors": errors,
    }
