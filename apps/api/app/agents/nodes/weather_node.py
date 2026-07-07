from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.weather_tools import get_weather_forecast, get_weather_alerts
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

WEATHER_AGENT_SYSTEM_PROMPT = """
You are WeatherAgent, a weather information agent for travel planning.

YOUR TOOLS:
- get_weather_forecast: Get 7-day forecast for coordinates
- get_weather_alerts: Get active weather alerts

RULES:
1. Fetch weather for origin, all transit cities, and destination.
2. Highlight any conditions that could affect travel:
   - Heavy rain (>20mm)
   - Extreme heat (>45C)
   - Fog (winter, north India)
   - Cyclone warnings
3. Confidence is always HIGH (direct from OpenWeatherMap API).
4. Include data_source and timestamp.

OUTPUT: JSON matching the WeatherData schema.
"""


def get_weather_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=1024,
        convert_system_message_to_human=False
    )
    tools = [get_weather_forecast, get_weather_alerts]
    prompt = ChatPromptTemplate.from_messages([
        ("system", WEATHER_AGENT_SYSTEM_PROMPT),
        ("human", "Get weather forecast for coordinates lat={lat}, lng={lng} on {date}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)


async def weather_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: WeatherAgent - fetches weather forecasts for all relevant locations."""
    logger.info("Executing weather_node...")

    errors = list(state.get("errors", []))
    geocoded_origin = state.get("geocoded_origin", {})
    geocoded_destination = state.get("geocoded_destination", {})
    travel_date = state.get("travel_date", "")

    weather_data = {}

    try:
        origin_lat = geocoded_origin.get("lat", 0)
        origin_lng = geocoded_origin.get("lng", 0)

        agent = get_weather_agent_executor()
        result = await agent.ainvoke({
            "messages": [("user", f"Get weather forecast for coordinates lat={origin_lat}, lng={origin_lng} on {travel_date}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                weather_data["origin"] = json.loads(output.strip())
            except json.JSONDecodeError:
                weather_data["origin"] = {"error": "Failed to parse weather data", "forecasts": [], "alerts": []}
        else:
            weather_data["origin"] = output
    except Exception as e:
        logger.error(f"WeatherAgent origin failed: {e}")
        weather_data["origin"] = {"error": str(e), "forecasts": [], "alerts": []}

    try:
        dest_lat = geocoded_destination.get("lat", 0)
        dest_lng = geocoded_destination.get("lng", 0)

        agent = get_weather_agent_executor()
        result = await agent.ainvoke({
            "messages": [("user", f"Get weather forecast for coordinates lat={dest_lat}, lng={dest_lng} on {travel_date}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                weather_data["destination"] = json.loads(output.strip())
            except json.JSONDecodeError:
                weather_data["destination"] = {"error": "Failed to parse weather data", "forecasts": [], "alerts": []}
        else:
            weather_data["destination"] = output
    except Exception as e:
        logger.error(f"WeatherAgent destination failed: {e}")
        weather_data["destination"] = {"error": str(e), "forecasts": [], "alerts": []}

    return {
        "weather_data": weather_data,
        "errors": errors,
    }
