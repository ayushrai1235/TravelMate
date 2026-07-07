from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.train_tools import search_trains, get_train_info, get_train_running_status
from app.agents.state import TripPlanningState

logger = logging.getLogger(__name__)

TRAIN_AGENT_SYSTEM_PROMPT = """
You are TrainAgent, a specialized AI that finds accurate Indian Railways train schedules.

YOUR TOOLS:
- search_trains: Find trains between two stations on a date
- get_train_info: Get static schedule and info for a specific train
- get_train_running_status: Check if a train is on time or delayed

RULES:
1. Use ONLY the data returned by your tools.
2. NEVER invent a train number, name, departure time, or platform number.
3. If search_trains returns no results, set no_trains_found=true.
4. If running_status is not available, set it to null.
5. Check if the train runs on the requested day of the week.

CONFIDENCE LEVELS:
- Tool data < 30 minutes old: HIGH
- Cached data (30-60 minutes): MEDIUM
- No data available: null (do not include)

OUTPUT: JSON matching the TrainData schema.
"""


def get_train_agent_executor():
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=2048,
        convert_system_message_to_human=False
    )
    tools = [search_trains, get_train_info, get_train_running_status]
    prompt = ChatPromptTemplate.from_messages([
        ("system", TRAIN_AGENT_SYSTEM_PROMPT),
        ("human", "Find trains from {origin_station} to {destination_station} on {date}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)


async def train_node(state: TripPlanningState) -> dict[str, Any]:
    """LangGraph node: TrainAgent - queries real Indian Railways train schedule data."""
    logger.info("Executing train_node...")

    errors = list(state.get("errors", []))
    origin = state.get("geocoded_origin", {}).get("resolved_name", state.get("origin", {}).get("text", ""))
    destination = state.get("geocoded_destination", {}).get("resolved_name", state.get("destination", {}).get("text", ""))
    travel_date = state.get("travel_date", "")

    mode_plan = state.get("transport_mode_plan", [])
    if "TRAIN" not in mode_plan:
        return {"train_data": None, "errors": errors}

    try:
        agent = get_train_agent_executor()
        result = await agent.ainvoke({
            "messages": [("user", f"Find trains from {origin} to {destination} on {travel_date}")],
        })

        output = result.get("messages", [])[-1].content if isinstance(result, dict) and result.get("messages") else "{}"
        if isinstance(output, str):
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3].replace("json", "")
            try:
                train_data = json.loads(output.strip())
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from TrainAgent")
                train_data = {"no_trains_found": True, "trains": [], "fallback_suggestion": "Check IRCTC for schedules"}
        else:
            train_data = output

        return {"train_data": train_data, "errors": errors}
    except Exception as e:
        logger.error(f"TrainAgent execution failed: {e}")
        errors.append({"agent": "train", "message": f"TrainAgent failed: {e}", "recoverable": True})
        return {
            "train_data": {"no_trains_found": True, "trains": [], "fallback_suggestion": "Check IRCTC for schedules"},
            "errors": errors,
        }
