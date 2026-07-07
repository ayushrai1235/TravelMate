from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.bus_tools import search_gtfs_routes, find_nearest_bus_stop
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

BUS_AGENT_SYSTEM_PROMPT = """
You are BusAgent, a specialized Indian bus route planning agent.

YOUR TOOLS:
- search_gtfs_routes: Search bus routes in GTFS feeds
- find_nearest_bus_stop: Find bus stops near coordinates

RULES:
1. NEVER invent a bus route number.
2. Try GTFS first, then provide guidance.
3. If no confirmed data exists, provide route guidance with confidence=LOW.

FALLBACK FORMAT (when no confirmed data):
{
  "routes": [],
  "ai_guidance": "From [stop], buses to [destination] depart approximately every [N] minutes. Ask at the bus stand. Fare: approximately Rs.[estimate].",
  "fallback_used": true
}

OUTPUT: JSON matching the BusData schema.
"""


def get_bus_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=1024,
        convert_system_message_to_human=False
    )
    tools = [search_gtfs_routes, find_nearest_bus_stop]
    prompt = ChatPromptTemplate.from_messages([
        ("system", BUS_AGENT_SYSTEM_PROMPT),
        ("human", "Find bus routes from {origin} to {destination} on {date}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)


async def bus_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: BusAgent - finds bus routes connecting transit hub to final destination."""
    logger.info("Executing bus_node...")

    errors = list(state.get("errors", []))
    mode_plan = state.get("transport_mode_plan", [])

    if "BUS" not in mode_plan:
        return {"bus_data": None, "errors": errors}

    try:
        agent = get_bus_agent_executor()
        origin = state.get("geocoded_origin", {}).get("resolved_name", "")
        destination = state.get("geocoded_destination", {}).get("resolved_name", "")
        travel_date = state.get("travel_date", "")

        result = await agent.ainvoke({
            "messages": [("user", f"Find bus routes from {origin} to {destination} on {travel_date}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                bus_data = json.loads(output.strip())
            except json.JSONDecodeError:
                bus_data = {"routes": [], "ai_guidance": "Bus route data unavailable. Ask at the bus stand.", "fallback_used": True}
        else:
            bus_data = output

        return {"bus_data": bus_data, "errors": errors}
    except Exception as e:
        logger.error(f"BusAgent execution failed: {e}")
        errors.append({"agent": "bus", "message": f"BusAgent failed: {e}", "recoverable": True})
        return {
            "bus_data": {"routes": [], "ai_guidance": "Bus route data unavailable. Ask at the bus stand.", "fallback_used": True},
            "errors": errors,
        }
