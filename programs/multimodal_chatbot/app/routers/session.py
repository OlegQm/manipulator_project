"""
Session management endpoints.

Provides CRUD operations for chat sessions: create, get info, get history, delete.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from app.models.session import (
    ChatMessageRecord,
    SessionCreateResponse,
    SessionDeleteResponse,
    SessionInfoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse, status_code=201)
async def create_session(request: Request) -> SessionCreateResponse:
    """
    Create a new chat session.

    The mobile app must call this before sending any chat messages.
    Returns a session_id that should be included in all subsequent requests.
    """
    session_manager = request.app.state.session_manager
    session_id, created_at = await session_manager.create_session()
    logger.info("New session created: %s", session_id)
    return SessionCreateResponse(session_id=session_id, created_at=created_at)


@router.get("/{session_id}", response_model=SessionInfoResponse)
async def get_session(request: Request, session_id: str) -> SessionInfoResponse:
    """
    Get metadata for an existing session.

    Args:
        session_id: UUID of the session to look up.

    Returns:
        Session info including creation time, last activity, and message count.

    Raises:
        HTTPException 404 if the session does not exist.
    """
    session_manager = request.app.state.session_manager
    info = await session_manager.get_session_info(session_id)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return info


@router.get("/{session_id}/history", response_model=list[ChatMessageRecord])
async def get_session_history(
    request: Request, session_id: str
) -> list[ChatMessageRecord]:
    """
    Retrieve the full message history for a session.

    Args:
        session_id: UUID of the session.

    Returns:
        Ordered list of chat messages.

    Raises:
        HTTPException 404 if the session does not exist.
    """
    session_manager = request.app.state.session_manager
    if not await session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return await session_manager.get_history(session_id)


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(request: Request, session_id: str) -> SessionDeleteResponse:
    """
    Delete a chat session and all its messages.

    Args:
        session_id: UUID of the session to delete.

    Returns:
        SessionDeleteResponse indicating whether deletion was successful.
    """
    session_manager = request.app.state.session_manager
    deleted = await session_manager.delete_session(session_id)
    if not deleted:
        logger.warning("Attempted to delete non-existent session: %s", session_id)
    return SessionDeleteResponse(session_id=session_id, deleted=deleted)
