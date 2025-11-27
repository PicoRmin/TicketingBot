"""
Common helper functions shared by Telegram bot handlers.
"""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.telegram_bot import sessions
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import main_menu_keyboard
from app.telegram_bot.utils import get_chat_id, get_user_id
from app.core.enums import Language, UserRole


async def _resolve_menu_permissions(user_id: int) -> tuple[Language, bool, bool, bool]:
    language = sessions.get_language(user_id)
    is_authenticated = sessions.is_authenticated(user_id)
    can_change_status = False
    can_manage_infrastructure = False

    if is_authenticated:
        token = sessions.get_token(user_id)
        if token:
            from app.telegram_bot.runtime import api_client

            allowed_roles = {
                UserRole.CENTRAL_ADMIN.value,
                UserRole.ADMIN.value,
                UserRole.IT_SPECIALIST.value,
            }
            try:
                user_info = await api_client.get_current_user(token)
                if user_info:
                    user_role = user_info.get("role")
                    if user_role in allowed_roles:
                        can_change_status = True
                        can_manage_infrastructure = True
            except Exception:
                pass

    return language, is_authenticated, can_change_status, can_manage_infrastructure


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the main menu to the user."""
    user_id = get_user_id(update)
    language, is_authenticated, can_change_status, can_manage_infrastructure = await _resolve_menu_permissions(
        user_id
    )
    keyboard = main_menu_keyboard(
        language, is_authenticated, can_change_status, can_manage_infrastructure
    )

    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("main_menu", language),
        reply_markup=keyboard,
    )


async def require_token(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str | None:
    """
    Ensure the user is authenticated; otherwise prompt them to log in.
    Also checks session timeout and updates activity.
    """
    user_id = get_user_id(update)
    token = sessions.get_token(user_id)
    
    if token:
        # Check and update session activity in database
        try:
            from app.services.telegram_session_service import get_active_session, update_session_activity
            from app.database import SessionLocal
            
            db = SessionLocal()
            try:
                db_session = get_active_session(db, user_id, token)
                if not db_session:
                    # Session expired or not found, clear in-memory session
                    sessions.set_token(user_id, None)
                    sessions.set_profile(user_id, None)
                    language = sessions.get_language(user_id)
                    await context.bot.send_message(
                        chat_id=get_chat_id(update),
                        text=get_message("session_expired", language),
                    )
                    return None
                else:
                    # Update activity
                    update_session_activity(db, user_id, token)
            finally:
                db.close()
        except Exception:
            # If database check fails, continue with in-memory session
            pass
        
        return token

    language = sessions.get_language(user_id)
    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("login_required", language),
    )
    return None


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generic cancellation handler for conversations."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data.clear()

    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("cancelled", language),
    )
    await send_main_menu(update, context)
    return ConversationHandler.END


__all__ = ["send_main_menu", "require_token", "cancel_command"]

