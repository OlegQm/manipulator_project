"""
Tests for session management endpoints and the SessionManager service.
"""

from datetime import datetime, timezone

import pytest


# ── SessionManager unit tests ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_session(session_manager):
    """Creating a session returns a UUID and a datetime."""
    session_id, created_at = await session_manager.create_session()
    assert isinstance(session_id, str)
    assert len(session_id) == 36  # UUID4 format
    assert isinstance(created_at, datetime)


@pytest.mark.asyncio
async def test_session_exists(session_manager):
    """session_exists returns True for created sessions, False otherwise."""
    session_id, _ = await session_manager.create_session()
    assert await session_manager.session_exists(session_id) is True
    assert await session_manager.session_exists("nonexistent-id") is False


@pytest.mark.asyncio
async def test_get_session_info(session_manager):
    """get_session_info returns correct metadata."""
    session_id, _ = await session_manager.create_session()
    info = await session_manager.get_session_info(session_id)
    assert info is not None
    assert info.session_id == session_id
    assert info.message_count == 0


@pytest.mark.asyncio
async def test_get_session_info_nonexistent(session_manager):
    """get_session_info returns None for nonexistent sessions."""
    info = await session_manager.get_session_info("nonexistent-id")
    assert info is None


@pytest.mark.asyncio
async def test_delete_session(session_manager):
    """Deleting a session removes it from Redis."""
    session_id, _ = await session_manager.create_session()
    assert await session_manager.delete_session(session_id) is True
    assert await session_manager.session_exists(session_id) is False


@pytest.mark.asyncio
async def test_delete_nonexistent_session(session_manager):
    """Deleting a nonexistent session returns False."""
    assert await session_manager.delete_session("nonexistent-id") is False


@pytest.mark.asyncio
async def test_add_and_get_messages(session_manager):
    """Messages added to a session can be retrieved in order."""
    session_id, _ = await session_manager.create_session()
    await session_manager.add_message(session_id, "user", "Hello")
    await session_manager.add_message(session_id, "assistant", "Hi there!")

    history = await session_manager.get_history(session_id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi there!"


@pytest.mark.asyncio
async def test_message_count_updates(session_manager):
    """Message count in session info reflects added messages."""
    session_id, _ = await session_manager.create_session()
    await session_manager.add_message(session_id, "user", "Test")
    info = await session_manager.get_session_info(session_id)
    assert info.message_count == 1


@pytest.mark.asyncio
async def test_token_counting(session_manager):
    """count_tokens returns a positive number for non-empty sessions."""
    session_id, _ = await session_manager.create_session()
    await session_manager.add_message(session_id, "user", "Hello, how are you?")
    tokens = await session_manager.count_tokens(session_id)
    assert tokens > 0


@pytest.mark.asyncio
async def test_token_limit_within(session_manager):
    """check_token_limit returns True when within limits."""
    session_id, _ = await session_manager.create_session()
    await session_manager.add_message(session_id, "user", "Short message")
    assert await session_manager.check_token_limit(session_id) is True


@pytest.mark.asyncio
async def test_token_limit_exceeded(session_manager):
    """check_token_limit returns False when tokens exceed MAX_CONTEXT_TOKENS."""
    session_id, _ = await session_manager.create_session()
    # MAX_CONTEXT_TOKENS is set to 1000 in test_settings
    # Generate a lot of text to exceed the limit
    long_text = "word " * 500  # ~500 tokens
    await session_manager.add_message(session_id, "user", long_text)
    await session_manager.add_message(session_id, "assistant", long_text)
    assert await session_manager.check_token_limit(session_id) is False


@pytest.mark.asyncio
async def test_get_all_session_ids(session_manager):
    """get_all_session_ids returns all created session IDs."""
    id1, _ = await session_manager.create_session()
    id2, _ = await session_manager.create_session()
    all_ids = await session_manager.get_all_session_ids()
    assert id1 in all_ids
    assert id2 in all_ids


@pytest.mark.asyncio
async def test_last_activity_updates(session_manager):
    """last_activity is updated when a message is added."""
    session_id, _ = await session_manager.create_session()
    initial = await session_manager.get_last_activity(session_id)
    await session_manager.add_message(session_id, "user", "Test")
    updated = await session_manager.get_last_activity(session_id)
    assert updated >= initial


# ── Cleanup unit tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cleanup_expired_sessions(session_manager, fake_redis):
    """Cleanup deletes sessions that exceed the TTL."""
    from app.services.cleanup import cleanup_expired_sessions

    session_id, _ = await session_manager.create_session()

    # Manually set last_activity to 2 hours ago to simulate expiry
    two_hours_ago = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat()
    await fake_redis.hset(f"session:{session_id}:meta", "last_activity", two_hours_ago)

    deleted = await cleanup_expired_sessions(session_manager, ttl_seconds=3600)
    assert deleted >= 1
    assert await session_manager.session_exists(session_id) is False


@pytest.mark.asyncio
async def test_cleanup_preserves_active_sessions(session_manager):
    """Cleanup does not delete sessions that are still active."""
    from app.services.cleanup import cleanup_expired_sessions

    session_id, _ = await session_manager.create_session()
    await session_manager.add_message(session_id, "user", "Active")

    deleted = await cleanup_expired_sessions(session_manager, ttl_seconds=3600)
    assert deleted == 0
    assert await session_manager.session_exists(session_id) is True


# ── API endpoint tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_api_create_session(test_client):
    """POST /api/v1/sessions creates a session and returns 201."""
    response = await test_client.post("/api/v1/sessions")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_api_get_session(test_client):
    """GET /api/v1/sessions/{id} returns session info."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    response = await test_client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["message_count"] == 0


@pytest.mark.asyncio
async def test_api_get_session_not_found(test_client):
    """GET /api/v1/sessions/{id} returns 404 for nonexistent sessions."""
    response = await test_client.get("/api/v1/sessions/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_delete_session(test_client):
    """DELETE /api/v1/sessions/{id} deletes the session."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    response = await test_client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Verify it's gone
    response = await test_client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_get_history(test_client):
    """GET /api/v1/sessions/{id}/history returns message history."""
    create_resp = await test_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    response = await test_client.get(f"/api/v1/sessions/{session_id}/history")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_get_history_not_found(test_client):
    """GET /api/v1/sessions/{id}/history returns 404 for nonexistent sessions."""
    response = await test_client.get("/api/v1/sessions/nonexistent-id/history")
    assert response.status_code == 404
