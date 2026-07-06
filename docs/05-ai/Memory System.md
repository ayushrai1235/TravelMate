# Memory System.md

# TravelMate AI — AI Memory System

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Memory Architecture

| Memory Type | Scope | Storage | TTL | Purpose |
|---|---|---|---|---|
| **Working Memory** | Single trip planning request | LangGraph State (in-process) | Request duration | Carry intermediate results between agents |
| **Conversation Memory** | Single chat session | Redis | 1 hour inactivity | Maintain chat context for itinerary Q&A |
| **User Preference Memory** | Per user, persistent | PostgreSQL | Until user changes | Home address, transport class, budget, accessibility |
| **Trip History Memory** | Per user, persistent | PostgreSQL | 24 months | Past trips for quick re-plan and pattern learning |
| **Cache Memory** | Global, shared | Redis | Varies per data type | Avoid redundant API calls for identical queries |

---

## 2. Working Memory (LangGraph State)

The `TripPlanningState` TypedDict carries all intermediate results through the agent graph. This memory exists only during a single request and is NOT persisted.

**State fields grow as agents complete:**
```
Step 1: {origin, destination, date} → geocode_node
Step 2: + {geocoded_origin, geocoded_destination} → plan_transport_node
Step 3: + {transport_mode_plan} → parallel agents
Step 4: + {train_data, weather_data, temple_data, hotel_data} → bus_node
Step 5: + {bus_data} → budget_node
Step 6: + {budget_data} → synthesis_node
Step 7: + {itinerary} → validate_node
Step 8: + {validation_result} → END
```

**Checkpointing:** LangGraph's `MemorySaver` saves state after each node. If bus_node fails, retry resumes from bus_node with train_data already populated.

---

## 3. Conversation Memory (Chat)

### 3.1 Implementation

Uses LangChain's `ConversationBufferWindowMemory` backed by Redis:

```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=20,                    # Keep last 20 message pairs
    return_messages=True,
    memory_key="chat_history",
    input_key="input",
    output_key="output"
)
```

### 3.2 Context Injection

The chat session receives:
1. System prompt (ChatAgent prompt from Prompt Library)
2. Current itinerary JSON (injected as system context)
3. Last 20 messages from conversation history
4. User preferences (from PostgreSQL)

### 3.3 Context Window Management

Gemini 3.5 Flash has a 1M+ token context window. Budget allocation:

| Section | Max Tokens | Content |
|---|---|---|
| System prompt | 500 | ChatAgent instructions |
| Itinerary context | 2,000 | Full itinerary JSON |
| User preferences | 200 | Compact preference object |
| Conversation history | 4,000 | Last 20 messages |
| Current user message | 500 | User's latest query |
| Response budget | 1,000 | AI response |
| **Total** | **8,200** | Per chat turn |

When conversation exceeds 20 messages, older messages are summarized:
```python
if len(messages) > 20:
    summary = await llm.invoke(
        f"Summarize this conversation in 3 sentences: {older_messages}"
    )
    memory.save_context({"input": "SUMMARY"}, {"output": summary})
```

### 3.4 Session Management

- Session ID: Generated on first chat interaction, stored in Redis
- TTL: 1 hour of inactivity
- Cleanup: Redis TTL auto-expires; no manual cleanup needed
- New itinerary: Clears conversation memory (fresh context)

---

## 4. User Preference Memory

Stored in PostgreSQL `user_preferences` table:

| Field | Type | Usage |
|---|---|---|
| `home_address` | text | Default origin for trip planning |
| `preferred_transport_class` | enum | SL, 3A, 2A (default class for train legs) |
| `budget_tier` | enum | budget, mid, premium |
| `accessibility_senior` | boolean | Enables senior-friendly routing |
| `accessibility_wheelchair` | boolean | Enables wheelchair-accessible routing |
| `language` | text | UI and chat language preference |
| `notification_email` | boolean | Email notification preference |
| `notification_push` | boolean | Push notification preference |

**Loading:** Preferences loaded from DB on session start and cached in Redis for the session duration.

---

## 5. Trip History Memory

Past trips are searchable for:
1. **Quick re-plan:** "Plan the same trip as last month" → load saved trip, update date
2. **Pattern detection (future v2.0):** Identify user's common routes for personalized suggestions
3. **Budget tracking:** Compare actual vs estimated costs across trips

---

## 6. No Long-Term AI Learning

TravelMate AI does NOT use fine-tuning or long-term memory to learn from individual users. All AI behavior comes from:
1. System prompts (versioned, deterministic)
2. Tool calls (real-time data)
3. User preferences (explicit, user-controlled)

This is an intentional privacy decision: user interactions are not used to train AI models.
