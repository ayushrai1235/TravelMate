from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.hotel_tools import search_hotels
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

HOTEL_AGENT_SYSTEM_PROMPT = """
You are HotelAgent, an accommodation suggestion agent for travel planning.

YOUR TOOLS:
- search_hotels: Search for hotels near a location via Google Maps Places API

RULES:
1. Search for hotels near the destination.
2. Include dharamshalas for pilgrimage destinations.
3. Rank by proximity, price, rating, veg food availability, and accessibility.
4. Confidence is MEDIUM for Places API data.

OUTPUT: JSON matching the HotelData schema with hotels and dharamshalas.
"""


def get_hotel_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=1024,
        convert_system_message_to_human=False
    )
    tools = [search_hotels]
    prompt = ChatPromptTemplate.from_messages([
        ("system", HOTEL_AGENT_SYSTEM_PROMPT),
        ("human", "Search for hotels near {location} with budget tier {budget_tier}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)


async def hotel_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: HotelAgent - suggests accommodation options near destination."""
    logger.info("Executing hotel_node...")

    errors = list(state.get("errors", []))
    preferences = state.get("preferences", {})
    budget_tier = preferences.get("budget_tier", "mid")
    destination = state.get("destination", {}).get("text", "")
    travel_date = state.get("travel_date", "")

    hotel_data = []

    try:
        agent = get_hotel_agent_executor()
        result = await agent.ainvoke({
            "messages": [("user", f"Search for hotels near {destination} with budget tier {budget_tier}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                parsed = json.loads(output.strip())
                hotel_data = parsed.get("hotels", [])
            except json.JSONDecodeError:
                hotel_data = []
        else:
            hotel_data = output.get("hotels", []) if isinstance(output, dict) else []
    except Exception as e:
        logger.error(f"HotelAgent execution failed: {e}")

    return {
        "hotel_data": hotel_data,
        "errors": errors,
    }
