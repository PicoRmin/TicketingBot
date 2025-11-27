"""
Session management handlers for Telegram bot
"""
from __future__ import annotations

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from app.telegram_bot import sessions
from app.telegram_bot.handlers.common import require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.utils import get_user_id, get_chat_id
from app.database import SessionLocal
from app.services.telegram_session_service import (
    get_user_sessions,
    logout_all_sessions,
    format_session_info,
)

logger = logging.getLogger(__name__)


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle `/sessions` command - show active sessions"""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    token = await require_token(update, context)
    
    if not token:
        return
    
    try:
        # Get user profile to get backend user_id
        profile = sessions.get_profile(user_id)
        if not profile:
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=get_message("error_occurred", language),
            )
            return
        
        backend_user_id = profile.get("id")
        if not backend_user_id:
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=get_message("error_occurred", language),
            )
            return
        
        db = SessionLocal()
        try:
            user_sessions = get_user_sessions(db, backend_user_id, active_only=True)
            
            if not user_sessions:
                if language.value == "en":
                    message = "📱 No active sessions found."
                else:
                    message = "📱 هیچ session فعالی یافت نشد."
                await context.bot.send_message(
                    chat_id=get_chat_id(update),
                    text=message,
                )
                return
            
            # Format sessions list
            lang_code = language.value
            if lang_code == "en":
                header = f"📱 Active Sessions ({len(user_sessions)}):\n\n"
            else:
                header = f"📱 Sessions فعال ({len(user_sessions)}):\n\n"
            
            messages = [header]
            current_message = header
            
            for idx, session in enumerate(user_sessions, 1):
                session_info = format_session_info(session, lang_code)
                
                # Check if this is current session
                current_token = sessions.get_token(user_id)
                is_current = (session.token == current_token)
                
                if lang_code == "en":
                    session_header = f"🔹 Session {idx}"
                    if is_current:
                        session_header += " (Current)"
                else:
                    session_header = f"🔹 Session {idx}"
                    if is_current:
                        session_header += " (فعلی)"
                
                session_text = f"{session_header}\n{session_info}\n"
                
                # Telegram message limit is 4096 characters
                if len(current_message + session_text) > 4000:
                    messages.append(current_message)
                    current_message = session_text
                else:
                    current_message += session_text
            
            if current_message:
                messages.append(current_message)
            
            # Send messages
            for msg in messages:
                if msg.strip():
                    await context.bot.send_message(
                        chat_id=get_chat_id(update),
                        text=msg,
                    )
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in sessions_command: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("error_occurred", language),
        )


async def logout_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle `/logout_all` command - logout from all sessions"""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    token = await require_token(update, context)
    
    if not token:
        return
    
    try:
        # Get user profile to get backend user_id
        profile = sessions.get_profile(user_id)
        if not profile:
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=get_message("error_occurred", language),
            )
            return
        
        backend_user_id = profile.get("id")
        if not backend_user_id:
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=get_message("error_occurred", language),
            )
            return
        
        db = SessionLocal()
        try:
            count = logout_all_sessions(db, backend_user_id)
            
            # Clear in-memory session
            sessions.set_token(user_id, None)
            sessions.set_profile(user_id, None)
            
            lang_code = language.value
            if lang_code == "en":
                message = f"✅ Logged out from {count} session(s)."
            else:
                message = f"✅ از {count} session خارج شدید."
            
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=message,
            )
            await send_main_menu(update, context)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in logout_all_command: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("error_occurred", language),
        )


def get_handlers():
    """Get session management handlers"""
    return [
        CommandHandler("sessions", sessions_command),
        CommandHandler("logout_all", logout_all_command),
    ]


__all__ = ["get_handlers", "sessions_command", "logout_all_command"]

