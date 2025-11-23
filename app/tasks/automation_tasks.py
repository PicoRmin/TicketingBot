"""
Background tasks for automation rules
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal

logger = logging.getLogger(__name__)


async def run_automation_tasks():
    """
    Run automation tasks periodically
    This should be called by a background scheduler
    """
    db: Session = SessionLocal()
    try:
        from app.services.automation_service import process_automation_rules
        
        logger.info("Starting automation tasks...")
        stats = process_automation_rules(db)
        logger.info(f"Automation tasks completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error running automation tasks: {e}", exc_info=True)
        return None
    finally:
        db.close()


def start_automation_scheduler():
    """
    Start background scheduler for automation tasks
    This runs every 30 minutes
    """
    async def scheduler_loop():
        while True:
            try:
                await run_automation_tasks()
                # Wait 30 minutes before next run
                await asyncio.sleep(30 * 60)
            except Exception as e:
                logger.error(f"Error in automation scheduler: {e}", exc_info=True)
                # Wait 5 minutes before retry on error
                await asyncio.sleep(5 * 60)
    
    # Start scheduler in background
    asyncio.create_task(scheduler_loop())
    logger.info("Automation scheduler started")

