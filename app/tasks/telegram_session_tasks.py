"""
Background tasks for Telegram session management
"""
import asyncio
import logging
from app.database import SessionLocal
from app.services.telegram_session_service import cleanup_expired_telegram_sessions
from app.config import settings

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_MINUTES = settings.TELEGRAM_SESSION_CLEANUP_INTERVAL_MINUTES


async def run_session_cleanup():
    """
    Run Telegram session cleanup periodically
    """
    db = SessionLocal()
    try:
        logger.info("Starting Telegram session cleanup...")
        count = cleanup_expired_telegram_sessions(db)
        if count > 0:
            logger.info(f"Cleaned up {count} expired Telegram sessions.")
        else:
            logger.debug("No expired Telegram sessions to clean up.")
    except Exception as e:
        # Log error but don't crash the scheduler
        error_msg = str(e).lower()
        if "no such table" in error_msg or "does not exist" in error_msg:
            logger.warning(
                "telegram_sessions table does not exist. "
                "Run migration: python scripts/migrate_v21_create_telegram_sessions.py"
            )
        else:
            logger.error(f"Error running Telegram session cleanup: {e}", exc_info=True)
    finally:
        db.close()


async def _scheduler_loop():
    """
    Scheduler loop for Telegram session cleanup
    """
    while True:
        try:
            await run_session_cleanup()
            await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)
        except asyncio.CancelledError:
            logger.info("Telegram session cleanup scheduler was cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in Telegram session cleanup scheduler: {e}", exc_info=True)
            await asyncio.sleep(60)  # Wait a minute before retrying on error


def start_telegram_session_cleanup_scheduler():
    """
    Start background scheduler for Telegram session cleanup
    """
    try:
        asyncio.create_task(_scheduler_loop())
        logger.info(f"Telegram session cleanup scheduler started (runs every {CLEANUP_INTERVAL_MINUTES} minutes)")
    except Exception as exc:
        logger.error("Failed to start Telegram session cleanup scheduler: %s", exc, exc_info=True)

