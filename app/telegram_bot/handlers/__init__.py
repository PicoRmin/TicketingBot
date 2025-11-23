"""
Telegram bot handler registration entry point.
"""
from telegram.ext import Application, CommandHandler

from app.telegram_bot.handlers import auth, language, start, ticket, track, ticket_status
from app.telegram_bot.handlers.common import cancel_command
from app.telegram_bot.runtime import api_client


def register_handlers(application: Application) -> None:
    """Register all Telegram bot handlers with the provided application."""
    # Basic commands
    for handler in start.get_handlers():
        application.add_handler(handler)

    # Authentication
    application.add_handler(auth.get_conversation_handler())
    for handler in auth.get_logout_handlers():
        application.add_handler(handler)

    # Ticket flows
    for handler in ticket.get_handlers():
        application.add_handler(handler)

    # Track ticket flow
    application.add_handler(track.get_handler())

    # Ticket status change flow
    for handler in ticket_status.get_handlers():
        application.add_handler(handler)

    # Language selection callbacks
    for handler in language.get_handlers():
        application.add_handler(handler)

    # Global cancel command
    application.add_handler(CommandHandler("cancel", cancel_command))


__all__ = ["register_handlers", "api_client"]
