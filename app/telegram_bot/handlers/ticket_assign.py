"""
Ticket assignment handlers - EP2-S5: تخصیص تیکت از طریق بات
"""
import logging
from typing import Any, Dict, List, Optional

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
    CALLBACK_TICKET_ASSIGN,
    CALLBACK_USER_PREFIX,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import user_selection_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import AssignState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


def check_manager_permission(user_role: str) -> bool:
    """بررسی دسترسی مدیر برای تخصیص تیکت"""
    role_values = [
        UserRole.ADMIN.value if hasattr(UserRole.ADMIN, 'value') else "admin",
        UserRole.CENTRAL_ADMIN.value if hasattr(UserRole.CENTRAL_ADMIN, 'value') else "central_admin",
        UserRole.BRANCH_ADMIN.value if hasattr(UserRole.BRANCH_ADMIN, 'value') else "branch_admin",
        UserRole.IT_SPECIALIST.value if hasattr(UserRole.IT_SPECIALIST, 'value') else "it_specialist",
    ]
    return user_role in role_values or str(user_role).lower() in [r.lower() for r in role_values]


async def get_agent_workload(token: str, user_id: int) -> int:
    """دریافت تعداد تیکت‌های assigned شده به یک agent"""
    try:
        # Get tickets assigned to this user with pending or in_progress status
        # Try pending first
        tickets_pending = await api_client.search_tickets(
            token=token,
            page=1,
            page_size=100,
            status="pending"
        )
        tickets_in_progress = await api_client.search_tickets(
            token=token,
            page=1,
            page_size=100,
            status="in_progress"
        )
        
        # Count tickets assigned to this user
        count = 0
        if tickets_pending:
            items = tickets_pending.get("items", [])
            count += len([t for t in items if t.get("assigned_to", {}).get("id") == user_id])
        if tickets_in_progress:
            items = tickets_in_progress.get("items", [])
            count += len([t for t in items if t.get("assigned_to", {}).get("id") == user_id])
        
        return count
    except Exception as e:
        logger.error(f"Error getting agent workload: {e}")
        return 0


async def assign_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای تخصیص تیکت"""
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
        message = get_message("assign_not_allowed", language)
        if update.message:
            await update.message.reply_text(message)
        else:
            await context.bot.send_message(chat_id=get_chat_id(update), text=message)
        await send_main_menu(update, context)
        return ConversationHandler.END
    
    # بررسی اگر ticket ID به عنوان آرگومان یا callback داده شده
    ticket_id = None
    ticket_number = None
    
    # Handle callback query (from inline keyboard)
    if update.callback_query:
        await update.callback_query.answer()
        callback_data = update.callback_query.data
        if callback_data.startswith(CALLBACK_TICKET_ASSIGN):
            ticket_id = int(callback_data.replace(CALLBACK_TICKET_ASSIGN, ""))
            # Get ticket to verify access
            ticket = await api_client.get_ticket_by_id(token, ticket_id)
            if not ticket:
                await update.callback_query.edit_message_text(
                    get_message("ticket_detail_not_found", language)
                )
                return ConversationHandler.END
            ticket_number = ticket.get("ticket_number", "")
            context.user_data["assign_ticket_id"] = ticket_id
            context.user_data["assign_ticket_number"] = ticket_number
            context.user_data["assign_current_assignee"] = ticket.get("assigned_to")
            
            # Show agent selection
            return await show_agent_selection(update, context, ticket_number, ticket.get("assigned_to"))
    
    # Handle command with ticket number
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            ticket_number = parts[1].strip()
            # Get ticket by number
            ticket = await api_client.get_ticket_by_number(token, ticket_number)
            if ticket:
                ticket_id = ticket.get("id")
                context.user_data["assign_ticket_id"] = ticket_id
                context.user_data["assign_ticket_number"] = ticket_number
                context.user_data["assign_current_assignee"] = ticket.get("assigned_to")
                
                return await show_agent_selection(update, context, ticket_number, ticket.get("assigned_to"))
    
    # Prompt for ticket number
    prompt = get_message("assign_prompt", language)
    await update.message.reply_text(prompt)
    return AssignState.TICKET_NUMBER


async def assign_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت شماره تیکت برای تخصیص"""
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
            await update.message.reply_text(get_message("assign_not_allowed", language))
            await send_main_menu(update, context)
            return ConversationHandler.END

        ticket_number = update.message.text.strip()
        logger.debug(f"User {user_id} assigning ticket: {ticket_number}")
        
        # Get ticket by number
        ticket = await api_client.get_ticket_by_number(token, ticket_number)
        
        if not ticket:
            await update.message.reply_text(get_message("ticket_detail_not_found", language))
            return ConversationHandler.END
        
        ticket_id = ticket.get("id")
        context.user_data["assign_ticket_id"] = ticket_id
        context.user_data["assign_ticket_number"] = ticket_number
        context.user_data["assign_current_assignee"] = ticket.get("assigned_to")
        
        return await show_agent_selection(update, context, ticket_number, ticket.get("assigned_to"))
        
    except Exception as e:
        logger.error(f"Error in assign_ticket_number: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(
            get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def show_agent_selection(update, context: ContextTypes.DEFAULT_TYPE, ticket_number: str, current_assignee: Optional[Dict[str, Any]]):
    """نمایش لیست agents برای انتخاب"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            if update.message:
                await update.message.reply_text(get_message("login_required", language))
            else:
                await context.bot.send_message(
                    chat_id=get_chat_id(update),
                    text=get_message("login_required", language)
                )
            return ConversationHandler.END
        
        # Get current user to filter by branch if needed
        current_user = await api_client.get_current_user(token)
        branch_id = None
        if current_user and current_user.get("role") == "branch_admin":
            branch_id = current_user.get("branch_id")
        
        # Get list of users (agents) - filter by IT_SPECIALIST and AGENT roles
        users = await api_client.get_users(token, role=None, branch_id=branch_id)
        
        if not users:
            message = get_message("assign_no_users", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                query = update.callback_query
                await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Filter users to only include IT specialists and admins (who can handle tickets)
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
            message = get_message("assign_no_users", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                query = update.callback_query
                await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Get workload for each agent
        agents_with_workload = []
        for agent in agents:
            workload = await get_agent_workload(token, agent.get("id"))
            agents_with_workload.append({
                **agent,
                "workload": workload
            })
        
        # Sort by workload (agents with less workload first)
        agents_with_workload.sort(key=lambda x: x.get("workload", 0))
        
        # Build message
        current_assignee_text = "هیچکس" if not current_assignee else (
            current_assignee.get("full_name") or current_assignee.get("username", "کاربر")
        )
        
        message = get_message("assign_select", language).format(
            ticket_number=ticket_number,
            current_assignee=current_assignee_text
        )
        
        # Add workload info
        message += "\n\n📊 بار کاری کارشناسان:\n"
        for agent in agents_with_workload[:10]:  # Limit to 10 agents
            agent_name = agent.get("full_name") or agent.get("username", f"User {agent.get('id')}")
            workload = agent.get("workload", 0)
            workload_emoji = "🟢" if workload < 5 else "🟡" if workload < 10 else "🔴"
            message += f"{workload_emoji} {agent_name}: {workload} تیکت باز\n"
        
        if len(agents_with_workload) > 10:
            message += f"\n... و {len(agents_with_workload) - 10} کارشناس دیگر"
        
        # Create keyboard with agents
        keyboard = user_selection_keyboard(agents_with_workload[:20], language, CALLBACK_USER_PREFIX)
        
        if update.message:
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            query = update.callback_query
            await query.edit_message_text(message, reply_markup=keyboard)
        
        # Store agents in context for later use
        context.user_data["assign_agents"] = agents_with_workload
        
        return AssignState.USER
        
    except Exception as e:
        logger.error(f"Error in show_agent_selection: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            query = update.callback_query
            await query.edit_message_text(error_msg)
        return ConversationHandler.END


async def agent_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب agent"""
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
            await query.edit_message_text(get_message("assign_not_allowed", language))
            return ConversationHandler.END
        
        # Extract user ID from callback data
        callback_data = query.data
        
        if callback_data == "no_users":
            await query.edit_message_text(get_message("assign_no_users", language))
            return ConversationHandler.END
        
        if not callback_data.startswith(CALLBACK_USER_PREFIX):
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        assigned_to_id = int(callback_data.replace(CALLBACK_USER_PREFIX, ""))
        
        # Get ticket info from context
        ticket_id = context.user_data.get("assign_ticket_id")
        ticket_number = context.user_data.get("assign_ticket_number", "")
        
        if not ticket_id:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        # Get agent info from stored agents
        agents = context.user_data.get("assign_agents", [])
        selected_agent = next((a for a in agents if a.get("id") == assigned_to_id), None)
        
        if not selected_agent:
            # Fallback: get user info from API
            users = await api_client.get_users(token)
            selected_agent = next((u for u in users if u.get("id") == assigned_to_id), None)
        
        # Assign ticket
        updated_ticket = await api_client.assign_ticket(
            token=token,
            ticket_id=ticket_id,
            assigned_to_id=assigned_to_id
        )
        
        if not updated_ticket:
            await query.edit_message_text(get_message("assign_error", language))
            return ConversationHandler.END
        
        # Success message
        assignee_name = "کاربر"
        if selected_agent:
            assignee_name = selected_agent.get("full_name") or selected_agent.get("username", "کاربر")
        
        success_message = get_message("assign_success", language).format(
            ticket_number=ticket_number,
            assignee_name=assignee_name
        )
        
        await query.edit_message_text(success_message)
        logger.info(f"User {user_id} assigned ticket {ticket_id} to user {assigned_to_id}")
        
        # Cleanup
        context.user_data.pop("assign_ticket_id", None)
        context.user_data.pop("assign_ticket_number", None)
        context.user_data.pop("assign_current_assignee", None)
        context.user_data.pop("assign_agents", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in agent_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def assign_search_agent(update, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی agent بر اساس نام"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END
        
        search_text = update.message.text.strip().lower()
        
        if len(search_text) < 2:
            await update.message.reply_text(
                get_message("assign_search_too_short", language)
            )
            return AssignState.USER
        
        # Get current user to filter by branch if needed
        current_user = await api_client.get_current_user(token)
        branch_id = None
        if current_user and current_user.get("role") == "branch_admin":
            branch_id = current_user.get("branch_id")
        
        # Get list of users
        users = await api_client.get_users(token, role=None, branch_id=branch_id)
        
        if not users:
            await update.message.reply_text(get_message("assign_no_users", language))
            return AssignState.USER
        
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
        
        # Search in agent names
        filtered_agents = [
            a for a in agents
            if search_text in (a.get("full_name", "") or "").lower() or
            search_text in (a.get("username", "") or "").lower()
        ]
        
        if not filtered_agents:
            await update.message.reply_text(
                get_message("assign_search_no_results", language).format(search=search_text)
            )
            return AssignState.USER
        
        # Get workload for each agent
        agents_with_workload = []
        for agent in filtered_agents:
            workload = await get_agent_workload(token, agent.get("id"))
            agents_with_workload.append({
                **agent,
                "workload": workload
            })
        
        # Sort by workload
        agents_with_workload.sort(key=lambda x: x.get("workload", 0))
        
        # Build message
        ticket_number = context.user_data.get("assign_ticket_number", "")
        message = get_message("assign_search_results", language).format(
            search=search_text,
            count=len(agents_with_workload)
        )
        
        # Add workload info
        message += "\n\n📊 نتایج جستجو:\n"
        for agent in agents_with_workload[:10]:
            agent_name = agent.get("full_name") or agent.get("username", f"User {agent.get('id')}")
            workload = agent.get("workload", 0)
            workload_emoji = "🟢" if workload < 5 else "🟡" if workload < 10 else "🔴"
            message += f"{workload_emoji} {agent_name}: {workload} تیکت باز\n"
        
        # Create keyboard
        keyboard = user_selection_keyboard(agents_with_workload[:20], language, CALLBACK_USER_PREFIX)
        
        # Store agents in context
        context.user_data["assign_agents"] = agents_with_workload
        
        await update.message.reply_text(message, reply_markup=keyboard)
        return AssignState.USER
        
    except Exception as e:
        logger.error(f"Error in assign_search_agent: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(get_message("error_occurred", language))
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای تخصیص تیکت"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("assign", assign_ticket_start),
            CallbackQueryHandler(assign_ticket_start, pattern=f"^{CALLBACK_TICKET_ASSIGN}"),
        ],
        states={
            AssignState.TICKET_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, assign_ticket_number)
            ],
            AssignState.USER: [
                CallbackQueryHandler(agent_selected, pattern=f"^{CALLBACK_USER_PREFIX}"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, assign_search_agent),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "assign_ticket_start",
    "assign_ticket_number",
    "show_agent_selection",
    "agent_selected",
    "assign_search_agent",
]

