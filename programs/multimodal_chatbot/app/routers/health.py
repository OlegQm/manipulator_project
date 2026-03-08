"""
Health check endpoint.

Verifies that the API is running and Redis is reachable.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> JSONResponse:
    """
    Check application health and Redis connectivity.

    Returns:
        200 with {"status": "ok", "redis": "connected"} if everything is healthy.
        503 with {"status": "degraded", "redis": "error"} if Redis is unreachable.
    """
    redis_client = request.app.state.redis
    try:
        await redis_client.ping()
        redis_status = "connected"
    except Exception:
        logger.exception("Redis health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "redis": "error"},
        )

    return JSONResponse(
        status_code=200,
        content={"status": "ok", "redis": redis_status},
    )
