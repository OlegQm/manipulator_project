"""
Chat endpoint.

Accepts a user message (optionally with an image), runs it through the LangGraph
agent, stores the conversation in Redis, and returns the agent's response.
"""

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.chat import ChatRequest, ChatResponse, TokenLimitExceededResponse
from app.services.agent import invoke_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        404: {"description": "Session not found"},
        409: {
            "description": "Token limit exceeded",
            "model": TokenLimitExceededResponse,
        },
    },
)
async def chat(request: Request, body: ChatRequest) -> ChatResponse | JSONResponse:
    """
    Send a message to the chatbot agent within an existing session.

    Flow:
        1. Validate the session exists.
        2. Check whether the conversation is still within the token limit.
        3. Store the user message in session history.
        4. Invoke the LangGraph agent with the full conversation.
        5. Store the assistant's response in session history.
        6. Return the response along with token statistics.

    Args:
        body: ChatRequest with session_id, message, and optional image/image_url.

    Returns:
        ChatResponse on success, or HTTP 409 if the token limit is exceeded.

    Raises:
        HTTPException 404 if the session does not exist.
    """
    session_manager = request.app.state.session_manager
    settings = request.app.state.settings

    # 1. Validate session
    if not await session_manager.session_exists(body.session_id):
        raise HTTPException(
            status_code=404, detail=f"Session {body.session_id} not found"
        )

    # 2. Check token limit BEFORE adding the new message
    if not await session_manager.check_token_limit(body.session_id):
        logger.warning("Token limit exceeded for session %s", body.session_id)
        error_resp = TokenLimitExceededResponse(session_id=body.session_id)
        return JSONResponse(status_code=409, content=error_resp.model_dump())

    # 3. Store user message (and image if present)
    image_id: str | None = None
    if body.image:
        image_id = await session_manager.store_image(body.session_id, body.image)
    has_image = image_id is not None or body.image_url is not None

    await session_manager.add_message(
        session_id=body.session_id,
        role="user",
        content=body.message,
        has_image=has_image,
        image_id=image_id,
    )

    # 4. Get history and invoke agent
    history = await session_manager.get_history(body.session_id)
    # Exclude the last message (just added) — the agent function will add it
    history_for_agent = history[:-1]

    try:
        agent_response = await invoke_agent(
            settings=settings,
            history=history_for_agent,
            user_message=body.message,
            session_id=body.session_id,
            image_id=image_id,
            image_url=body.image_url,
        )
    except Exception:
        logger.exception("Agent invocation failed for session %s", body.session_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate a response. Please try again.",
        )

    # 5. Store assistant response
    await session_manager.add_message(
        session_id=body.session_id,
        role="assistant",
        content=agent_response,
    )

    # 6. Return with token stats
    tokens_used, tokens_remaining = await session_manager.get_token_stats(
        body.session_id
    )

    logger.info(
        "Chat response for session %s: %d tokens used, %d remaining",
        body.session_id,
        tokens_used,
        tokens_remaining,
    )

    return ChatResponse(
        session_id=body.session_id,
        response=agent_response,
        tokens_used=tokens_used,
        tokens_remaining=tokens_remaining,
    )
