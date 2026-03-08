"""
Tests for the POST /api/v1/chat endpoint.

Uses mocked agent to avoid real OpenAI API calls during testing.
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_chat_text_only(test_client):
    """Chat with a text-only message returns a valid response."""
    # Create session first
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = "This is a test response from the agent."

        response = await test_client.post(
            "/api/v1/chat",
            json={"session_id": session_id, "message": "Hello, what can you do?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["response"] == "This is a test response from the agent."
    assert "tokens_used" in data
    assert "tokens_remaining" in data


@pytest.mark.asyncio
async def test_chat_with_image(test_client):
    """Chat with an image + text message returns a valid response."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    # Fake small base64 image
    fake_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = "I see a small 1x1 pixel image."

        response = await test_client.post(
            "/api/v1/chat",
            json={
                "session_id": session_id,
                "message": "What is in this image?",
                "image": fake_image_b64,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "image" in data["response"].lower() or len(data["response"]) > 0


@pytest.mark.asyncio
async def test_chat_session_not_found(test_client):
    """Chat with a nonexistent session returns 404."""
    response = await test_client.post(
        "/api/v1/chat",
        json={"session_id": "nonexistent-id", "message": "Hello"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_token_limit_exceeded(test_client):
    """Chat returns 409 when the session exceeds the token limit."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    # Fill up the session with a lot of messages to exceed MAX_CONTEXT_TOKENS (1000 in test)
    sm = test_client._transport.app.state.session_manager
    long_text = "word " * 500  # ~500 tokens per message
    await sm.add_message(session_id, "user", long_text)
    await sm.add_message(session_id, "assistant", long_text)

    # Now try to chat — should be over the limit
    response = await test_client.post(
        "/api/v1/chat",
        json={"session_id": session_id, "message": "One more message"},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["action"] == "recreate_session"
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_chat_stores_messages_in_history(test_client):
    """After chatting, messages appear in the session history."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = "Agent response."

        await test_client.post(
            "/api/v1/chat",
            json={"session_id": session_id, "message": "User says hello"},
        )

    history_resp = await test_client.get(f"/api/v1/sessions/{session_id}/history")
    history = history_resp.json()
    assert len(history) == 2  # user message + assistant response
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "User says hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Agent response."
