"""
Main FastAPI application
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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

# OpenAPI metadata for Swagger UI
tags_metadata = [
    {
        "name": "Authentication",
        "description": "ورود/خروج، مدیریت توکن و بازیابی هویت کاربران (admin و user)."
    },
    {
        "name": "Users",
        "description": "CRUD کاربران، تخصیص نقش، مدیریت دسترسی و پروفایل."
    },
    {
        "name": "Tickets",
        "description": "ایجاد، به‌روزرسانی، فیلتر، تاریخچه و تخصیص تیکت‌ها."
    },
    {
        "name": "Comments",
        "description": "یادداشت‌های داخلی/خارجی تیکت و ضمیمه‌های مرتبط."
    },
    {
        "name": "Files",
        "description": "آپلود/دانلود پیوست‌ها با اعتبارسنجی اندازه و فرمت."
    },
    {
        "name": "Branches",
        "description": "مدیریت شعب، کدها و اطلاعات زیرساخت."
    },
    {
        "name": "Departments",
        "description": "تعریف دپارتمان‌ها، اولویت‌ها و نگاشت به شعب."
    },
    {
        "name": "Custom Fields",
        "description": "تعریف فیلدهای پویا و دریافت مقادیر متناسب با دسته‌بندی تیکت."
    },
    {
        "name": "SLA",
        "description": "قوانین SLA، پایش و لاگ‌ها، نرخ رعایت و Escalation."
    },
    {
        "name": "Automation",
        "description": "قوانین خودکارسازی (تخصیص، اعلان، بستن خودکار)."
    },
    {
        "name": "Reports",
        "description": "گزارش‌های آماری، خروجی CSV/PDF و KPIهای اصلی."
    },
    {
        "name": "Time Tracker",
        "description": "ثبت تایم‌لاگ کارشناسان و گزارش‌گیری مرتبط."
    },
    {
        "name": "Settings",
        "description": "پیکربندی سیستم، SMTP، Telegram Bot و گزینه‌های امنیتی."
    },
    {
        "name": "Branch Infrastructure",
        "description": "ثبت تجهیزات شبکه/زیرساخت هر شعبه برای پیگیری فنی."
    },
    {
        "name": "Priorities",
        "description": "تعریف اولویت‌ها و برچسب‌های مرتبط برای SLA."
    },
    {
        "name": "Notifications",
        "description": "فید اعلان درون‌برنامه‌ای برای موبایل و وب، خواندن/علامت‌گذاری."
    },
    {
        "name": "Profile",
        "description": "مدیریت اطلاعات تکمیلی و مرحله onboarding کاربران."
    },
    {
        "name": "Knowledge Base",
        "description": "مقالات آموزشی و پیشنهادات هوشمند برای کاربران و کارشناسان."
    },
]

# Create FastAPI app with richer Swagger metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "سیستم تیکتینگ ایرانمهر (Iranmehr Ticketing) شامل APIهای اصلی مدیریت تیکت، "
        "SLA، خودکارسازی و پورتال کاربر است. از بخش Tags می‌توانید مسیرهای مرتبط هر حوزه را ببینید."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Iranmehr IT",
        "url": "https://iranmehr.com",
        "email": "it@iranmehr.com",
    },
    license_info={
        "name": "Internal Use Only",
        "url": "https://iranmehr.com/licenses/internal",
    },
)

app.state.telegram_bot_started = False

# Serve static files (e.g., favicon)
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure CORS
cors_origins = settings.cors_origins_list
logger.info(f"CORS allowed origins: {cors_origins}")
logger.info(f"CORS_ORIGINS raw value: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# i18n middleware - makes request.state.lang available
app.add_middleware(I18nMiddleware)


# Exception handlers to ensure CORS headers are included in error responses
def get_cors_headers(request: Request) -> dict:
    """Get CORS headers based on request origin"""
    origin = request.headers.get("origin")
    if origin and origin in cors_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers=headers
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with CORS headers"""
    logger.exception(f"Unhandled exception: {exc}")
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
        headers=headers
    )


# Validate production settings on startup
if settings.is_production:
    try:
        settings.validate_production_settings()
        logger.info("Production settings validated successfully")
    except ValueError as e:
        logger.critical(f"Production settings validation failed: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    # Production settings already validated before startup
    
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

    # Start Telegram daily report scheduler
    try:
        from app.tasks.telegram_report_tasks import start_daily_report_scheduler

        start_daily_report_scheduler()
        logger.info("Telegram daily report scheduler initialization attempted")
    except Exception as e:
        logger.warning(f"Failed to initialize Telegram daily report scheduler: {e}")
    
    # Start Telegram Bot if token is provided
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            from app.telegram_bot.bot import start_bot
            await start_bot()
            app.state.telegram_bot_started = True
            logger.info("Telegram Bot started successfully")
        except Exception as e:
            app.state.telegram_bot_started = False
            logger.error(f"Failed to start Telegram Bot: {e}", exc_info=True)
            logger.warning("Telegram Bot will not be available. The application will continue without it.")
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
    """Health check endpoint for monitoring"""
    from app.database import SessionLocal
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }
    
    # Check database connection
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        finally:
            db.close()
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return health_status, 503
    
    return health_status


@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS is working correctly",
        "cors_origins": settings.cors_origins_list,
        "timestamp": "test"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon for browsers"""
    favicon_path = static_dir / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"detail": "favicon not found"}

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
from app.api import custom_fields
from app.api import notifications
from app.api import profile
from app.api import knowledge_base

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
app.include_router(custom_fields.router, prefix="/api/custom-fields", tags=["Custom Fields"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["Knowledge Base"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

