"""
Pydantic models for session-related request and response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreateResponse(BaseModel):
    """Returned when a new chat session is created."""

    session_id: str = Field(..., description="Newly generated session UUID")
    created_at: datetime = Field(..., description="Timestamp when the session was created")


class SessionInfoResponse(BaseModel):
    """Detailed information about an existing session."""

    session_id: str
    created_at: datetime
    last_activity: datetime = Field(
        ..., description="Timestamp of the last message in this session"
    )
    message_count: int = Field(..., ge=0, description="Total messages in the session")


class SessionDeleteResponse(BaseModel):
    """Returned when a session deletion is requested."""

    session_id: str
    deleted: bool = Field(
        ..., description="True if the session was found and deleted, False otherwise"
    )


class ChatMessageRecord(BaseModel):
    """A single message stored in the session history."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")
    has_image: bool = Field(
        default=False,
        description="Whether this message included an image attachment",
    )
    image_id: Optional[str] = Field(
        default=None,
        description="UUID of the image stored in Redis (if any)",
    )
    timestamp: datetime = Field(..., description="When this message was recorded")
