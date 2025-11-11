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


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the main menu to the user."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    keyboard = main_menu_keyboard(language, sessions.is_authenticated(user_id))

    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("main_menu", language),
        reply_markup=keyboard,
    )


async def require_token(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str | None:
    """Ensure the user is authenticated; otherwise prompt them to log in."""
    user_id = get_user_id(update)
    token = sessions.get_token(user_id)
    if token:
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

