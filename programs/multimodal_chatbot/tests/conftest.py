"""
Shared test fixtures for the multimodal chatbot test suite.

Provides:
    - Fake Redis client (fakeredis) instead of a real server
    - Test Settings with overridden config values
    - Async HTTPX test client wired to the FastAPI app
    - SessionManager fixture with fake Redis
"""

import asyncio
from typing import AsyncGenerator

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.services.session_manager import SessionManager, set_session_manager


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Return Settings with test-appropriate values."""
    return Settings(
        openai_api_key="test-key-not-real",
        openai_model="gpt-4o-mini",
        redis_url="redis://localhost:6379/0",
        session_ttl_seconds=3600,
        cleanup_interval_seconds=600,
        max_context_tokens=1000,  # low limit for testing token overflow
        basic_auth_user="testuser",
        basic_auth_password="testpass",
        log_level="DEBUG",
    )


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator:
    """Provide a fakeredis async client that behaves like a real Redis."""
    server = fakeredis.aioredis.FakeServer()
    client = fakeredis.aioredis.FakeRedis(server=server, decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def session_manager(
    fake_redis, test_settings
) -> AsyncGenerator[SessionManager, None]:
    """Provide a SessionManager backed by fake Redis."""
    manager = SessionManager(redis_client=fake_redis, settings=test_settings)
    yield manager


@pytest_asyncio.fixture
async def test_client(fake_redis, test_settings) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTPX client connected to the FastAPI app.

    Overrides the app's Redis and settings with test fixtures so no real
    Redis or OpenAI connections are needed.
    """
    from app.main import create_app

    app = create_app()

    # Override lifespan-created state with test fixtures
    app.state.redis = fake_redis
    sm = SessionManager(fake_redis, test_settings)
    app.state.session_manager = sm
    app.state.settings = test_settings
    set_session_manager(sm)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
