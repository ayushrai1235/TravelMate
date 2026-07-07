import json
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from redis.asyncio import Redis

from app.core.config import settings
from app.agents.memory import ChatMemoryService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message")
    history: list[ChatMessage] = Field(default_factory=list, description="List of previous messages")
    session_id: str | None = Field(default=None, description="Chat session ID for context persistence")


@router.post("")
async def chat_endpoint(payload: ChatRequest, request: Request) -> StreamingResponse:
    memory_service = ChatMemoryService()
    
    # Generate or use existing session ID
    session_id = payload.session_id or str(uuid.uuid4())
    
    # Initialize session in Redis
    await memory_service.create_session(session_id)
    
    # Get conversation history from Redis
    redis_messages = await memory_service.get_messages(session_id)
    
    # Build messages list: system + history + current message
    chat_prompt = """You are the TravelMate AI travel assistant. You are helping a user with their
planned journey.

YOUR CAPABILITIES:
1. Answer questions about the itinerary
2. Suggest modifications (will trigger a replan)
3. Provide general travel advice
4. Explain confidence scores and data sources

RULES:
1. When asked about data that IS in the itinerary context, provide it directly.
2. When asked about data NOT in context (e.g., "which platform?"), say:
   "I don't have confirmed real-time data for [topic]. Based on your itinerary,
   [relevant context]. For the most accurate information, check [official source]."
3. NEVER fabricate transport data.
4. If the user asks to modify their trip, extract the modification intent as JSON:
   {"modification_type": "change_departure_time", "new_value": "06:00"}
5. Be concise, friendly, and culturally sensitive for Indian travelers.
6. For pilgrimage questions, be respectful of religious practices.

MODIFICATION TYPES:
- change_departure_time
- change_transport_mode
- add_stop
- remove_stop
- change_budget_tier
- change_class_preference
"""

    messages = [SystemMessage(content=chat_prompt)]
    
    # Add Redis conversation history
    for msg in redis_messages:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") in ["assistant", "ai"]:
            messages.append(AIMessage(content=msg.get("content", "")))
    
    # Add frontend history
    for msg in payload.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role in ["assistant", "ai"]:
            messages.append(AIMessage(content=msg.content))
            
    messages.append(HumanMessage(content=payload.message))

    async def event_stream():
        try:
            if not settings.GEMINI_API_KEY:
                yield f"data: {json.dumps({'content': 'I am TravelMate AI. Please configure the GEMINI_API_KEY in the backend .env to enable real AI responses.'})}\n\n"
                yield "data: [DONE]\n\n"
                # Store the exchange even without API key
                await memory_service.add_message(session_id, "user", payload.message)
                await memory_service.add_message(session_id, "assistant", "I am TravelMate AI. Please configure the GEMINI_API_KEY.")
                return

            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL_NAME or "gemini-3.5-flash",
                temperature=0.7,
                google_api_key=settings.GEMINI_API_KEY
            )
            
            full_response = ""
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield f"data: {json.dumps({'content': chunk.content})}\n\n"
            
            # Store the exchange in Redis memory
            await memory_service.add_message(session_id, "user", payload.message)
            await memory_service.add_message(session_id, "assistant", full_response)
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
            
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Request-ID": request.headers.get("x-request-id", ""),
        }
    )
