"""
Background tasks for SLA monitoring and alerts
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sla_alert_service import check_sla_warnings_and_breaches

logger = logging.getLogger(__name__)


async def run_sla_checks():
    """
    اجرای بررسی‌های SLA به صورت دوره‌ای
    این تابع باید توسط یک background scheduler فراخوانی شود
    """
    db: Session = SessionLocal()
    try:
        logger.info("Starting SLA checks...")
        stats = await check_sla_warnings_and_breaches(db)
        logger.info(f"SLA checks completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error running SLA checks: {e}", exc_info=True)
        return None
    finally:
        db.close()


def start_sla_scheduler():
    """
    شروع background scheduler برای بررسی‌های SLA
    این scheduler هر 15 دقیقه یکبار اجرا می‌شود
    """
    async def scheduler_loop():
        while True:
            try:
                await run_sla_checks()
                # Wait 15 minutes before next run
                await asyncio.sleep(15 * 60)
            except Exception as e:
                logger.error(f"Error in SLA scheduler: {e}", exc_info=True)
                # Wait 5 minutes before retry on error
                await asyncio.sleep(5 * 60)
    
    # Start scheduler in background
    try:
        # Create task in the current event loop (should be running in FastAPI startup)
        asyncio.create_task(scheduler_loop())
        logger.info("SLA scheduler started (runs every 15 minutes)")
    except Exception as e:
        logger.error(f"Failed to start SLA scheduler: {e}", exc_info=True)

