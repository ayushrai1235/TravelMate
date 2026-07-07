from __future__ import annotations

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

CHAT_SESSION_TTL = 3600  # 1 hour inactivity TTL
CHAT_MAX_MESSAGES = 20


# In-memory session store fallback
_IN_MEMORY_SESSIONS: dict[str, list[dict[str, str]]] = {}


class ChatMemoryService:
    """Redis-backed conversation memory with in-memory fallback.
    
    Implements ConversationBufferWindowMemory as specified in Memory System.md:
    - Window: Last 20 message pairs
    - Storage: Redis (session-scoped, TTL: 1 hour) with automatic local in-memory fallback
    - Context compression: Summarized after 20 messages
    """
    _redis_unavailable = False

    def __init__(self, redis_client: Optional[Redis] = None):
        self._redis = redis_client if not ChatMemoryService._redis_unavailable else None

    async def _get_redis(self) -> Redis | None:
        """Get or create Redis connection."""
        if ChatMemoryService._redis_unavailable:
            return None
        if self._redis is None:
            try:
                self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Quick test connection with timeout
                import asyncio
                await asyncio.wait_for(self._redis.ping(), timeout=1.0)
            except Exception as e:
                logger.warning(f"Redis unavailable for chat memory: {e}. Falling back to in-memory storage.")
                self._redis = None
                ChatMemoryService._redis_unavailable = True
        return self._redis

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"session:chat:{session_id}"

    @staticmethod
    def _messages_key(session_id: str) -> str:
        return f"session:chat:{session_id}:messages"

    async def create_session(self, session_id: str) -> str:
        """Create a new chat session with TTL."""
        redis = await self._get_redis()
        if redis is None:
            _IN_MEMORY_SESSIONS[session_id] = []
            return session_id
        try:
            key = self._session_key(session_id)
            await redis.setex(key, CHAT_SESSION_TTL, "active")
            await redis.set(self._messages_key(session_id), json.dumps([]))
            logger.info(f"Created chat session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create chat session in Redis, falling back to in-memory: {e}")
            _IN_MEMORY_SESSIONS[session_id] = []
            ChatMemoryService._redis_unavailable = True
        return session_id

    async def get_session_exists(self, session_id: str) -> bool:
        """Check if a chat session exists and is active."""
        redis = await self._get_redis()
        if redis is None:
            return session_id in _IN_MEMORY_SESSIONS
        try:
            key = self._session_key(session_id)
            exists = await redis.exists(key)
            return bool(exists)
        except Exception:
            ChatMemoryService._redis_unavailable = True
            return session_id in _IN_MEMORY_SESSIONS

    async def refresh_session_ttl(self, session_id: str):
        """Refresh session TTL on each message."""
        redis = await self._get_redis()
        if redis is None:
            return
        try:
            key = self._session_key(session_id)
            await redis.expire(key, CHAT_SESSION_TTL)
        except Exception as e:
            logger.error(f"Failed to refresh session TTL: {e}")
            ChatMemoryService._redis_unavailable = True

    async def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the conversation history."""
        redis = await self._get_redis()
        if redis is None:
            if session_id not in _IN_MEMORY_SESSIONS:
                _IN_MEMORY_SESSIONS[session_id] = []
            _IN_MEMORY_SESSIONS[session_id].append({"role": role, "content": content})
            if len(_IN_MEMORY_SESSIONS[session_id]) > CHAT_MAX_MESSAGES:
                _IN_MEMORY_SESSIONS[session_id] = _IN_MEMORY_SESSIONS[session_id][-CHAT_MAX_MESSAGES:]
            logger.debug(f"Added message in-memory for session {session_id}, total: {len(_IN_MEMORY_SESSIONS[session_id])}")
            return
        try:
            messages_key = self._messages_key(session_id)
            messages = json.loads(await redis.get(messages_key) or "[]")
            messages.append({"role": role, "content": content})
            
            # Keep only last CHAT_MAX_MESSAGES
            if len(messages) > CHAT_MAX_MESSAGES:
                messages = messages[-CHAT_MAX_MESSAGES:]
            
            await redis.set(messages_key, json.dumps(messages))
            await self.refresh_session_ttl(session_id)
            logger.debug(f"Added message to session {session_id}, total: {len(messages)}")
        except Exception as e:
            logger.error(f"Failed to add message in Redis, falling back to in-memory: {e}")
            ChatMemoryService._redis_unavailable = True
            if session_id not in _IN_MEMORY_SESSIONS:
                _IN_MEMORY_SESSIONS[session_id] = []
            _IN_MEMORY_SESSIONS[session_id].append({"role": role, "content": content})

    async def get_messages(self, session_id: str) -> list[dict[str, str]]:
        """Get conversation history (last 20 messages)."""
        redis = await self._get_redis()
        if redis is None:
            return _IN_MEMORY_SESSIONS.get(session_id, [])[-CHAT_MAX_MESSAGES:]
        try:
            messages_key = self._messages_key(session_id)
            messages = json.loads(await redis.get(messages_key) or "[]")
            return messages[-CHAT_MAX_MESSAGES:]
        except Exception as e:
            logger.error(f"Failed to get messages from Redis, falling back to in-memory: {e}")
            ChatMemoryService._redis_unavailable = True
            return _IN_MEMORY_SESSIONS.get(session_id, [])[-CHAT_MAX_MESSAGES:]

    async def clear_session(self, session_id: str):
        """Clear a chat session."""
        redis = await self._get_redis()
        if session_id in _IN_MEMORY_SESSIONS:
            del _IN_MEMORY_SESSIONS[session_id]
        if redis is None:
            return
        try:
            key = self._session_key(session_id)
            messages_key = self._messages_key(session_id)
            pipe = redis.pipeline()
            await pipe.delete(key, messages_key)
            await pipe.execute()
            logger.info(f"Cleared chat session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            ChatMemoryService._redis_unavailable = True

    async def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return f"chat_{uuid.uuid4().hex[:16]}"

