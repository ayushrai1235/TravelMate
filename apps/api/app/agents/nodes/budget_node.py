from __future__ import annotations

import logging
from typing import Any

from app.agents.tools.budget_tools import calculate_budget
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)


async def budget_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: BudgetAgent - computes cost breakdown from all transport legs."""
    logger.info("Executing budget_node...")

    errors = list(state.get("errors", []))
    preferences = state.get("preferences", {})
    budget_tier = preferences.get("budget_tier", "mid")
    group = state.get("group", {"adults": 1, "children": 0, "seniors": 0})

    legs = _extract_legs(state)

    budget_data = None
    try:
        result = await calculate_budget.ainvoke(
            legs=legs,
            group_adults=group.get("adults", 1),
            group_children=group.get("children", 0),
            group_seniors=group.get("seniors", 0),
            days=1,
            budget_tier=budget_tier,
        )
        budget_data = result
    except Exception as e:
        logger.error(f"BudgetAgent execution failed: {e}")
        errors.append({"agent": "budget", "message": f"BudgetAgent failed: {e}", "recoverable": True})

    return {
        "budget_data": budget_data,
        "errors": errors,
    }


def _extract_legs(state: TripPlanningState) -> list[dict[str, Any]]:
    """Extract transport legs from state data."""
    legs = []

    # Auto first-mile
    distance_km = state.get("distance_km", 0)
    if distance_km:
        legs.append({
            "mode": "AUTO",
            "description": f"Auto to transit hub ({distance_km} km)",
            "cost_inr": {"min": max(50, int(distance_km * 15)), "max": max(80, int(distance_km * 25))},
            "confidence": "MEDIUM",
            "data_source": "Google Maps Distance Matrix",
        })

    # Train legs
    train_data = state.get("train_data")
    if train_data and isinstance(train_data, dict) and train_data.get("trains"):
        for train in train_data["trains"]:
            legs.append({
                "mode": "TRAIN",
                "description": f"{train.get('name', '')} ({train.get('number', '')})",
                "departure_time": train.get("departure_time", ""),
                "arrival_time": train.get("arrival_time", ""),
                "duration_minutes": train.get("duration_minutes", 0),
                "cost_inr": _extract_train_cost(train),
                "confidence": "HIGH",
                "data_source": "RailRadar",
            })

    # Bus legs
    bus_data = state.get("bus_data")
    if bus_data and isinstance(bus_data, dict) and bus_data.get("routes"):
        for route in bus_data["routes"]:
            legs.append({
                "mode": "BUS",
                "description": route.get("route_name", route.get("operator", "Bus")),
                "cost_inr": route.get("fare_inr", {"min": 30, "max": 60}),
                "confidence": "MEDIUM",
                "data_source": route.get("data_source", "GTFS"),
            })

    # Walking last-mile
    legs.append({
        "mode": "WALK",
        "description": "Walking to final destination",
        "cost_inr": {"min": 0, "max": 0},
        "confidence": "HIGH",
        "data_source": "Estimated",
    })

    return legs


def _extract_train_cost(train: dict) -> dict:
    """Extract cost range from train data."""
    classes = train.get("classes_available", [])
    if not classes:
        return {"min": 180, "max": 800}

    fare_map = {"SL": (180, 350), "3A": (500, 900), "2A": (800, 1400), "1A": (1500, 2500), "CC": (250, 450), "2S": (60, 150)}
    best_class = classes[0]
    fare_range = fare_map.get(best_class, (200, 500))
    return {"min": fare_range[0], "max": fare_range[1]}
