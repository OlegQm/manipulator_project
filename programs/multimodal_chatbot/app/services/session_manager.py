"""
Redis-backed session manager.

Handles creation, retrieval, deletion of chat sessions,
message storage, token counting (tiktoken), and session expiry checks.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
import tiktoken

from app.config import Settings
from app.models.session import ChatMessageRecord, SessionInfoResponse

logger = logging.getLogger(__name__)

# Module-level reference set during app startup, used by tools
_session_manager: Optional["SessionManager"] = None


def get_session_manager() -> "SessionManager":
    """Return the globally registered SessionManager instance."""
    if _session_manager is None:
        raise RuntimeError("SessionManager not initialized yet")
    return _session_manager


def set_session_manager(manager: "SessionManager") -> None:
    """Register the SessionManager instance for global access (called at startup)."""
    global _session_manager
    _session_manager = manager


class SessionManager:
    """Manages chat sessions stored in Redis."""

    def __init__(self, redis_client: redis.Redis, settings: Settings) -> None:
        """
        Initialize the session manager.

        Args:
            redis_client: Async Redis client instance.
            settings: Application settings.
        """
        self._redis = redis_client
        self._settings = settings
        # tiktoken encoder for the model (fall back to cl100k_base if not found)
        try:
            self._encoder = tiktoken.encoding_for_model(settings.openai_model)
        except KeyError:
            self._encoder = tiktoken.get_encoding("cl100k_base")

    # ── Key helpers ───────────────────────────────────────────────────

    @staticmethod
    def _meta_key(session_id: str) -> str:
        """Return the Redis key for session metadata."""
        return f"session:{session_id}:meta"

    @staticmethod
    def _messages_key(session_id: str) -> str:
        """Return the Redis key for session messages list."""
        return f"session:{session_id}:messages"

    @staticmethod
    def _image_key(session_id: str, image_id: str) -> str:
        """Return the Redis key for a stored image."""
        return f"session:{session_id}:image:{image_id}"

    # ── CRUD ──────────────────────────────────────────────────────────

    async def create_session(self) -> tuple[str, datetime]:
        """
        Create a new chat session.

        Returns:
            Tuple of (session_id, created_at).
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        await self._redis.hset(
            self._meta_key(session_id),
            mapping={"created_at": now_iso, "last_activity": now_iso},
        )
        logger.info("Created session %s", session_id)
        return session_id, now

    async def session_exists(self, session_id: str) -> bool:
        """Check whether a session with the given ID exists in Redis."""
        return await self._redis.exists(self._meta_key(session_id)) > 0

    async def get_session_info(self, session_id: str) -> Optional[SessionInfoResponse]:
        """
        Retrieve metadata for a session.

        Returns:
            SessionInfoResponse or None if the session does not exist.
        """
        meta = await self._redis.hgetall(self._meta_key(session_id))
        if not meta:
            return None

        message_count = await self._redis.llen(self._messages_key(session_id))
        return SessionInfoResponse(
            session_id=session_id,
            created_at=datetime.fromisoformat(meta["created_at"]),
            last_activity=datetime.fromisoformat(meta["last_activity"]),
            message_count=message_count,
        )

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.

        Returns:
            True if the session existed and was deleted.
        """
        meta_key = self._meta_key(session_id)
        msgs_key = self._messages_key(session_id)

        # Collect image keys belonging to this session
        image_keys: list[str] = []
        async for key in self._redis.scan_iter(
            match=f"session:{session_id}:image:*"
        ):
            image_keys.append(key)

        keys_to_delete = [meta_key, msgs_key] + image_keys
        deleted = await self._redis.delete(*keys_to_delete)
        if deleted > 0:
            logger.info("Deleted session %s (%d image(s))", session_id, len(image_keys))
            return True
        return False

    # ── Messages ──────────────────────────────────────────────────────

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        has_image: bool = False,
        image_id: Optional[str] = None,
    ) -> None:
        """
        Append a message to the session history and update last_activity.

        Args:
            session_id: Session UUID.
            role: 'user' or 'assistant'.
            content: Text content of the message.
            has_image: Whether the message included an image attachment.
            image_id: UUID of the stored image (if any).
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        record = {
            "role": role,
            "content": content,
            "has_image": has_image,
            "image_id": image_id,
            "timestamp": now_iso,
        }
        pipe = self._redis.pipeline()
        pipe.rpush(self._messages_key(session_id), json.dumps(record))
        pipe.hset(self._meta_key(session_id), "last_activity", now_iso)
        await pipe.execute()

    async def get_history(self, session_id: str) -> list[ChatMessageRecord]:
        """
        Retrieve the full message history for a session.

        Returns:
            Ordered list of ChatMessageRecord objects.
        """
        raw_messages = await self._redis.lrange(self._messages_key(session_id), 0, -1)
        records: list[ChatMessageRecord] = []
        for raw in raw_messages:
            data = json.loads(raw)
            records.append(ChatMessageRecord(**data))
        return records

    # ── Image storage ─────────────────────────────────────────────────

    async def store_image(
        self, session_id: str, image_b64: str,
    ) -> str:
        """
        Store a base64-encoded image in Redis, tied to the session lifetime.

        Args:
            session_id: Session UUID that owns this image.
            image_b64: Base64-encoded image data.

        Returns:
            A unique image_id that can be used to retrieve the image.
        """
        image_id = str(uuid.uuid4())
        key = self._image_key(session_id, image_id)
        await self._redis.set(key, image_b64)
        logger.info("Stored image %s for session %s", image_id, session_id)
        return image_id

    async def get_image(self, session_id: str, image_id: str) -> Optional[str]:
        """
        Retrieve a stored base64-encoded image.

        Args:
            session_id: Session UUID that owns the image.
            image_id: The image identifier returned by store_image.

        Returns:
            Base64-encoded image data, or None if not found.
        """
        key = self._image_key(session_id, image_id)
        return await self._redis.get(key)

    # ── Token counting ────────────────────────────────────────────────

    async def count_tokens(self, session_id: str) -> int:
        """
        Count the total number of tokens in the session history using tiktoken.

        Returns:
            Total token count across all messages.
        """
        raw_messages = await self._redis.lrange(self._messages_key(session_id), 0, -1)
        total_tokens = 0
        for raw in raw_messages:
            data = json.loads(raw)
            # Count tokens in the text content
            total_tokens += len(self._encoder.encode(data["content"]))
            # Rough overhead per message (role, formatting)
            total_tokens += 4
        return total_tokens

    async def check_token_limit(self, session_id: str) -> bool:
        """
        Check whether the session is still within the token limit.

        Returns:
            True if total tokens < MAX_CONTEXT_TOKENS.
        """
        total = await self.count_tokens(session_id)
        return total < self._settings.max_context_tokens

    async def get_token_stats(self, session_id: str) -> tuple[int, int]:
        """
        Get token usage and remaining capacity for a session.

        Returns:
            Tuple of (tokens_used, tokens_remaining).
        """
        used = await self.count_tokens(session_id)
        remaining = max(0, self._settings.max_context_tokens - used)
        return used, remaining

    # ── Cleanup support ───────────────────────────────────────────────

    async def get_all_session_ids(self) -> list[str]:
        """
        Scan Redis for all session meta keys and extract session IDs.

        Returns:
            List of session ID strings.
        """
        session_ids: list[str] = []
        async for key in self._redis.scan_iter(match="session:*:meta"):
            # key format: "session:<uuid>:meta"
            parts = key.split(":")
            if len(parts) == 3:
                session_ids.append(parts[1])
        return session_ids

    async def get_last_activity(self, session_id: str) -> Optional[datetime]:
        """
        Get the last_activity timestamp for a session.

        Returns:
            datetime or None if session does not exist.
        """
        val = await self._redis.hget(self._meta_key(session_id), "last_activity")
        if val is None:
            return None
        return datetime.fromisoformat(val)
