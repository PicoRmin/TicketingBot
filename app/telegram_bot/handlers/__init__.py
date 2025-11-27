"""
Telegram bot handler registration entry point.
"""
from telegram.ext import Application, CommandHandler

from app.telegram_bot.handlers import auth, language, start, ticket, track, ticket_status, session_management, ticket_detail, ticket_reply, ticket_search, ticket_priority, ticket_assign, ticket_bulk, ticket_sla, sla_alerts, sla_report
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

    # Ticket detail flow (EP2-S1)
    application.add_handler(ticket_detail.get_handler())
    for handler in ticket_detail.get_callback_handlers():
        application.add_handler(handler)

    # Ticket reply/comment flow (EP2-S2)
    application.add_handler(ticket_reply.get_handler())
    for handler in ticket_reply.get_callback_handlers():
        application.add_handler(handler)

    # Ticket search and filter flow (EP2-S3)
    application.add_handler(ticket_search.get_handler())

    # Ticket priority change flow (EP2-S4)
    application.add_handler(ticket_priority.get_handler())

    # Ticket assignment flow (EP2-S5)
    application.add_handler(ticket_assign.get_handler())

    # Ticket bulk actions flow (EP2-S6)
    application.add_handler(ticket_bulk.get_handler())

    # Ticket SLA flow (EP3-S1)
    application.add_handler(ticket_sla.get_handler())

    # SLA Alerts flow (EP3-S2)
    application.add_handler(sla_alerts.get_handler())

    # SLA Report flow (EP3-S3)
    application.add_handler(sla_report.get_handler())

    # Ticket status change flow
    for handler in ticket_status.get_handlers():
        application.add_handler(handler)

    # Language selection callbacks
    for handler in language.get_handlers():
        application.add_handler(handler)

    # Session management
    for handler in session_management.get_handlers():
        application.add_handler(handler)

    # Global cancel command
    application.add_handler(CommandHandler("cancel", cancel_command))


__all__ = ["register_handlers", "api_client"]
