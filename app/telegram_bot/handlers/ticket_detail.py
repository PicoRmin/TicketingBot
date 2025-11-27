"""
Ticket detail handlers - EP2-S1: مشاهده جزئیات کامل تیکت
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language, UserRole
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_TICKET_DETAIL,
    CALLBACK_TICKET_REPLY,
    CALLBACK_TICKET_COMMENTS,
    CALLBACK_TICKET_HISTORY,
    CALLBACK_TICKET_ATTACHMENTS,
    CALLBACK_TICKET_PRIORITY,
    CALLBACK_TICKET_ASSIGN,
)
from app.telegram_bot.handlers.ticket_priority import priority_ticket_start
from app.telegram_bot.handlers.ticket_assign import assign_ticket_start
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_category_name, get_message, get_status_name
from app.telegram_bot.keyboards import ticket_detail_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import TrackState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_datetime(dt_str: str, language: Language) -> str:
    """Format datetime string for display."""
    try:
        if not dt_str:
            return ""
        # Parse ISO format datetime
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        if language == Language.FA:
            return dt.strftime("%Y/%m/%d %H:%M")
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_str[:16] if dt_str else ""


async def ticket_detail_start(update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for viewing ticket details."""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Check if ticket number is provided as command argument
    ticket_number = None
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            ticket_number = parts[1].strip()
    
    if ticket_number:
        # Direct ticket number provided, show details immediately
        return await show_ticket_details(update, context, ticket_number)
    
    # Prompt for ticket number
    prompt = get_message("ticket_detail_prompt", language)
    
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
    else:
        await update.message.reply_text(prompt)
    
    return TrackState.NUMBER


async def ticket_detail_number(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ticket number input and show details."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)

        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END

        ticket_number = update.message.text.strip()
        logger.debug(f"User {user_id} viewing ticket details: {ticket_number}")
        
        return await show_ticket_details(update, context, ticket_number)
    except Exception as e:
        logger.error(f"Error in ticket_detail_number: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(
            get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def show_ticket_details(update, context: ContextTypes.DEFAULT_TYPE, ticket_number: str):
    """Show complete ticket details with inline keyboard."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)

        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END

        # Get ticket by number
        ticket = await api_client.get_ticket_by_number(token, ticket_number)
        
        if not ticket:
            message = get_message("ticket_detail_not_found", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                await context.bot.send_message(chat_id=get_chat_id(update), text=message)
            await send_main_menu(update, context)
            return ConversationHandler.END

        ticket_id = ticket.get("id")
        
        # Get current user info to check permissions
        current_user = await api_client.get_current_user(token)
        is_manager = False
        if current_user:
            user_role = current_user.get("role")
            # Handle both string and enum values
            role_values = [
                UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
                UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
                UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
                UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
            ]
            is_manager = user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]

        # Build priority line
        priority = ticket.get("priority", "medium")
        priority_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "🟡")
        priority_line = f"{priority_emoji} اولویت: {get_message(f'priority_{priority}', language, default=priority)}\n"
        
        # Build assigned line
        assigned_to = ticket.get("assigned_to")
        assigned_line = ""
        if assigned_to:
            assigned_name = assigned_to.get("full_name") or assigned_to.get("username", "")
            assigned_line = f"👤 کارشناس مسئول: {assigned_name}\n"
        
        # Format dates
        created_at = format_datetime(ticket.get("created_at", ""), language)
        updated_at = format_datetime(ticket.get("updated_at", ""), language)
        
        # Build message
        message = get_message("ticket_detail_header", language).format(
            ticket_number=ticket.get("ticket_number", ""),
            title=ticket.get("title", ""),
            description=ticket.get("description", ""),
            category=get_category_name(ticket.get("category", ""), language),
            status=get_status_name(ticket.get("status", ""), language),
            priority_line=priority_line,
            assigned_line=assigned_line,
            created_at=created_at,
            updated_at=updated_at,
        )
        
        # Create inline keyboard
        keyboard = ticket_detail_keyboard(ticket_id, language, is_manager=is_manager)
        
        # Send message
        if update.message:
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=get_chat_id(update), text=message, reply_markup=keyboard)
        
        logger.info(f"User {user_id} viewed ticket details: {ticket_number}")
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in show_ticket_details: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            await context.bot.send_message(chat_id=get_chat_id(update), text=error_msg)
        return ConversationHandler.END


async def show_ticket_comments(update, context: ContextTypes.DEFAULT_TYPE):
    """Show ticket comments."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return
        
        # Extract ticket ID from callback data
        ticket_id = int(query.data.replace(CALLBACK_TICKET_COMMENTS, ""))
        
        # Get comments
        comments = await api_client.get_ticket_comments(token, ticket_id)
        
        # Get ticket number for header
        ticket = await api_client.get_ticket_by_id(token, ticket_id)
        ticket_number = ticket.get("ticket_number", "") if ticket else str(ticket_id)
        
        if not comments or len(comments) == 0:
            message = get_message("comments_empty", language)
            await query.edit_message_text(message)
            return
        
        # Build comments message
        header = get_message("comments_header", language).format(ticket_number=ticket_number)
        message_parts = [header]
        
        for comment in comments[:10]:  # Limit to 10 comments to avoid message length issues
            author = "سیستم"  # Default
            if comment.get("user"):
                author = comment["user"].get("full_name") or comment["user"].get("username", "کاربر")
            
            created_at = format_datetime(comment.get("created_at", ""), language)
            comment_text = comment.get("comment", "")
            is_internal = comment.get("is_internal", False)
            internal_tag = get_message("comment_internal", language) if is_internal else ""
            
            comment_item = get_message("comment_item", language).format(
                author=author,
                created_at=created_at,
                comment=comment_text,
                internal_tag=internal_tag,
            )
            message_parts.append(comment_item)
        
        if len(comments) > 10:
            message_parts.append(f"\n... و {len(comments) - 10} کامنت دیگر")
        
        message = "\n".join(message_parts)
        
        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n... (متن کامل در پنل وب قابل مشاهده است)"
        
        await query.edit_message_text(message)
        
    except Exception as e:
        logger.error(f"Error in show_ticket_comments: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))


async def show_ticket_history(update, context: ContextTypes.DEFAULT_TYPE):
    """Show ticket history."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return
        
        # Extract ticket ID from callback data
        ticket_id = int(query.data.replace(CALLBACK_TICKET_HISTORY, ""))
        
        # Get history
        history = await api_client.get_ticket_history(token, ticket_id)
        
        # Get ticket number for header
        ticket = await api_client.get_ticket_by_id(token, ticket_id)
        ticket_number = ticket.get("ticket_number", "") if ticket else str(ticket_id)
        
        if not history or len(history) == 0:
            message = get_message("history_empty", language)
            await query.edit_message_text(message)
            return
        
        # Build history message
        header = get_message("history_header", language).format(ticket_number=ticket_number)
        message_parts = [header]
        
        for entry in history[:15]:  # Limit to 15 entries
            changed_by = "سیستم"  # Default
            if entry.get("changed_by"):
                changed_by = entry["changed_by"].get("full_name") or entry["changed_by"].get("username", "کاربر")
            
            created_at = format_datetime(entry.get("created_at", ""), language)
            status = get_status_name(entry.get("status", ""), language)
            comment = entry.get("comment", "") or "-"
            
            history_item = get_message("history_item", language).format(
                created_at=created_at,
                changed_by=changed_by,
                status=status,
                comment=comment,
            )
            message_parts.append(history_item)
        
        if len(history) > 15:
            message_parts.append(f"\n... و {len(history) - 15} رویداد دیگر")
        
        message = "\n".join(message_parts)
        
        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n... (متن کامل در پنل وب قابل مشاهده است)"
        
        await query.edit_message_text(message)
        
    except Exception as e:
        logger.error(f"Error in show_ticket_history: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))


async def show_ticket_attachments(update, context: ContextTypes.DEFAULT_TYPE):
    """Show ticket attachments."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return
        
        # Extract ticket ID from callback data
        ticket_id = int(query.data.replace(CALLBACK_TICKET_ATTACHMENTS, ""))
        
        # Get attachments
        attachments = await api_client.get_ticket_attachments(token, ticket_id)
        
        # Get ticket number for header
        ticket = await api_client.get_ticket_by_id(token, ticket_id)
        ticket_number = ticket.get("ticket_number", "") if ticket else str(ticket_id)
        
        if not attachments or len(attachments) == 0:
            message = get_message("attachments_empty", language)
            await query.edit_message_text(message)
            return
        
        # Build attachments message
        header = get_message("attachments_header", language).format(ticket_number=ticket_number)
        message_parts = [header]
        
        for attachment in attachments:
            file_name = attachment.get("file_name", "Unknown")
            file_size = attachment.get("file_size", 0)
            created_at = format_datetime(attachment.get("created_at", ""), language)
            
            attachment_item = get_message("attachment_item", language).format(
                file_name=file_name,
                file_size=format_file_size(file_size),
                created_at=created_at,
            )
            message_parts.append(attachment_item)
        
        message = "\n".join(message_parts)
        
        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n... (فایل‌های بیشتر در پنل وب قابل مشاهده است)"
        
        await query.edit_message_text(message)
        
    except Exception as e:
        logger.error(f"Error in show_ticket_attachments: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))


def get_handler():
    """Return conversation handler for ticket details."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("ticket", ticket_detail_start),
        ],
        states={
            TrackState.NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_detail_number)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


def get_callback_handlers():
    """Return callback handlers for ticket detail actions."""
    return [
        CallbackQueryHandler(show_ticket_comments, pattern=f"^{CALLBACK_TICKET_COMMENTS}"),
        CallbackQueryHandler(show_ticket_history, pattern=f"^{CALLBACK_TICKET_HISTORY}"),
        CallbackQueryHandler(show_ticket_attachments, pattern=f"^{CALLBACK_TICKET_ATTACHMENTS}"),
        CallbackQueryHandler(priority_ticket_start, pattern=f"^{CALLBACK_TICKET_PRIORITY}"),
        CallbackQueryHandler(assign_ticket_start, pattern=f"^{CALLBACK_TICKET_ASSIGN}"),
    ]


__all__ = [
    "get_handler",
    "get_callback_handlers",
    "ticket_detail_start",
    "ticket_detail_number",
    "show_ticket_details",
    "show_ticket_comments",
    "show_ticket_history",
    "show_ticket_attachments",
]

