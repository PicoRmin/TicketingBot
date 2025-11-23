"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.i18n import I18nMiddleware
from app.config import settings
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="سیستم تیکتینگ ایرانمهر / Iranmehr Ticketing System",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.telegram_bot_started = False

# Configure CORS
cors_origins = settings.cors_origins_list
logger.info(f"CORS allowed origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# i18n middleware - makes request.state.lang available
app.add_middleware(I18nMiddleware)


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Start automation scheduler
    try:
        from app.tasks.automation_tasks import start_automation_scheduler
        start_automation_scheduler()
        logger.info("Automation scheduler started")
    except Exception as e:
        logger.warning(f"Failed to start automation scheduler: {e}")
    
    # Start SLA monitoring scheduler
    try:
        from app.tasks.sla_tasks import start_sla_scheduler
        start_sla_scheduler()
        logger.info("SLA monitoring scheduler started")
    except Exception as e:
        logger.warning(f"Failed to start SLA scheduler: {e}")
    
    # Start Telegram Bot if token is provided
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            from app.telegram_bot.bot import start_bot
            await start_bot()
            app.state.telegram_bot_started = True
            logger.info("Telegram Bot started successfully")
        except Exception as e:
            app.state.telegram_bot_started = False
            logger.error(f"Failed to start Telegram Bot: {e}")
    else:
        app.state.telegram_bot_started = False
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram Bot startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    logger.info("Shutting down application")
    
    # Stop Telegram Bot if it was started
    if settings.TELEGRAM_BOT_TOKEN and getattr(app.state, "telegram_bot_started", False):
        try:
            from app.telegram_bot.bot import stop_bot
            await stop_bot()
            logger.info("Telegram Bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram Bot: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Iranmehr Ticketing System",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# Import and include routers
from app.api import auth, tickets, files
from app.api import branches, comments
from app.api import reports
from app.api import users
from app.api import settings as settings_api
from app.api import branch_infrastructure
from app.api import departments
from app.api import priorities
from app.api import sla
from app.api import automation
from app.api import time_tracker

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(branches.router, prefix="/api/branches", tags=["Branches"])
app.include_router(comments.router, prefix="/api/comments", tags=["Comments"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(branch_infrastructure.router, prefix="/api/branch-infrastructure", tags=["Branch Infrastructure"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(priorities.router, prefix="/api/priorities", tags=["Priorities"])
app.include_router(sla.router, prefix="/api/sla", tags=["SLA"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])
app.include_router(time_tracker.router, prefix="/api/time-tracker", tags=["Time Tracker"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

