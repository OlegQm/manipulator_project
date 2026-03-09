"""
FastAPI application entry point.

Sets up the application lifespan (Redis connection, cleanup scheduler),
mounts all routers, and configures middleware.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, health, session, warehouse
from app.services.cleanup import start_cleanup_scheduler, stop_cleanup_scheduler
from app.services.session_manager import SessionManager, set_session_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan: runs on startup and shutdown.

    Startup:
        - Connect to Redis
        - Initialize SessionManager
        - Start the cleanup scheduler

    Shutdown:
        - Stop the cleanup scheduler
        - Close the Redis connection
    """
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Connect to Redis (decode_responses=True so we get str, not bytes)
    redis_client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    # Verify Redis connectivity
    try:
        await redis_client.ping()
        logger.info("Connected to Redis at %s", settings.redis_url)
    except Exception:
        logger.exception("Failed to connect to Redis at %s", settings.redis_url)
        raise

    # Initialize services
    session_manager = SessionManager(redis_client, settings)
    set_session_manager(session_manager)

    # Store on app.state for access in request handlers
    app.state.redis = redis_client
    app.state.session_manager = session_manager
    app.state.settings = settings

    # Start background cleanup
    start_cleanup_scheduler(
        session_manager=session_manager,
        interval_seconds=settings.cleanup_interval_seconds,
        ttl_seconds=settings.session_ttl_seconds,
    )

    logger.info("Multimodal chatbot started (model=%s)", settings.openai_model)
    yield

    # Shutdown
    stop_cleanup_scheduler()
    await redis_client.aclose()
    logger.info("Multimodal chatbot shut down")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance with all routers and middleware.
    """
    app = FastAPI(
        title="Multimodal Chatbot API",
        description="A multimodal chatbot that accepts images and text to answer questions.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS — allow mobile app connections from any origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    app.include_router(health.router)
    app.include_router(session.router)
    app.include_router(chat.router)
    app.include_router(warehouse.router)  # TO DELETE: remove this line and app/routers/warehouse.py

    return app


# Application instance used by uvicorn
app = create_app()
