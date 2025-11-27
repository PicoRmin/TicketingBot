"""
Ticket bulk actions handlers - EP2-S6: Bulk Actions برای تیکت‌ها
"""
import logging
from typing import Any, Dict, List, Optional, Set

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
    CALLBACK_BULK_ACTION,
    CALLBACK_BULK_SELECT,
    CALLBACK_BULK_CONFIRM,
    CALLBACK_BULK_CANCEL,
    CALLBACK_STATUS_PREFIX,
    CALLBACK_USER_PREFIX,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import (
    bulk_action_keyboard,
    status_keyboard,
    user_selection_keyboard,
)
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import BulkActionState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


def check_manager_permission(user_role: str) -> bool:
    """بررسی دسترسی مدیر برای bulk actions"""
    role_values = [
        UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
        UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
        UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
    ]
    return user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]


async def bulk_action_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای bulk actions"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # بررسی دسترسی مدیر
    current_user = await api_client.get_current_user(token)
    if not current_user:
        if update.message:
            await update.message.reply_text(get_message("login_required", language))
        else:
            await context.bot.send_message(
                chat_id=get_chat_id(update),
                text=get_message("login_required", language)
            )
        return ConversationHandler.END
    
    user_role = current_user.get("role")
    if not check_manager_permission(user_role):
        message = get_message("bulk_not_allowed", language)
        if update.message:
            await update.message.reply_text(message)
        else:
            await context.bot.send_message(chat_id=get_chat_id(update), text=message)
        await send_main_menu(update, context)
        return ConversationHandler.END
    
    # Initialize context
    context.user_data["bulk_selected_tickets"] = set()
    context.user_data["bulk_action"] = None
    context.user_data["bulk_status"] = None
    context.user_data["bulk_assigned_to_id"] = None
    
    # Show action selection
    message = get_message("bulk_action_prompt", language)
    keyboard = bulk_action_keyboard(language)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message, reply_markup=keyboard)
    
    return BulkActionState.ACTION


async def bulk_action_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب نوع bulk action"""
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
            await query.edit_message_text(get_message("bulk_not_allowed", language))
            return ConversationHandler.END
        
        # Extract action from callback data
        callback_data = query.data
        
        if callback_data == CALLBACK_BULK_CANCEL:
            await query.edit_message_text(get_message("bulk_cancelled", language))
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Actions: status, assign, unassign, delete
        action_map = {
            "bulk_status": "status",
            "bulk_assign": "assign",
            "bulk_unassign": "unassign",
            "bulk_delete": "delete",
        }
        
        action = None
        for key, value in action_map.items():
            if callback_data == key:
                action = value
                break
        
        if not action:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        context.user_data["bulk_action"] = action
        
        # For status action, show status selection
        if action == "status":
            message = get_message("bulk_status_select", language)
            keyboard = status_keyboard(language)
            await query.edit_message_text(message, reply_markup=keyboard)
            return BulkActionState.ACTION
        
        # For assign action, show user selection
        if action == "assign":
            # Get current user to filter by branch if needed
            branch_id = None
            if current_user.get("role") == "branch_admin":
                branch_id = current_user.get("branch_id")
            
            # Get list of users
            users = await api_client.get_users(token, role=None, branch_id=branch_id)
            
            if not users:
                await query.edit_message_text(get_message("assign_no_users", language))
                return ConversationHandler.END
            
            # Filter users to only include IT specialists and admins
            agent_roles = [
                UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
                UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
                UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
            ]
            agents = [
                u for u in users 
                if u.get("is_active", True) and 
                (u.get("role") in agent_roles or str(u.get("role", "")).lower() in [r.lower() for r in agent_roles])
            ]
            
            if not agents:
                await query.edit_message_text(get_message("assign_no_users", language))
                return ConversationHandler.END
            
            message = get_message("bulk_assign_select", language)
            keyboard = user_selection_keyboard(agents[:20], language, CALLBACK_USER_PREFIX)
            await query.edit_message_text(message, reply_markup=keyboard)
            return BulkActionState.ACTION
        
        # For unassign and delete, go directly to ticket selection
        return await show_ticket_selection(update, context)
        
    except Exception as e:
        logger.error(f"Error in bulk_action_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def bulk_status_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب status برای bulk action"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        callback_data = query.data
        
        if not callback_data.startswith(CALLBACK_STATUS_PREFIX):
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        status = callback_data.replace(CALLBACK_STATUS_PREFIX, "")
        context.user_data["bulk_status"] = status
        
        # Go to ticket selection
        return await show_ticket_selection(update, context)
        
    except Exception as e:
        logger.error(f"Error in bulk_status_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def bulk_user_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب user برای bulk assign"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        callback_data = query.data
        
        if not callback_data.startswith(CALLBACK_USER_PREFIX):
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        assigned_to_id = int(callback_data.replace(CALLBACK_USER_PREFIX, ""))
        context.user_data["bulk_assigned_to_id"] = assigned_to_id
        
        # Go to ticket selection
        return await show_ticket_selection(update, context)
        
    except Exception as e:
        logger.error(f"Error in bulk_user_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def show_ticket_selection(update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست تیکت‌ها برای انتخاب"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            if update.callback_query:
                await update.callback_query.edit_message_text(get_message("login_required", language))
            else:
                await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # Get current user to filter by branch if needed
        current_user = await api_client.get_current_user(token)
        branch_id = None
        if current_user and current_user.get("role") == "branch_admin":
            branch_id = current_user.get("branch_id")
        
        # Get tickets (pending and in_progress for easier selection)
        tickets_pending = await api_client.search_tickets(
            token=token,
            page=1,
            page_size=50,
            status="pending",
            branch_id=branch_id
        )
        tickets_in_progress = await api_client.search_tickets(
            token=token,
            page=1,
            page_size=50,
            status="in_progress",
            branch_id=branch_id
        )
        
        # Combine tickets
        all_tickets = []
        if tickets_pending:
            all_tickets.extend(tickets_pending.get("items", []))
        if tickets_in_progress:
            all_tickets.extend(tickets_in_progress.get("items", []))
        
        if not all_tickets:
            message = get_message("bulk_no_tickets", language)
            if update.callback_query:
                await update.callback_query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Store tickets in context
        context.user_data["bulk_available_tickets"] = all_tickets[:50]  # Limit to 50
        
        # Build message
        action = context.user_data.get("bulk_action", "unknown")
        action_text = get_message(f"bulk_action_{action}", language, default=action)
        
        selected_count = len(context.user_data.get("bulk_selected_tickets", set()))
        
        message = get_message("bulk_ticket_selection", language).format(
            action=action_text,
            total=len(all_tickets),
            selected=selected_count
        )
        
        # Create keyboard with ticket selection
        from app.telegram_bot.keyboards import bulk_ticket_selection_keyboard
        keyboard = bulk_ticket_selection_keyboard(
            all_tickets[:50],
            context.user_data.get("bulk_selected_tickets", set()),
            language
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text(message, reply_markup=keyboard)
        
        return BulkActionState.TICKET_SELECTION
        
    except Exception as e:
        logger.error(f"Error in show_ticket_selection: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return ConversationHandler.END


async def bulk_ticket_toggle(update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle انتخاب تیکت"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        callback_data = query.data
        
        if not callback_data.startswith(CALLBACK_BULK_SELECT):
            return BulkActionState.TICKET_SELECTION
        
        ticket_id = int(callback_data.replace(CALLBACK_BULK_SELECT, ""))
        
        # Toggle selection
        selected_tickets: Set[int] = context.user_data.get("bulk_selected_tickets", set())
        if ticket_id in selected_tickets:
            selected_tickets.remove(ticket_id)
        else:
            selected_tickets.add(ticket_id)
        
        context.user_data["bulk_selected_tickets"] = selected_tickets
        
        # Update keyboard
        all_tickets = context.user_data.get("bulk_available_tickets", [])
        
        from app.telegram_bot.keyboards import bulk_ticket_selection_keyboard
        keyboard = bulk_ticket_selection_keyboard(
            all_tickets[:50],
            selected_tickets,
            language
        )
        
        # Update message
        action = context.user_data.get("bulk_action", "unknown")
        action_text = get_message(f"bulk_action_{action}", language, default=action)
        
        message = get_message("bulk_ticket_selection", language).format(
            action=action_text,
            total=len(all_tickets),
            selected=len(selected_tickets)
        )
        
        await query.edit_message_text(message, reply_markup=keyboard)
        return BulkActionState.TICKET_SELECTION
        
    except Exception as e:
        logger.error(f"Error in bulk_ticket_toggle: {e}", exc_info=True)
        return BulkActionState.TICKET_SELECTION


async def bulk_confirm(update, context: ContextTypes.DEFAULT_TYPE):
    """تایید و اجرای bulk action"""
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
            await query.edit_message_text(get_message("bulk_not_allowed", language))
            return ConversationHandler.END
        
        # Get selected tickets
        selected_tickets: Set[int] = context.user_data.get("bulk_selected_tickets", set())
        
        if not selected_tickets:
            await query.edit_message_text(get_message("bulk_no_tickets_selected", language))
            return BulkActionState.TICKET_SELECTION
        
        action = context.user_data.get("bulk_action")
        if not action:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        # Prepare bulk action
        status = context.user_data.get("bulk_status")
        assigned_to_id = context.user_data.get("bulk_assigned_to_id")
        
        # Execute bulk action
        result = await api_client.bulk_action_tickets(
            token=token,
            ticket_ids=list(selected_tickets),
            action=action,
            status=status,
            assigned_to_id=assigned_to_id
        )
        
        if not result:
            await query.edit_message_text(get_message("bulk_error", language))
            return ConversationHandler.END
        
        # Show result
        success_count = result.get("success_count", 0)
        failed_count = result.get("failed_count", 0)
        
        if failed_count == 0:
            message = get_message("bulk_success", language).format(
                count=success_count,
                action=get_message(f"bulk_action_{action}", language, default=action)
            )
        else:
            message = get_message("bulk_partial_success", language).format(
                success=success_count,
                failed=failed_count,
                action=get_message(f"bulk_action_{action}", language, default=action)
            )
        
        await query.edit_message_text(message)
        logger.info(f"User {user_id} performed bulk action {action} on {success_count} tickets")
        
        # Cleanup
        context.user_data.pop("bulk_selected_tickets", None)
        context.user_data.pop("bulk_action", None)
        context.user_data.pop("bulk_status", None)
        context.user_data.pop("bulk_assigned_to_id", None)
        context.user_data.pop("bulk_available_tickets", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in bulk_confirm: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای bulk actions"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("bulk", bulk_action_start),
            CallbackQueryHandler(bulk_action_start, pattern=f"^{CALLBACK_BULK_ACTION}$"),
        ],
        states={
            BulkActionState.ACTION: [
                CallbackQueryHandler(bulk_action_selected, pattern="^(bulk_status|bulk_assign|bulk_unassign|bulk_delete|bulk_cancel)$"),
                CallbackQueryHandler(bulk_status_selected, pattern=f"^{CALLBACK_STATUS_PREFIX}"),
                CallbackQueryHandler(bulk_user_selected, pattern=f"^{CALLBACK_USER_PREFIX}"),
            ],
            BulkActionState.TICKET_SELECTION: [
                CallbackQueryHandler(bulk_ticket_toggle, pattern=f"^{CALLBACK_BULK_SELECT}"),
                CallbackQueryHandler(bulk_confirm, pattern=f"^{CALLBACK_BULK_CONFIRM}$"),
                CallbackQueryHandler(bulk_action_start, pattern=f"^{CALLBACK_BULK_CANCEL}$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "bulk_action_start",
    "bulk_action_selected",
    "bulk_status_selected",
    "bulk_user_selected",
    "show_ticket_selection",
    "bulk_ticket_toggle",
    "bulk_confirm",
]

