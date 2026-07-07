from __future__ import annotations

import asyncio
import logging
from typing import Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import TripPlanningState
from app.agents.nodes.geocode_node import geocode_node
from app.agents.nodes.plan_transport_node import plan_transport_node
from app.agents.nodes.train_node import train_node
from app.agents.nodes.bus_node import bus_node
from app.agents.nodes.weather_node import weather_node
from app.agents.nodes.temple_node import temple_node
from app.agents.nodes.hotel_node import hotel_node
from app.agents.nodes.budget_node import budget_node
from app.agents.nodes.synthesis_node import synthesis_node
from app.agents.nodes.validate_node import validate_node
from app.agents.nodes.fallback_node import fallback_node

logger = logging.getLogger(__name__)


async def parallel_agents_node(state: TripPlanningState) -> dict[str, Any]:
    """Runs train, weather, temple, and hotel agents in parallel using asyncio.gather."""
    logger.info("Executing parallel_agents_node...")

    results = await asyncio.gather(
        train_node(state),
        weather_node(state),
        temple_node(state),
        hotel_node(state),
        return_exceptions=True,
    )

    merged: dict[str, Any] = {"errors": list(state.get("errors", []))}

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            agent_names = ["train", "weather", "temple", "hotel"]
            agent = agent_names[i]
            merged["errors"].append({"agent": agent, "message": f"{agent}Agent failed: {result}", "recoverable": True})
        elif isinstance(result, dict):
            merged.update(result)

    return merged


def _route_after_parallel(state: TripPlanningState) -> str:
    """Route after parallel agents - check for critical errors."""
    errors = state.get("errors", [])
    critical_errors = [e for e in errors if not e.get("recoverable", True)]
    if critical_errors:
        return "fallback_node"
    return "bus_node"


def _route_after_validate(state: TripPlanningState) -> str:
    """Route after validation."""
    if state.get("validation_passed", False):
        return "END"
    retry_count = state.get("retry_count", 0)
    if retry_count < 2:
        state["retry_count"] = retry_count + 1
        return "parallel_agents_node"
    return "fallback_node"


def build_graph() -> StateGraph:
    """Build the LangGraph StateGraph for trip planning."""
    logger.info("Building LangGraph trip planning graph...")

    workflow = StateGraph(TripPlanningState)

    # Add all nodes
    workflow.add_node("geocode_node", geocode_node)
    workflow.add_node("plan_transport_node", plan_transport_node)
    workflow.add_node("parallel_agents_node", parallel_agents_node)
    workflow.add_node("bus_node", bus_node)
    workflow.add_node("budget_node", budget_node)
    workflow.add_node("synthesis_node", synthesis_node)
    workflow.add_node("validate_node", validate_node)
    workflow.add_node("fallback_node", fallback_node)

    # Build the graph flow
    workflow.add_edge(START, "geocode_node")
    workflow.add_edge("geocode_node", "plan_transport_node")
    workflow.add_edge("plan_transport_node", "parallel_agents_node")
    workflow.add_conditional_edges(
        "parallel_agents_node",
        _route_after_parallel,
        {"bus_node": "bus_node", "fallback_node": "fallback_node"},
    )
    workflow.add_edge("bus_node", "budget_node")
    workflow.add_edge("budget_node", "synthesis_node")
    workflow.add_edge("synthesis_node", "validate_node")
    workflow.add_conditional_edges(
        "validate_node",
        _route_after_validate,
        {"END": END, "parallel_agents_node": "parallel_agents_node", "fallback_node": "fallback_node"},
    )
    workflow.add_edge("fallback_node", END)

    return workflow


def create_trip_planning_graph() -> Any:
    """Create and compile the trip planning graph with checkpointing."""
    workflow = build_graph()
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    logger.info("Trip planning graph compiled successfully with checkpointing.")
    return compiled_graph


def get_initial_state(request: dict[str, Any]) -> TripPlanningState:
    """Create initial state from API request."""
    return {
        "origin": {
            "text": request.get("origin", ""),
            "coordinates": {},
            "resolved_name": request.get("origin", ""),
        },
        "destination": {
            "text": request.get("destination", ""),
            "coordinates": {},
            "resolved_name": request.get("destination", ""),
        },
        "travel_date": request.get("travel_date", ""),
        "departure_preference": request.get("departure_preference", "morning"),
        "return_time_preference": request.get("return_time_preference", ""),
        "trip_end_time_preference": request.get("trip_end_time_preference", ""),
        "group": request.get("group", {"adults": 1, "children": 0, "seniors": 0}),
        # Normalize preferences: convert string[] to dict if needed
        "preferences": (
            {"budget_tier": "mid", "accessibility": False, "interests": request.get("preferences", [])}
            if isinstance(request.get("preferences"), list)
            else request.get("preferences", {"budget_tier": "mid", "accessibility": False})
        ),
        "geocoded_origin": {},
        "geocoded_destination": {},
        "distance_km": 0,
        "transport_mode_plan": [],
        "train_data": None,
        "bus_data": None,
        "weather_data": None,
        "temple_data": None,
        "hotel_data": None,
        "budget_data": None,
        "itinerary": None,
        "errors": [],
        "retry_count": 0,
        "confidence_summary": {},
        "validation_passed": False,
    }
