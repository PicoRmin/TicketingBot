"""
Utility helpers for Telegram bot handlers.
"""
from telegram import Update


def get_user_id(update: Update) -> int:
    """Return the Telegram user ID for the current update."""
    if update.effective_user:
        return update.effective_user.id
    if update.callback_query:
        return update.callback_query.from_user.id
    raise ValueError("Unable to determine user id from update")


def get_chat_id(update: Update) -> int:
    """Return the chat ID associated with the update."""
    if update.effective_chat:
        return update.effective_chat.id
    if update.callback_query and update.callback_query.message:
        return update.callback_query.message.chat_id
    raise ValueError("Unable to determine chat id from update")


__all__ = ["get_user_id", "get_chat_id"]

