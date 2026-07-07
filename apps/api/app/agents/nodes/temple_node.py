from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.temple_tools import get_temple_by_name, get_temple_by_coordinates
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

TEMPLE_AGENT_SYSTEM_PROMPT = """
You are TempleAgent, a temple and religious site information agent.

YOUR TOOLS:
- get_temple_by_name: Look up temple in database by name
- get_temple_by_coordinates: Find temples near coordinates

RULES:
1. Use ONLY the temple database for timing information.
2. If the temple is not in the database, return not_found=true with external links.
3. Include dress code and photography policy if available.
4. Confidence is HIGH for database matches, null for not found.

OUTPUT: JSON matching the TempleData schema.
"""


def get_temple_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=1024,
        convert_system_message_to_human=False
    )
    tools = [get_temple_by_name, get_temple_by_coordinates]
    prompt = ChatPromptTemplate.from_messages([
        ("system", TEMPLE_AGENT_SYSTEM_PROMPT),
        ("human", "Find temple information for {temple_name} near coordinates lat={lat}, lng={lng}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)


async def temple_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: TempleAgent - retrieves temple/religious site information."""
    logger.info("Executing temple_node...")

    errors = list(state.get("errors", []))
    destination_text = state.get("destination", {}).get("text", "")
    geocoded_dest = state.get("geocoded_destination", {})
    dest_lat = geocoded_dest.get("lat", 0)
    dest_lng = geocoded_dest.get("lng", 0)

    temple_data = None

    try:
        agent = get_temple_agent_executor()
        result = await agent.ainvoke({
            "messages": [("user", f"Find temple information for {destination_text} near coordinates lat={dest_lat}, lng={dest_lng}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                temple_data = json.loads(output.strip())
            except json.JSONDecodeError:
                temple_data = {"temple": None, "not_found": True, "external_links": {"google_maps": f"https://maps.google.com/?q={destination_text}"}}
        else:
            temple_data = output
    except Exception as e:
        logger.error(f"TempleAgent execution failed: {e}")
        temple_data = {"temple": None, "not_found": True, "external_links": {"google_maps": f"https://maps.google.com/?q={destination_text}"}}

    return {
        "temple_data": temple_data,
        "errors": errors,
    }
