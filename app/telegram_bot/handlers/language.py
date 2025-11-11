"""
Language selection callbacks.
"""
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.core.enums import Language
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import CALLBACK_LANGUAGE, CALLBACK_LANGUAGE_PREFIX
from app.telegram_bot.handlers.common import send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import language_keyboard
from app.telegram_bot.utils import get_chat_id, get_user_id


async def language_menu_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)

    await query.edit_message_text(
        get_message("language_prompt", language),
        reply_markup=language_keyboard(language),
    )


async def language_change_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    language_code = query.data.replace(CALLBACK_LANGUAGE_PREFIX, "")

    try:
        language = Language(language_code)
    except ValueError:
        language = Language.FA

    sessions.set_language(user_id, language)
    await query.edit_message_text(
        get_message("language_set", language).format(
            language_name=get_message(f"language_name_{language.value}", language)
        )
    )
    await send_main_menu(update, context)


def get_handlers():
    return [
        CallbackQueryHandler(language_menu_callback, pattern=f"^{CALLBACK_LANGUAGE}$"),
        CallbackQueryHandler(language_change_callback, pattern=f"^{CALLBACK_LANGUAGE_PREFIX}"),
    ]


__all__ = ["get_handlers", "language_menu_callback", "language_change_callback"]

