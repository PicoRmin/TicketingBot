"""
Authentication (login/logout) handlers and conversation.
"""
from __future__ import annotations

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import CALLBACK_LOGIN, CALLBACK_LOGOUT
from app.telegram_bot.handlers.common import cancel_command, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import LoginState
from app.telegram_bot.utils import get_chat_id, get_user_id


async def login_start(update, context: ContextTypes.DEFAULT_TYPE) -> LoginState:
    """Prompt the user for their username."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data.pop("login", None)

    text = get_message("login_prompt_username", language)
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=get_chat_id(update), text=text)
    else:
        await update.message.reply_text(text)
    return LoginState.USERNAME


async def login_username(update, context: ContextTypes.DEFAULT_TYPE) -> LoginState:
    """Collect username and ask for password."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data["login"] = {"username": update.message.text.strip()}
    await update.message.reply_text(get_message("login_prompt_password", language))
    return LoginState.PASSWORD


async def login_password(update, context: ContextTypes.DEFAULT_TYPE):
    """Validate credentials and finish login conversation."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    credentials = context.user_data.get("login", {})
    username = credentials.get("username")
    password = update.message.text.strip()

    if not username:
        await update.message.reply_text(get_message("login_prompt_username", language))
        return LoginState.USERNAME

    token = await api_client.login(username=username, password=password)
    if not token:
        await update.message.reply_text(get_message("login_failed", language))
        return LoginState.USERNAME

    sessions.set_token(user_id, token)

    profile = await api_client.get_current_user(token)
    if profile and profile.get("language"):
        try:
            sessions.set_language(user_id, Language(profile["language"]))
            language = sessions.get_language(user_id)
        except ValueError:
            pass
    sessions.set_profile(user_id, profile)

    await update.message.reply_text(get_message("login_success", language))
    await send_main_menu(update, context)
    context.user_data.pop("login", None)
    return ConversationHandler.END


async def logout_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle `/logout` command."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    sessions.set_token(user_id, None)
    sessions.set_profile(user_id, None)
    await update.message.reply_text(get_message("logout_success", language))
    await send_main_menu(update, context)


async def logout_callback(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle logout triggered via inline menu."""
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    sessions.set_token(user_id, None)
    sessions.set_profile(user_id, None)
    await query.edit_message_text(get_message("logout_success", language))
    await send_main_menu(update, context)


def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("login", login_start),
            CallbackQueryHandler(login_start, pattern=f"^{CALLBACK_LOGIN}$"),
        ],
        states={
            LoginState.USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)
            ],
            LoginState.PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,  # Must be False when using MessageHandler
    )


def get_logout_handlers():
    return [
        CommandHandler("logout", logout_command),
        CallbackQueryHandler(logout_callback, pattern=f"^{CALLBACK_LOGOUT}$"),
    ]


__all__ = [
    "get_conversation_handler",
    "get_logout_handlers",
    "login_start",
    "login_username",
    "login_password",
    "logout_command",
    "logout_callback",
]

