"""
Ticket-related commands and conversations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from telegram.constants import ChatAction
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language, TicketCategory
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_BRANCH_PREFIX,
    CALLBACK_CATEGORY_PREFIX,
    CALLBACK_MY_TICKETS,
    CALLBACK_NEW_TICKET,
    CALLBACK_SKIP_ATTACHMENTS,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_category_name, get_message, get_status_name
from app.telegram_bot.keyboards import branch_keyboard, category_keyboard, skip_attachments_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import TicketState
from app.telegram_bot.utils import get_chat_id, get_user_id


async def my_tickets(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current user's tickets."""
    token = await require_token(update, context)
    if not token:
        return

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.edit_message_reply_markup(None)
        except Exception:
            pass

    tickets_data = await api_client.get_user_tickets(token, page=1, page_size=10)
    if not tickets_data or tickets_data.get("total", 0) == 0:
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("my_tickets_empty", language),
        )
        return

    header = get_message("my_tickets_list", language)
    await context.bot.send_message(chat_id=get_chat_id(update), text=header)

    for ticket in tickets_data.get("items", []):
        message = get_message("ticket_item", language).format(
            ticket_number=ticket.get("ticket_number", ""),
            title=ticket.get("title", ""),
            status=get_status_name(ticket.get("status", ""), language),
            category=get_category_name(ticket.get("category", ""), language),
            created_at=ticket.get("created_at", "")[:10] if ticket.get("created_at") else "",
        )
        await context.bot.send_message(chat_id=get_chat_id(update), text=message)


async def start_new_ticket(update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for creating a new ticket."""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data["ticket_flow"] = {}

    prompt = get_message("new_ticket_start", language)
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
    else:
        await update.message.reply_text(prompt)

    return TicketState.TITLE


async def ticket_title(update, context: ContextTypes.DEFAULT_TYPE):
    """Collect ticket title."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data.setdefault("ticket_flow", {})["title"] = update.message.text.strip()

    await update.message.reply_text(
        get_message("new_ticket_title", language).format(title=update.message.text.strip())
    )
    return TicketState.DESCRIPTION


async def ticket_description(update, context: ContextTypes.DEFAULT_TYPE):
    """Collect ticket description and prompt for branch selection."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    data = context.user_data.setdefault("ticket_flow", {})
    data["description"] = update.message.text.strip()
    token = sessions.get_token(user_id)

    if not token:
        await update.message.reply_text(get_message("login_required", language))
        return ConversationHandler.END

    # Fetch branches
    branches = await api_client.get_branches(token)
    if not branches:
        # If no branches, skip to category
        await update.message.reply_text(
            get_message("new_ticket_description", language),
            reply_markup=category_keyboard(language),
        )
        return TicketState.CATEGORY

    # Store branches for later use
    data["branches"] = branches

    await update.message.reply_text(
        get_message("new_ticket_description", language),
        reply_markup=branch_keyboard(branches, language),
    )
    return TicketState.BRANCH


async def ticket_branch(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle branch selection and prompt for category."""
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    data: Dict[str, Any] = context.user_data.setdefault("ticket_flow", {})

    branch_value = query.data.replace(CALLBACK_BRANCH_PREFIX, "")
    
    if branch_value == "skip":
        data["branch_id"] = None
        branch_name = get_message("branch_skip", language)
    else:
        try:
            branch_id = int(branch_value)
            data["branch_id"] = branch_id
            # Get branch name from stored branches list
            branches = data.get("branches", [])
            branch = next((b for b in branches if b.get("id") == branch_id), None)
            branch_name = branch.get("name", f"Branch {branch_id}") if branch else f"Branch {branch_id}"
        except ValueError:
            await query.edit_message_text(get_message("invalid_input", language))
            return ConversationHandler.END

    await query.edit_message_text(
        get_message("new_ticket_branch", language).format(branch_name=branch_name)
    )
    
    # Get proper message for category prompt
    category_prompt = "لطفاً دسته‌بندی تیکت را انتخاب کنید:" if language == Language.FA else "Please select the ticket category:"
    
    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=category_prompt,
        reply_markup=category_keyboard(language),
    )
    return TicketState.CATEGORY


async def ticket_category(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection and create the ticket via API."""
    query = update.callback_query
    await query.answer()
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    data: Dict[str, Any] = context.user_data.setdefault("ticket_flow", {})
    token = sessions.get_token(user_id)

    if not token:
        await query.edit_message_text(get_message("login_required", language))
        return ConversationHandler.END

    category_value = query.data.replace(CALLBACK_CATEGORY_PREFIX, "")
    try:
        category = TicketCategory(category_value)
    except ValueError:
        await query.edit_message_text(get_message("invalid_input", language))
        return ConversationHandler.END

    data["category"] = category
    await query.edit_message_text(
        get_message("new_ticket_category", language).format(
            category=get_category_name(category_value, language)
        )
    )

    ticket = await api_client.create_ticket(
        token=token,
        title=data.get("title", ""),
        description=data.get("description", ""),
        category=category,
        branch_id=data.get("branch_id"),
    )

    if not ticket:
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("ticket_created_error", language),
        )
        context.user_data.pop("ticket_flow", None)
        await send_main_menu(update, context)
        return ConversationHandler.END

    data["ticket"] = ticket
    created_message = get_message("ticket_created", language).format(
        ticket_number=ticket.get("ticket_number", ""),
        title=ticket.get("title", ""),
        category=get_category_name(ticket.get("category", ""), language),
        status=get_status_name(ticket.get("status", ""), language),
    )

    await context.bot.send_message(chat_id=get_chat_id(update), text=created_message)
    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("attachments_prompt", language),
        reply_markup=skip_attachments_keyboard(language),
    )
    return TicketState.ATTACHMENTS


async def ticket_attachment(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document/photo uploads for attachments."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    data = context.user_data.get("ticket_flow")
    token = sessions.get_token(user_id)

    if not token or not data or "ticket" not in data:
        await update.message.reply_text(get_message("error", language))
        return ConversationHandler.END

    attachment = update.message.document or (update.message.photo[-1] if update.message.photo else None)
    if not attachment:
        await update.message.reply_text(get_message("attachments_text_hint", language))
        return TicketState.ATTACHMENTS

    ticket = data["ticket"]
    ticket_id = ticket.get("id")
    if not ticket_id:
        await update.message.reply_text(get_message("error", language))
        return ConversationHandler.END

    await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    telegram_file = await attachment.get_file()
    file_bytes = await telegram_file.download_as_bytearray()

    file_name = getattr(attachment, "file_name", None)
    if not file_name:
        file_name = f"attachment_{ticket_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
    mime_type = getattr(attachment, "mime_type", None) or (
        "image/jpeg" if update.message.photo else "application/octet-stream"
    )

    uploaded = await api_client.upload_ticket_attachment(
        token=token,
        ticket_id=ticket_id,
        file_name=file_name,
        file_bytes=bytes(file_bytes),
        content_type=mime_type,
    )

    if not uploaded:
        await update.message.reply_text(get_message("attachment_error", language))
        return TicketState.ATTACHMENTS

    await update.message.reply_text(
        get_message("attachment_saved", language).format(file_name=file_name)
    )
    return TicketState.ATTACHMENTS


async def ticket_attachment_text(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle textual input while waiting for attachments."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    text = update.message.text.strip().lower()
    if text in {"skip", "done", "finish", "تمام", "پایان"}:
        return await finish_ticket_creation(update, context)

    await update.message.reply_text(get_message("attachments_text_hint", language))
    return TicketState.ATTACHMENTS


async def skip_attachments_command(update, context: ContextTypes.DEFAULT_TYPE):
    return await finish_ticket_creation(update, context)


async def skip_attachments_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(None)
    except Exception:
        pass
    return await finish_ticket_creation(update, context)


async def finish_ticket_creation(update, context: ContextTypes.DEFAULT_TYPE):
    """Finish the ticket creation flow."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    context.user_data.pop("ticket_flow", None)

    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("attachments_done", language),
    )
    await send_main_menu(update, context)
    return ConversationHandler.END


def get_handlers():
    """Return handlers related to tickets."""
    new_ticket_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("newticket", start_new_ticket),
            CallbackQueryHandler(start_new_ticket, pattern=f"^{CALLBACK_NEW_TICKET}$"),
        ],
        states={
            TicketState.TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_title)
            ],
            TicketState.DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_description)
            ],
            TicketState.BRANCH: [
                CallbackQueryHandler(ticket_branch, pattern=f"^{CALLBACK_BRANCH_PREFIX}")
            ],
            TicketState.CATEGORY: [
                CallbackQueryHandler(ticket_category, pattern=f"^{CALLBACK_CATEGORY_PREFIX}")
            ],
            TicketState.ATTACHMENTS: [
                MessageHandler((filters.Document.ALL | filters.PHOTO), ticket_attachment),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_attachment_text),
                CommandHandler("skip", skip_attachments_command),
                CallbackQueryHandler(skip_attachments_callback, pattern=f"^{CALLBACK_SKIP_ATTACHMENTS}$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("skip", skip_attachments_command),
        ],
        allow_reentry=True,
        per_message=False,  # Set to False when using MessageHandler in states
    )

    my_tickets_handlers = [
        CommandHandler("mytickets", my_tickets),
        CallbackQueryHandler(my_tickets, pattern=f"^{CALLBACK_MY_TICKETS}$"),
    ]

    return [new_ticket_conversation, *my_tickets_handlers]


__all__ = [
    "get_handlers",
    "my_tickets",
    "start_new_ticket",
    "ticket_title",
    "ticket_description",
    "ticket_category",
    "ticket_attachment",
    "ticket_attachment_text",
    "skip_attachments_command",
    "skip_attachments_callback",
    "finish_ticket_creation",
]

