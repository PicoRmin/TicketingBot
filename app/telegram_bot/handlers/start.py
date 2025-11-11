"""
/start and /help command handlers.
"""
from telegram.ext import CommandHandler, ContextTypes

from app.telegram_bot import sessions
from app.telegram_bot.handlers.common import send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import main_menu_keyboard
from app.telegram_bot.utils import get_user_id


async def start_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle `/start` command."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    keyboard = main_menu_keyboard(language, sessions.is_authenticated(user_id))
    await update.message.reply_text(get_message("welcome", language), reply_markup=keyboard)


async def help_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle `/help` command."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    await update.message.reply_text(get_message("help", language))
    await send_main_menu(update, context)


def get_handlers():
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
    ]


__all__ = ["get_handlers", "start_command", "help_command"]

