"""
Ticket-related commands and conversations.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from telegram.constants import ChatAction

logger = logging.getLogger(__name__)
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
    try:
        token = await require_token(update, context)
        if not token:
            return

        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        logger.debug(f"User {user_id} requested their tickets")

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
            logger.debug(f"User {user_id} has no tickets")
            return

        header = get_message("my_tickets_list", language)
        await context.bot.send_message(chat_id=get_chat_id(update), text=header)

        ticket_count = 0
        for ticket in tickets_data.get("items", []):
            # Build message with priority and assigned_to
            priority = ticket.get("priority", "medium")
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(priority, "🟡")
            
            assigned_to = ticket.get("assigned_to")
            assigned_text = ""
            if assigned_to:
                assigned_name = assigned_to.get("full_name") or assigned_to.get("username", "")
                assigned_text = f"\n👤 کارشناس: {assigned_name}"
            
            message = get_message("ticket_item", language).format(
                ticket_number=ticket.get("ticket_number", ""),
                title=ticket.get("title", ""),
                status=get_status_name(ticket.get("status", ""), language),
                category=get_category_name(ticket.get("category", ""), language),
                created_at=ticket.get("created_at", "")[:10] if ticket.get("created_at") else "",
            )
            # Add priority and assigned_to to message
            message += f"\n{priority_emoji} اولویت: {get_message(f'priority_{priority}', language, default=priority)}"
            message += assigned_text
            
            await context.bot.send_message(chat_id=get_chat_id(update), text=message)
            ticket_count += 1
        
        logger.info(f"User {user_id} viewed {ticket_count} tickets")
    except Exception as e:
        logger.error(f"Error in my_tickets handler: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )


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
    description = update.message.text.strip()
    
    # Validate description length (minimum 10 characters)
    if len(description) < 10:
        await update.message.reply_text(
            get_message("description_too_short", language).format(min_length=10)
        )
        return TicketState.DESCRIPTION
    
    data["description"] = description
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
        # Try to get more specific error message
        error_msg = get_message("ticket_created_error", language)
        
        # Check if description is too short
        description = data.get("description", "")
        if len(description) < 10:
            error_msg = get_message("description_too_short", language).format(min_length=10)
        
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=error_msg,
        )
        context.user_data.pop("ticket_flow", None)
        await send_main_menu(update, context)
        return ConversationHandler.END

    data["ticket"] = ticket
    # Build message with priority and assigned_to
    priority = ticket.get("priority", "medium")
    priority_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }.get(priority, "🟡")
    
    assigned_to = ticket.get("assigned_to")
    assigned_text = ""
    if assigned_to:
        assigned_name = assigned_to.get("full_name") or assigned_to.get("username", "")
        assigned_text = f"\n👤 کارشناس مسئول: {assigned_name}"
    
    created_message = get_message("ticket_created", language).format(
        ticket_number=ticket.get("ticket_number", ""),
        title=ticket.get("title", ""),
        category=get_category_name(ticket.get("category", ""), language),
        status=get_status_name(ticket.get("status", ""), language),
    )
    # Add priority and assigned_to
    created_message += f"\n{priority_emoji} اولویت: {get_message(f'priority_{priority}', language, default=priority)}"
    created_message += assigned_text

    await context.bot.send_message(chat_id=get_chat_id(update), text=created_message)
    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text=get_message("attachments_prompt", language),
        reply_markup=skip_attachments_keyboard(language),
    )
    return TicketState.ATTACHMENTS


async def ticket_attachment(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document/photo uploads for attachments."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        data = context.user_data.get("ticket_flow")
        token = sessions.get_token(user_id)

        if not token or not data or "ticket" not in data:
            logger.warning(f"Invalid ticket flow state for user {user_id}")
            await update.message.reply_text(get_message("error", language))
            return ConversationHandler.END

        attachment = update.message.document or (update.message.photo[-1] if update.message.photo else None)
        if not attachment:
            await update.message.reply_text(get_message("attachments_text_hint", language))
            return TicketState.ATTACHMENTS

        ticket = data["ticket"]
        ticket_id = ticket.get("id")
        if not ticket_id:
            logger.error(f"Ticket ID missing in ticket flow for user {user_id}")
            await update.message.reply_text(get_message("error", language))
            return ConversationHandler.END

        # Get file info before downloading
        file_name = getattr(attachment, "file_name", None)
        file_size = getattr(attachment, "file_size", None)
        mime_type = getattr(attachment, "mime_type", None) or (
            "image/jpeg" if update.message.photo else "application/octet-stream"
        )
        
        logger.debug(f"User {user_id} uploading file: name={file_name}, size={file_size}, type={mime_type}, ticket_id={ticket_id}")
        
        # Get file settings from API (to use database settings instead of config)
        file_settings = await api_client.get_file_settings(token)
        if not file_settings:
            logger.warning(f"Failed to get file settings for user {user_id}, using defaults")
            file_settings = None  # Will use defaults in validation
        
        # Get current attachment counts for this ticket
        ticket_attachments_count = await api_client.get_ticket_attachments_count(token, ticket_id)
        if not ticket_attachments_count:
            logger.warning(f"Failed to get attachment counts for ticket {ticket_id}, using defaults")
            ticket_attachments_count = None  # Will skip count validation
        
        # Validate file before downloading (with settings from database)
        from app.telegram_bot.utils.file_validation import validate_telegram_file
        is_valid, error_message = validate_telegram_file(
            file_size=file_size,
            mime_type=mime_type,
            file_name=file_name,
            file_settings=file_settings,
            ticket_attachments_count=ticket_attachments_count
        )
        
        if not is_valid:
            error_msg = get_message("file_validation_error", language).format(error=error_message) if error_message else get_message("attachment_error", language)
            logger.warning(f"File validation failed for user {user_id}: {error_message}")
            await update.message.reply_text(error_msg)
            return TicketState.ATTACHMENTS

        await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
        
        try:
            telegram_file = await attachment.get_file()
            file_bytes = await telegram_file.download_as_bytearray()
            logger.debug(f"Downloaded file from Telegram: {len(file_bytes)} bytes")
        except Exception as e:
            logger.error(f"Error downloading file from Telegram for user {user_id}: {e}", exc_info=True)
            await update.message.reply_text(get_message("attachment_error", language))
            return TicketState.ATTACHMENTS

        # Generate filename if not provided
        if not file_name:
            extension = ".jpg" if update.message.photo else ".bin"
            file_name = f"attachment_{ticket_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{extension}"

        # Upload to API
        logger.info(f"Uploading file to API: ticket_id={ticket_id}, file_name={file_name}, size={len(file_bytes)}")
        try:
            uploaded = await api_client.upload_ticket_attachment(
                token=token,
                ticket_id=ticket_id,
                file_name=file_name,
                file_bytes=bytes(file_bytes),
                content_type=mime_type,
            )

            if not uploaded:
                logger.error(f"File upload failed for user {user_id}, ticket_id={ticket_id}, file_name={file_name}")
                error_msg = get_message("attachment_error", language)
                await update.message.reply_text(error_msg)
                return TicketState.ATTACHMENTS

            logger.info(f"File uploaded successfully: user_id={user_id}, ticket_id={ticket_id}, file_name={file_name}")
            await update.message.reply_text(
                get_message("attachment_saved", language).format(file_name=file_name)
            )
            return TicketState.ATTACHMENTS
        except Exception as upload_error:
            logger.error(f"Exception during file upload API call: {upload_error}", exc_info=True)
            error_msg = get_message("attachment_error", language)
            await update.message.reply_text(error_msg)
            return TicketState.ATTACHMENTS
    except Exception as e:
        logger.error(f"Error in ticket_attachment handler: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        try:
            await update.message.reply_text(get_message("attachment_error", language))
        except Exception as reply_error:
            logger.error(f"Failed to send error message: {reply_error}", exc_info=True)
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

