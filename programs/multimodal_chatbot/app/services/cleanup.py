"""
Background cleanup task that periodically removes expired sessions.

Uses APScheduler's AsyncIOScheduler to run a job at a configurable interval.
A session is considered expired when its last_activity is older than SESSION_TTL_SECONDS.
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.session_manager import SessionManager

logger = logging.getLogger(__name__)

# Module-level scheduler instance (started/stopped from FastAPI lifespan)
scheduler = AsyncIOScheduler()


async def cleanup_expired_sessions(session_manager: SessionManager, ttl_seconds: int) -> int:
    """
    Find and delete all sessions whose last activity exceeds the TTL.

    Args:
        session_manager: SessionManager instance for Redis operations.
        ttl_seconds: Maximum seconds of inactivity before a session expires.

    Returns:
        Number of sessions that were deleted.
    """
    now = datetime.now(timezone.utc)
    session_ids = await session_manager.get_all_session_ids()
    deleted_count = 0

    for sid in session_ids:
        last_activity = await session_manager.get_last_activity(sid)
        if last_activity is None:
            # Orphaned key — clean it up
            await session_manager.delete_session(sid)
            deleted_count += 1
            continue

        elapsed = (now - last_activity).total_seconds()
        if elapsed > ttl_seconds:
            await session_manager.delete_session(sid)
            deleted_count += 1
            logger.info(
                "Cleaned up session %s (inactive for %.0f seconds)",
                sid,
                elapsed,
            )

    if deleted_count > 0:
        logger.info("Cleanup complete: deleted %d expired session(s)", deleted_count)
    else:
        logger.debug("Cleanup complete: no expired sessions found")

    return deleted_count


def start_cleanup_scheduler(
    session_manager: SessionManager,
    interval_seconds: int,
    ttl_seconds: int,
) -> None:
    """
    Register the cleanup job and start the APScheduler.

    Args:
        session_manager: SessionManager for Redis operations.
        interval_seconds: How often (in seconds) to run the cleanup job.
        ttl_seconds: Session inactivity TTL in seconds.
    """
    scheduler.add_job(
        cleanup_expired_sessions,
        trigger="interval",
        seconds=interval_seconds,
        args=[session_manager, ttl_seconds],
        id="session_cleanup",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Cleanup scheduler started (interval=%ds, ttl=%ds)",
        interval_seconds,
        ttl_seconds,
    )


def stop_cleanup_scheduler() -> None:
    """Gracefully shut down the APScheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Cleanup scheduler stopped")
