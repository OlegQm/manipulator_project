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
    """Chat with an image stores it in Redis and passes image_id to the agent."""
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
    assert len(data["response"]) > 0

    # Verify the agent was called with session_id and image_id (not raw base64)
    call_kwargs = mock_agent.call_args.kwargs
    assert call_kwargs["session_id"] == session_id
    assert call_kwargs["image_id"] is not None
    assert len(call_kwargs["image_id"]) == 36  # UUID4 format
    assert "image_b64" not in call_kwargs  # raw base64 should NOT be passed

    # Verify the image_id is persisted in the message history
    history_resp = await test_client.get(f"/api/v1/sessions/{session_id}/history")
    history = history_resp.json()
    assert history[0]["image_id"] == call_kwargs["image_id"]


@pytest.mark.asyncio
async def test_chat_followup_reuses_previous_image_from_same_session(test_client):
    """Follow-up text-only message reuses the latest image from the same session."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    fake_image_b64 = "iVBORw0KGgoAAAANSUhEUg=="

    # First message: send image
    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = "I see a test image."
        await test_client.post(
            "/api/v1/chat",
            json={
                "session_id": session_id,
                "message": "Describe this",
                "image": fake_image_b64,
            },
        )
    first_image_id = mock_agent.call_args.kwargs["image_id"]

    # Second message: text-only follow-up about the same image
    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent2:
        mock_agent2.return_value = "The image shows..."
        await test_client.post(
            "/api/v1/chat",
            json={"session_id": session_id, "message": "What color is it?"},
        )

    call_kwargs2 = mock_agent2.call_args.kwargs
    assert call_kwargs2["image_id"] == first_image_id


@pytest.mark.asyncio
async def test_chat_followup_does_not_reuse_image_from_another_session(test_client):
    """Image carry-over must stay scoped to the current session only."""
    session_a = (await test_client.post("/api/v1/sessions")).json()["session_id"]
    session_b = (await test_client.post("/api/v1/sessions")).json()["session_id"]

    fake_image_b64 = "iVBORw0KGgoAAAANSUhEUg=="

    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent_a:
        mock_agent_a.return_value = "Session A image stored."
        await test_client.post(
            "/api/v1/chat",
            json={
                "session_id": session_a,
                "message": "Remember this image",
                "image": fake_image_b64,
            },
        )

    with patch("app.routers.chat.invoke_agent", new_callable=AsyncMock) as mock_agent_b:
        mock_agent_b.return_value = "Session B has no image."
        await test_client.post(
            "/api/v1/chat",
            json={"session_id": session_b, "message": "Do I have an image?"},
        )

    assert mock_agent_b.call_args.kwargs["image_id"] is None


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
