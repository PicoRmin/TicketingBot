"""
Ticket priority management handlers - EP2-S4: مدیریت اولویت تیکت
"""
import logging
from typing import Any, Dict

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
    CALLBACK_TICKET_PRIORITY,
    CALLBACK_PRIORITY_PREFIX,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import priority_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import PriorityState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


def check_manager_permission(user_role: str) -> bool:
    """بررسی دسترسی مدیر برای تغییر اولویت"""
    role_values = [
        UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
        UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
        UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
        UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
    ]
    return user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]


async def priority_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای تغییر اولویت تیکت"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # بررسی دسترسی مدیر
    current_user = await api_client.get_current_user(token)
    if not current_user:
        await update.message.reply_text(get_message("login_required", language))
        return ConversationHandler.END
    
    user_role = current_user.get("role")
    if not check_manager_permission(user_role):
        message = get_message("priority_not_allowed", language)
        if update.message:
            await update.message.reply_text(message)
        else:
            await context.bot.send_message(chat_id=get_chat_id(update), text=message)
        await send_main_menu(update, context)
        return ConversationHandler.END
    
    # بررسی اگر ticket number به عنوان آرگومان داده شده
    ticket_id = None
    ticket_number = None
    
    # Handle callback query (from inline keyboard)
    if update.callback_query:
        await update.callback_query.answer()
        callback_data = update.callback_query.data
        if callback_data.startswith(CALLBACK_TICKET_PRIORITY):
            ticket_id = int(callback_data.replace(CALLBACK_TICKET_PRIORITY, ""))
            # Get ticket to verify access
            ticket = await api_client.get_ticket_by_id(token, ticket_id)
            if not ticket:
                await update.callback_query.edit_message_text(
                    get_message("ticket_detail_not_found", language)
                )
                return ConversationHandler.END
            ticket_number = ticket.get("ticket_number", "")
            context.user_data["priority_ticket_id"] = ticket_id
            context.user_data["priority_ticket_number"] = ticket_number
            context.user_data["priority_current_priority"] = ticket.get("priority", "medium")
            
            # Show priority selection
            return await show_priority_selection(update, context, ticket_number, ticket.get("priority", "medium"))
    
    # Handle command with ticket number
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            ticket_number = parts[1].strip()
            # Get ticket by number
            ticket = await api_client.get_ticket_by_number(token, ticket_number)
            if ticket:
                ticket_id = ticket.get("id")
                context.user_data["priority_ticket_id"] = ticket_id
                context.user_data["priority_ticket_number"] = ticket_number
                context.user_data["priority_current_priority"] = ticket.get("priority", "medium")
                
                return await show_priority_selection(update, context, ticket_number, ticket.get("priority", "medium"))
    
    # Prompt for ticket number
    prompt = get_message("priority_prompt", language)
    await update.message.reply_text(prompt)
    return PriorityState.TICKET_NUMBER


async def priority_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت شماره تیکت برای تغییر اولویت"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)

        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END

        # بررسی دسترسی مدیر
        current_user = await api_client.get_current_user(token)
        if not current_user:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        user_role = current_user.get("role")
        if not check_manager_permission(user_role):
            await update.message.reply_text(get_message("priority_not_allowed", language))
            await send_main_menu(update, context)
            return ConversationHandler.END

        ticket_number = update.message.text.strip()
        logger.debug(f"User {user_id} changing priority for ticket: {ticket_number}")
        
        # Get ticket by number
        ticket = await api_client.get_ticket_by_number(token, ticket_number)
        
        if not ticket:
            await update.message.reply_text(get_message("ticket_detail_not_found", language))
            return ConversationHandler.END
        
        ticket_id = ticket.get("id")
        context.user_data["priority_ticket_id"] = ticket_id
        context.user_data["priority_ticket_number"] = ticket_number
        context.user_data["priority_current_priority"] = ticket.get("priority", "medium")
        
        return await show_priority_selection(update, context, ticket_number, ticket.get("priority", "medium"))
        
    except Exception as e:
        logger.error(f"Error in priority_ticket_number: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(
            get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def show_priority_selection(update, context: ContextTypes.DEFAULT_TYPE, ticket_number: str, current_priority: str):
    """نمایش انتخاب اولویت"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        current_priority_text = get_message(f"priority_{current_priority}", language, default=current_priority)
        
        message = get_message("priority_select", language).format(
            ticket_number=ticket_number,
            current_priority=current_priority_text
        )
        
        keyboard = priority_keyboard(language)
        
        if update.message:
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            query = update.callback_query
            await query.edit_message_text(message, reply_markup=keyboard)
        
        return PriorityState.PRIORITY
        
    except Exception as e:
        logger.error(f"Error in show_priority_selection: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            query = update.callback_query
            await query.edit_message_text(error_msg)
        return ConversationHandler.END


async def priority_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب اولویت"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # بررسی دسترسی مدیر
        current_user = await api_client.get_current_user(token)
        if not current_user:
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        user_role = current_user.get("role")
        if not check_manager_permission(user_role):
            await query.edit_message_text(get_message("priority_not_allowed", language))
            return ConversationHandler.END
        
        # Extract priority from callback data
        callback_data = query.data
        if not callback_data.startswith(CALLBACK_PRIORITY_PREFIX):
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        new_priority = callback_data.replace(CALLBACK_PRIORITY_PREFIX, "")
        
        # Get ticket info from context
        ticket_id = context.user_data.get("priority_ticket_id")
        ticket_number = context.user_data.get("priority_ticket_number", "")
        current_priority = context.user_data.get("priority_current_priority", "medium")
        
        if not ticket_id:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        # Check if priority changed
        if new_priority == current_priority:
            await query.edit_message_text(
                get_message("priority_no_change", language).format(
                    ticket_number=ticket_number,
                    priority=get_message(f"priority_{new_priority}", language, default=new_priority)
                )
            )
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Update priority
        updated_ticket = await api_client.update_ticket_priority(
            token=token,
            ticket_id=ticket_id,
            priority=new_priority
        )
        
        if not updated_ticket:
            await query.edit_message_text(get_message("priority_error", language))
            return ConversationHandler.END
        
        # Success message
        new_priority_text = get_message(f"priority_{new_priority}", language, default=new_priority)
        success_message = get_message("priority_success", language).format(
            ticket_number=ticket_number,
            new_priority=new_priority_text
        )
        
        await query.edit_message_text(success_message)
        logger.info(f"User {user_id} changed priority for ticket {ticket_id} from {current_priority} to {new_priority}")
        
        # Cleanup
        context.user_data.pop("priority_ticket_id", None)
        context.user_data.pop("priority_ticket_number", None)
        context.user_data.pop("priority_current_priority", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in priority_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای تغییر اولویت تیکت"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("priority", priority_ticket_start),
            CallbackQueryHandler(priority_ticket_start, pattern=f"^{CALLBACK_TICKET_PRIORITY}"),
        ],
        states={
            PriorityState.TICKET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, priority_ticket_number)
            ],
            PriorityState.PRIORITY: [
                CallbackQueryHandler(priority_selected, pattern=f"^{CALLBACK_PRIORITY_PREFIX}"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "priority_ticket_start",
    "priority_ticket_number",
    "priority_selected",
    "show_priority_selection",
]

