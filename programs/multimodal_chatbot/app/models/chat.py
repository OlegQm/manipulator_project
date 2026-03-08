"""
Pydantic models for chat-related request and response schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the mobile application."""

    session_id: str = Field(
        ...,
        description="UUID of the chat session (must be created via POST /api/v1/sessions first)",
    )
    message: str = Field(
        ...,
        min_length=1,
        description="User's text message or question about the image",
    )
    image: Optional[str] = Field(
        default=None,
        description="Base64-encoded image data (JPEG/PNG). Mutually exclusive with image_url",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="Public URL of an image. Mutually exclusive with image (base64)",
    )


class ChatResponse(BaseModel):
    """Response returned after the agent processes a chat message."""

    session_id: str = Field(..., description="Session UUID")
    response: str = Field(..., description="Agent's text response")
    tokens_used: int = Field(
        ..., ge=0, description="Total tokens used in this session so far"
    )
    tokens_remaining: int = Field(
        ..., ge=0, description="Tokens remaining before context window limit"
    )


class TokenLimitExceededResponse(BaseModel):
    """Returned (HTTP 409) when the session's token count exceeds the model context window."""

    session_id: str
    error: str = Field(
        default="Token limit exceeded. The conversation is too long.",
        description="Human-readable error message",
    )
    action: str = Field(
        default="recreate_session",
        description="Action the client should take: create a new session",
    )
