"""
Middleware for session management and timeout checking
"""
from typing import Callable, Awaitable
from telegram import Update
from telegram.ext import ContextTypes

from app.telegram_bot import sessions
from app.telegram_bot.utils import get_user_id
from app.services.telegram_session_service import get_active_session
from app.database import SessionLocal


async def session_timeout_middleware(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]],
) -> None:
    """
    Middleware to check session timeout and update activity
    
    This middleware:
    1. Checks if user has an active session
    2. Validates session hasn't expired (30 minutes inactivity)
    3. Updates last activity timestamp
    4. Clears session if expired
    """
    user_id = get_user_id(update)
    token = sessions.get_token(user_id)
    
    # If user has a token, check database session
    if token:
        db = SessionLocal()
        try:
            db_session = get_active_session(db, user_id, token)
            if not db_session:
                # Session expired or not found, clear in-memory session
                sessions.set_token(user_id, None)
                sessions.set_profile(user_id, None)
            else:
                # Update activity in database
                from app.services.telegram_session_service import update_session_activity
                update_session_activity(db, user_id, token)
        except Exception:
            # If database check fails, continue with in-memory session
            pass
        finally:
            db.close()
    
    # Continue to next handler
    await next_handler(update, context)

