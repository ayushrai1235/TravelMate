import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.train_tools import (
    search_trains, get_train_info, get_train_running_status
)

logger = logging.getLogger(__name__)

# System prompt based on Prompt Library docs
TRAIN_AGENT_SYSTEM_PROMPT = """
You are a specialized Indian Railways schedule lookup agent.

YOUR TOOLS:
- search_trains: Find trains between two stations on a date
- get_train_info: Get static schedule and info for a specific train
- get_train_running_status: Check if a train is on time or delayed

RULES:
1. Use ONLY the data returned by your tools. The tools connect directly to the production Railway Service.
2. NEVER invent a train number, name, departure time, or platform number.
3. If search_trains returns no results, set no_trains_found=true.
4. If running_status is not available, set it to null — do NOT assume "On Time".
5. Check if the train runs on the requested day of the week.

CONFIDENCE LEVELS:
- Tool data < 30 minutes old: HIGH
- Cached data (30-60 minutes): MEDIUM
- No data available: null (do not include)

OUTPUT: JSON matching the TrainData schema.
"""

def get_train_agent_executor():
    """Initialize and return the TrainAgent executor with tools attached."""
    
    # Initialize the LLM (Gemini 3.5 Flash or equivalent based on config)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME, 
        google_api_key=settings.GEMINI_API_KEY or "mock",
        temperature=0,
        max_output_tokens=2048,
        convert_system_message_to_human=False
    )
    
    # Tools are bound to RailwayService internally
    tools = [search_trains, get_train_info, get_train_running_status]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TRAIN_AGENT_SYSTEM_PROMPT),
        ("human", "Find trains from {origin_station} to {destination_station} on {date}."),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    return create_react_agent(llm, tools, prompt=prompt)

async def train_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for TrainAgent."""
    logger.info("Executing train_node...")
    
    # Extract needed state
    origin = state.get("geocoded_origin", {}).get("resolved_name", state.get("origin", {}).get("text", ""))
    destination = state.get("geocoded_destination", {}).get("resolved_name", state.get("destination", {}).get("text", ""))
    date = state.get("travel_date", "")
    
    executor = get_train_agent_executor()
    
    try:
        result = await executor.ainvoke({
            "origin_station": origin,
            "destination_station": destination,
            "date": date
        })
        
        # Result output should be a JSON string or dict parsed by the agent based on instructions
        import json
        output = result.get("output", "{}")
        if isinstance(output, str):
            try:
                # Strip markdown codeblocks if LLM includes them
                if output.startswith("```json"):
                    output = output[7:-3]
                train_data = json.loads(output)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from TrainAgent")
                train_data = None
        else:
            train_data = output
            
        return {"train_data": train_data}
    except Exception as e:
        logger.error(f"TrainAgent execution failed: {str(e)}")
        # Following LangGraph.md §5 Error Recovery
        return {
            "train_data": None, 
            "errors": [{"agent": "train", "message": str(e)}]
        }
