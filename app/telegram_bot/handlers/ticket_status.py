"""
Ticket status change handlers for Telegram bot.
"""
import logging
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import TicketStatus, UserRole
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_CHANGE_STATUS,
    CALLBACK_STATUS_PREFIX,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message, get_status_name
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import ChangeStatusState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


async def change_status_start(update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for changing ticket status."""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Check user role - only senior managers and IT specialists can change status
    user_info = await api_client.get_current_user(token)
    if not user_info:
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("error", language)
        )
        return ConversationHandler.END
    
    user_role = user_info.get("role")
    allowed_roles = [UserRole.CENTRAL_ADMIN.value, UserRole.ADMIN.value, UserRole.IT_SPECIALIST.value]
    
    if user_role not in allowed_roles:
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("change_status_not_allowed", language)
        )
        await send_main_menu(update, context)
        return ConversationHandler.END

    prompt = get_message("change_status_prompt", language)
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
    else:
        await update.message.reply_text(prompt)

    return ChangeStatusState.TICKET_NUMBER


async def change_status_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    """Collect ticket number and show status selection."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    token = sessions.get_token(user_id)

    if not token:
        await update.message.reply_text(get_message("login_required", language))
        return ConversationHandler.END

    ticket_number = update.message.text.strip()
    logger.debug(f"User {user_id} changing status for ticket: {ticket_number}")

    # Get ticket by number
    ticket = await api_client.get_ticket_by_number(token, ticket_number)

    if not ticket:
        await update.message.reply_text(get_message("change_status_ticket_not_found", language))
        await send_main_menu(update, context)
        return ConversationHandler.END

    # Store ticket in context
    context.user_data["change_status_ticket"] = ticket

    # Show status selection keyboard
    from app.telegram_bot.keyboards import status_keyboard
    status_prompt = get_message("change_status_select", language).format(
        ticket_number=ticket.get("ticket_number", ""),
        current_status=get_status_name(ticket.get("status", ""), language)
    )
    
    await update.message.reply_text(
        status_prompt,
        reply_markup=status_keyboard(language)
    )
    return ChangeStatusState.STATUS


async def change_status_select(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle status selection and update ticket."""
    query = update.callback_query
    await query.answer()
    
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    token = sessions.get_token(user_id)
    ticket = context.user_data.get("change_status_ticket")

    if not token or not ticket:
        await query.edit_message_text(get_message("error", language))
        await send_main_menu(update, context)
        return ConversationHandler.END

    status_value = query.data.replace(CALLBACK_STATUS_PREFIX, "")
    try:
        status = TicketStatus(status_value)
    except ValueError:
        await query.edit_message_text(get_message("invalid_input", language))
        return ConversationHandler.END

    # Update ticket status
    ticket_id = ticket.get("id")
    updated_ticket = await api_client.update_ticket_status(token, ticket_id, status.value)

    if updated_ticket:
        success_message = get_message("change_status_success", language).format(
            ticket_number=ticket.get("ticket_number", ""),
            new_status=get_status_name(status.value, language)
        )
        await query.edit_message_text(success_message)
        logger.info(f"User {user_id} changed status of ticket {ticket.get('ticket_number')} to {status.value}")
    else:
        error_message = get_message("change_status_error", language)
        await query.edit_message_text(error_message)
        logger.error(f"Failed to change status for ticket {ticket_id} by user {user_id}")

    context.user_data.pop("change_status_ticket", None)
    await send_main_menu(update, context)
    return ConversationHandler.END


def get_handlers():
    """Return handlers for ticket status change."""
    change_status_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("changestatus", change_status_start),
            CallbackQueryHandler(change_status_start, pattern=f"^{CALLBACK_CHANGE_STATUS}$"),
        ],
        states={
            ChangeStatusState.TICKET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_status_ticket_number)
            ],
            ChangeStatusState.STATUS: [
                CallbackQueryHandler(change_status_select, pattern=f"^{CALLBACK_STATUS_PREFIX}")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
        ],
        allow_reentry=True,
        per_message=False,
    )

    return [change_status_conversation]


__all__ = ["get_handlers", "change_status_start", "change_status_ticket_number", "change_status_select"]

