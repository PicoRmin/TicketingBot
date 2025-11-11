"""
Ticket tracking conversation handlers.
"""
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.telegram_bot import sessions
from app.telegram_bot.callbacks import CALLBACK_TRACK_TICKET
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_category_name, get_message, get_status_name
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import TrackState
from app.telegram_bot.utils import get_chat_id, get_user_id


async def track_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    prompt = get_message("track_ticket_prompt", language)

    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
    else:
        await update.message.reply_text(prompt)

    return TrackState.NUMBER


async def track_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    token = sessions.get_token(user_id)

    if not token:
        await update.message.reply_text(get_message("login_required", language))
        return ConversationHandler.END

    ticket_number = update.message.text.strip()
    ticket = await api_client.get_ticket_by_number(token, ticket_number)

    if ticket:
        message = get_message("track_ticket_details", language).format(
            ticket_number=ticket.get("ticket_number", ""),
            title=ticket.get("title", ""),
            description=ticket.get("description", ""),
            category=get_category_name(ticket.get("category", ""), language),
            status=get_status_name(ticket.get("status", ""), language),
            created_at=ticket.get("created_at", "")[:10] if ticket.get("created_at") else "",
            updated_at=ticket.get("updated_at", "")[:10] if ticket.get("updated_at") else "",
        )
    else:
        message = get_message("track_ticket_not_found", language)

    await update.message.reply_text(message)
    await send_main_menu(update, context)
    return ConversationHandler.END


def get_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("track", track_ticket_start),
            CallbackQueryHandler(track_ticket_start, pattern=f"^{CALLBACK_TRACK_TICKET}$"),
        ],
        states={
            TrackState.NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, track_ticket_number)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
    )


__all__ = ["get_handler", "track_ticket_start", "track_ticket_number"]

