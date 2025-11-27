"""
Ticket reply/comment handlers - EP2-S2: پاسخ و کامنت روی تیکت
"""
import logging
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

from app.core.enums import Language, UserRole
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import CALLBACK_TICKET_REPLY
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import ReplyState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


async def reply_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point for replying to a ticket."""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Check if ticket number is provided as command argument or callback
    ticket_id = None
    ticket_number = None
    
    # Handle callback query (from inline keyboard)
    if update.callback_query:
        await update.callback_query.answer()
        callback_data = update.callback_query.data
        if callback_data.startswith(CALLBACK_TICKET_REPLY):
            ticket_id = int(callback_data.replace(CALLBACK_TICKET_REPLY, ""))
            # Get ticket to verify access
            ticket = await api_client.get_ticket_by_id(token, ticket_id)
            if not ticket:
                await update.callback_query.edit_message_text(
                    get_message("ticket_detail_not_found", language)
                )
                return ConversationHandler.END
            ticket_number = ticket.get("ticket_number", "")
            context.user_data["reply_ticket_id"] = ticket_id
            context.user_data["reply_ticket_number"] = ticket_number
            
            # Get current user to check if can add internal comments
            current_user = await api_client.get_current_user(token)
            is_manager = False
            if current_user:
                user_role = current_user.get("role")
                role_values = [
                    UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
                    UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
                    UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
                    UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
                ]
                is_manager = user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]
            
            context.user_data["reply_is_manager"] = is_manager
            
            prompt = get_message("reply_comment_prompt", language).format(
                ticket_number=ticket_number
            )
            await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
            return ReplyState.COMMENT
    
    # Handle command with ticket number
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            ticket_number = parts[1].strip()
            # Get ticket by number
            ticket = await api_client.get_ticket_by_number(token, ticket_number)
            if ticket:
                ticket_id = ticket.get("id")
                context.user_data["reply_ticket_id"] = ticket_id
                context.user_data["reply_ticket_number"] = ticket_number
                
                # Get current user to check if can add internal comments
                current_user = await api_client.get_current_user(token)
                is_manager = False
                if current_user:
                    user_role = current_user.get("role")
                    role_values = [
                        UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
                        UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
                        UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
                        UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
                    ]
                    is_manager = user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]
                
                context.user_data["reply_is_manager"] = is_manager
                
                prompt = get_message("reply_comment_prompt", language).format(
                    ticket_number=ticket_number
                )
                await update.message.reply_text(prompt)
                return ReplyState.COMMENT
    
    # Prompt for ticket number
    prompt = get_message("reply_prompt", language)
    await update.message.reply_text(prompt)
    return ReplyState.TICKET_NUMBER


async def reply_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ticket number input for reply."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)

        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END

        ticket_number = update.message.text.strip()
        logger.debug(f"User {user_id} replying to ticket: {ticket_number}")
        
        # Get ticket by number
        ticket = await api_client.get_ticket_by_number(token, ticket_number)
        
        if not ticket:
            await update.message.reply_text(get_message("ticket_detail_not_found", language))
            return ConversationHandler.END
        
        ticket_id = ticket.get("id")
        context.user_data["reply_ticket_id"] = ticket_id
        context.user_data["reply_ticket_number"] = ticket_number
        
        # Get current user to check if can add internal comments
        current_user = await api_client.get_current_user(token)
        is_manager = False
        if current_user:
            user_role = current_user.get("role")
            role_values = [
                UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
                UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
                UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
                UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
            ]
            is_manager = user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]
        
        context.user_data["reply_is_manager"] = is_manager
        
        prompt = get_message("reply_comment_prompt", language).format(
            ticket_number=ticket_number
        )
        await update.message.reply_text(prompt)
        return ReplyState.COMMENT
        
    except Exception as e:
        logger.error(f"Error in reply_ticket_number: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(
            get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def reply_comment_text(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle comment text input."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        comment_text = update.message.text.strip()
        
        # Validate comment length
        if len(comment_text) < 3:
            await update.message.reply_text(
                get_message("comment_too_short", language).format(min_length=3)
            )
            return ReplyState.COMMENT
        
        ticket_id = context.user_data.get("reply_ticket_id")
        if not ticket_id:
            await update.message.reply_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        # Store comment text
        context.user_data["reply_comment"] = comment_text
        
        # Check if user is manager (can add internal comments)
        is_manager = context.user_data.get("reply_is_manager", False)
        
        # For managers, ask if internal comment
        if is_manager:
            from app.telegram_bot.keyboards import internal_comment_keyboard
            prompt = get_message("reply_attachment_prompt", language)
            await update.message.reply_text(
                prompt,
                reply_markup=internal_comment_keyboard(language)
            )
        else:
            # Regular user, just ask for attachment
            prompt = get_message("reply_attachment_prompt", language)
            await update.message.reply_text(prompt)
        
        return ReplyState.ATTACHMENT
        
    except Exception as e:
        logger.error(f"Error in reply_comment_text: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def reply_attachment(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file attachment for comment."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        ticket_id = context.user_data.get("reply_ticket_id")
        comment_text = context.user_data.get("reply_comment")
        
        if not ticket_id or not comment_text:
            await update.message.reply_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        attachment = update.message.document or (update.message.photo[-1] if update.message.photo else None)
        
        if attachment:
            # Get file info
            file_name = getattr(attachment, "file_name", None)
            file_size = getattr(attachment, "file_size", None)
            mime_type = getattr(attachment, "mime_type", None) or (
                "image/jpeg" if update.message.photo else "application/octet-stream"
            )
            
            # Validate file
            from app.telegram_bot.utils.file_validation import validate_telegram_file
            file_settings = await api_client.get_file_settings(token)
            ticket_attachments_count = await api_client.get_ticket_attachments_count(token, ticket_id)
            
            is_valid, error_message = validate_telegram_file(
                file_size=file_size,
                mime_type=mime_type,
                file_name=file_name,
                file_settings=file_settings,
                ticket_attachments_count=ticket_attachments_count
            )
            
            if not is_valid:
                error_msg = get_message("file_validation_error", language).format(error=error_message) if error_message else get_message("attachment_error", language)
                await update.message.reply_text(error_msg)
                return ReplyState.ATTACHMENT
            
            await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
            
            try:
                telegram_file = await attachment.get_file()
                file_bytes = await telegram_file.download_as_bytearray()
            except Exception as e:
                logger.error(f"Error downloading file: {e}", exc_info=True)
                await update.message.reply_text(get_message("attachment_error", language))
                return ReplyState.ATTACHMENT
            
            if not file_name:
                extension = ".jpg" if update.message.photo else ".bin"
                file_name = f"comment_attachment_{ticket_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{extension}"
            
            # Upload file
            uploaded = await api_client.upload_ticket_attachment(
                token=token,
                ticket_id=ticket_id,
                file_name=file_name,
                file_bytes=bytes(file_bytes),
                content_type=mime_type,
            )
            
            if not uploaded:
                await update.message.reply_text(get_message("attachment_error", language))
                return ReplyState.ATTACHMENT
            
            await update.message.reply_text(
                get_message("attachment_saved", language).format(file_name=file_name)
            )
        
        # Add comment (with or without attachment)
        is_internal = context.user_data.get("reply_is_internal", False)
        comment_result = await api_client.add_comment(
            token=token,
            ticket_id=ticket_id,
            comment=comment_text,
            is_internal=is_internal
        )
        
        if comment_result:
            ticket_number = context.user_data.get("reply_ticket_number", str(ticket_id))
            success_msg = get_message("reply_success", language)
            await update.message.reply_text(success_msg)
            logger.info(f"User {user_id} added comment to ticket {ticket_id}")
        else:
            await update.message.reply_text(get_message("reply_error", language))
        
        # Cleanup
        context.user_data.pop("reply_ticket_id", None)
        context.user_data.pop("reply_ticket_number", None)
        context.user_data.pop("reply_comment", None)
        context.user_data.pop("reply_is_manager", None)
        context.user_data.pop("reply_is_internal", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in reply_attachment: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def reply_attachment_text(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input while waiting for attachment."""
    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    text = update.message.text.strip().lower()
    
    # Check for skip/done
    if text in {"skip", "done", "finish", "تمام", "پایان", "بدون فایل"}:
        # Add comment without attachment
        return await finish_reply(update, context)
    
    # If text is provided but not skip, treat as comment and ask for attachment
    if len(text) >= 3:
        context.user_data["reply_comment"] = update.message.text.strip()
        prompt = get_message("reply_attachment_prompt", language)
        await update.message.reply_text(prompt)
        return ReplyState.ATTACHMENT
    
    await update.message.reply_text(get_message("reply_attachment_prompt", language))
    return ReplyState.ATTACHMENT


async def handle_internal_comment_callback(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback for internal/external comment selection."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        callback_data = query.data
        
        if callback_data == "comment_internal_yes":
            context.user_data["reply_is_internal"] = True
        elif callback_data == "comment_internal_no":
            context.user_data["reply_is_internal"] = False
        elif callback_data == "comment_skip_internal":
            context.user_data["reply_is_internal"] = False  # Default to external
        
        # Edit message to remove keyboard
        try:
            await query.edit_message_reply_markup(None)
        except Exception:
            pass
        
        # Continue to attachment prompt
        prompt = get_message("reply_attachment_prompt", language)
        await context.bot.send_message(chat_id=get_chat_id(update), text=prompt)
        
    except Exception as e:
        logger.error(f"Error in handle_internal_comment_callback: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))


async def finish_reply(update, context: ContextTypes.DEFAULT_TYPE):
    """Finish the reply flow by adding comment."""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        ticket_id = context.user_data.get("reply_ticket_id")
        comment_text = context.user_data.get("reply_comment")
        
        if not ticket_id or not comment_text:
            await update.message.reply_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        is_internal = context.user_data.get("reply_is_internal", False)
        
        # Add comment
        comment_result = await api_client.add_comment(
            token=token,
            ticket_id=ticket_id,
            comment=comment_text,
            is_internal=is_internal
        )
        
        if comment_result:
            success_msg = get_message("reply_success", language)
            await update.message.reply_text(success_msg)
            logger.info(f"User {user_id} added comment to ticket {ticket_id}")
        else:
            await update.message.reply_text(get_message("reply_error", language))
        
        # Cleanup
        context.user_data.pop("reply_ticket_id", None)
        context.user_data.pop("reply_ticket_number", None)
        context.user_data.pop("reply_comment", None)
        context.user_data.pop("reply_is_manager", None)
        context.user_data.pop("reply_is_internal", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in finish_reply: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(get_message("error_occurred", language))
        return ConversationHandler.END


def get_handler():
    """Return conversation handler for replying to tickets."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("reply", reply_ticket_start),
            CallbackQueryHandler(reply_ticket_start, pattern=f"^{CALLBACK_TICKET_REPLY}"),
        ],
        states={
            ReplyState.TICKET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reply_ticket_number)
            ],
            ReplyState.COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reply_comment_text)
            ],
            ReplyState.ATTACHMENT: [
                MessageHandler((filters.Document.ALL | filters.PHOTO), reply_attachment),
                MessageHandler(filters.TEXT & ~filters.COMMAND, reply_attachment_text),
                CallbackQueryHandler(handle_internal_comment_callback, pattern="^comment_internal_"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


def get_callback_handlers():
    """Return callback handlers for reply actions."""
    return [
        CallbackQueryHandler(handle_internal_comment_callback, pattern="^comment_internal_"),
    ]


__all__ = [
    "get_handler",
    "get_callback_handlers",
    "reply_ticket_start",
    "reply_ticket_number",
    "reply_comment_text",
    "reply_attachment",
    "finish_reply",
    "handle_internal_comment_callback",
]

