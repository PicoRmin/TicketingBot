"""
SLA Alerts handlers - EP3-S2: هشدارهای SLA
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_ALERTS,
    CALLBACK_ALERTS_FILTER_WARNING,
    CALLBACK_ALERTS_FILTER_BREACH,
    CALLBACK_ALERTS_FILTER_ALL,
    CALLBACK_ALERTS_TICKET,
    CALLBACK_TICKET_DETAIL,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import sla_alerts_filter_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import AlertsState
from app.telegram_bot.utils import get_user_id

logger = logging.getLogger(__name__)


def format_time_remaining(seconds: float) -> str:
    """فرمت کردن زمان باقی‌مانده به صورت خوانا"""
    if seconds < 0:
        return "⏰ گذشته"
    
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} روز")
    if hours > 0:
        parts.append(f"{hours} ساعت")
    if minutes > 0:
        parts.append(f"{minutes} دقیقه")
    
    if not parts:
        return "کمتر از یک دقیقه"
    
    return " و ".join(parts)


def get_alert_type_emoji(alert_type: str) -> str:
    """دریافت emoji بر اساس نوع هشدار"""
    if alert_type == "warning":
        return "🟡"
    elif alert_type == "breach":
        return "🔴"
    elif alert_type == "escalated":
        return "⚠️"
    return "⚪"


def get_status_emoji(status: Optional[str]) -> str:
    """دریافت emoji بر اساس وضعیت SLA"""
    if not status:
        return "⚪"
    status_lower = status.lower()
    if status_lower == "on_time":
        return "🟢"
    elif status_lower == "warning":
        return "🟡"
    elif status_lower == "breached":
        return "🔴"
    return "⚪"


async def alerts_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای مشاهده هشدارهای SLA"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Initialize context
    context.user_data["alerts_filter"] = "all"  # all, warning, breach
    
    # Show filter selection
    message = get_message("alerts_prompt", language)
    keyboard = sla_alerts_filter_keyboard(language, "all")
    
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message, reply_markup=keyboard)
    
    return AlertsState.FILTER


async def alerts_filter_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب فیلتر هشدارها"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        callback_data = query.data
        
        # Determine filter
        if callback_data == CALLBACK_ALERTS_FILTER_WARNING:
            filter_type = "warning"
        elif callback_data == CALLBACK_ALERTS_FILTER_BREACH:
            filter_type = "breach"
        elif callback_data == CALLBACK_ALERTS_FILTER_ALL:
            filter_type = "all"
        else:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
        context.user_data["alerts_filter"] = filter_type
        
        # Show results
        return await show_alerts(update, context, filter_type)
        
    except Exception as e:
        logger.error(f"Error in alerts_filter_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def show_alerts(update, context: ContextTypes.DEFAULT_TYPE, filter_type: str = "all"):
    """نمایش لیست هشدارهای SLA"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            if update.message:
                await update.message.reply_text(get_message("login_required", language))
            else:
                query = update.callback_query
                await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # Get current user to check permissions
        current_user = await api_client.get_current_user(token)
        if not current_user:
            if update.message:
                await update.message.reply_text(get_message("login_required", language))
            else:
                query = update.callback_query
                await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # Check if user is admin (alerts are admin-only)
        user_role = current_user.get("role")
        admin_roles = ["admin", "central_admin", "branch_admin", "it_specialist"]
        if user_role not in admin_roles and str(user_role).lower() not in [r.lower() for r in admin_roles]:
            message = get_message("alerts_not_allowed", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                query = update.callback_query
                await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Get SLA logs with filters
        # For warnings: response_status=warning OR resolution_status=warning
        # For breaches: response_status=breached OR resolution_status=breached
        # For all: (response_status IN (warning, breached)) OR (resolution_status IN (warning, breached))
        
        alerts: List[Dict[str, Any]] = []
        
        if filter_type == "warning":
            # Get warnings (response or resolution)
            response_warnings = await api_client.get_sla_logs(
                token=token,
                page=1,
                page_size=50,
                response_status="warning"
            )
            resolution_warnings = await api_client.get_sla_logs(
                token=token,
                page=1,
                page_size=50,
                resolution_status="warning"
            )
            
            # Combine and deduplicate
            seen_ids = set()
            if response_warnings:
                for log in response_warnings:
                    if log.get("id") not in seen_ids:
                        alerts.append(log)
                        seen_ids.add(log.get("id"))
            if resolution_warnings:
                for log in resolution_warnings:
                    if log.get("id") not in seen_ids:
                        alerts.append(log)
                        seen_ids.add(log.get("id"))
        
        elif filter_type == "breach":
            # Get breaches (response or resolution)
            response_breaches = await api_client.get_sla_logs(
                token=token,
                page=1,
                page_size=50,
                response_status="breached"
            )
            resolution_breaches = await api_client.get_sla_logs(
                token=token,
                page=1,
                page_size=50,
                resolution_status="breached"
            )
            
            # Combine and deduplicate
            seen_ids = set()
            if response_breaches:
                for log in response_breaches:
                    if log.get("id") not in seen_ids:
                        alerts.append(log)
                        seen_ids.add(log.get("id"))
            if resolution_breaches:
                for log in resolution_breaches:
                    if log.get("id") not in seen_ids:
                        alerts.append(log)
                        seen_ids.add(log.get("id"))
        
        else:  # all
            # Get all warnings and breaches
            all_alerts = await api_client.get_sla_logs(
                token=token,
                page=1,
                page_size=100
            )
            
            # Filter to only include warnings and breaches
            if all_alerts:
                for log in all_alerts:
                    response_status = log.get("response_status", "").lower()
                    resolution_status = log.get("resolution_status", "").lower()
                    if response_status in ("warning", "breached") or resolution_status in ("warning", "breached"):
                        alerts.append(log)
        
        if not alerts:
            filter_text = get_message(f"alerts_filter_{filter_type}", language, default=filter_type)
            message = get_message("alerts_no_alerts", language).format(filter=filter_text)
            
            # Update keyboard
            keyboard = sla_alerts_filter_keyboard(language, filter_type)
            
            if update.message:
                await update.message.reply_text(message, reply_markup=keyboard)
            else:
                query = update.callback_query
                await query.edit_message_text(message, reply_markup=keyboard)
            
            return AlertsState.FILTER
        
        # Sort alerts by severity (breach first, then warning)
        def sort_key(log: Dict[str, Any]) -> int:
            response_status = log.get("response_status", "").lower()
            resolution_status = log.get("resolution_status", "").lower()
            if "breached" in [response_status, resolution_status]:
                return 0  # Breach first
            elif "warning" in [response_status, resolution_status]:
                return 1  # Warning second
            return 2
        
        alerts.sort(key=sort_key)
        
        # Limit to 20 alerts per message
        alerts_to_show = alerts[:20]
        
        # Build message
        filter_text = get_message(f"alerts_filter_{filter_type}", language, default=filter_type)
        message = get_message("alerts_header", language).format(
            filter=filter_text,
            count=len(alerts),
            showing=len(alerts_to_show)
        )
        
        # Add alerts
        now = datetime.now(timezone.utc)
        for idx, alert in enumerate(alerts_to_show, 1):
            ticket_number = alert.get("ticket_number", f"T-{alert.get('ticket_id')}")
            response_status = alert.get("response_status", "")
            resolution_status = alert.get("resolution_status", "")
            
            # Determine alert type and emoji
            alert_types = []
            if response_status and response_status.lower() in ("warning", "breached"):
                alert_types.append(f"پاسخ: {get_status_emoji(response_status)}")
            if resolution_status and resolution_status.lower() in ("warning", "breached"):
                alert_types.append(f"حل: {get_status_emoji(resolution_status)}")
            
            alert_type_text = " | ".join(alert_types) if alert_types else "نامشخص"
            
            # Calculate time remaining or passed
            target_response_time = None
            target_resolution_time = None
            if alert.get("target_response_time"):
                target_response_time = datetime.fromisoformat(alert["target_response_time"].replace("Z", "+00:00"))
            if alert.get("target_resolution_time"):
                target_resolution_time = datetime.fromisoformat(alert["target_resolution_time"].replace("Z", "+00:00"))
            
            time_info = ""
            if target_response_time and not alert.get("actual_response_time"):
                remaining = (target_response_time - now).total_seconds()
                time_info = f"⏰ پاسخ: {format_time_remaining(remaining)}"
            elif target_resolution_time and not alert.get("actual_resolution_time"):
                remaining = (target_resolution_time - now).total_seconds()
                time_info = f"⏰ حل: {format_time_remaining(remaining)}"
            
            message += f"\n{idx}. {get_alert_type_emoji(response_status or resolution_status)} {ticket_number}\n"
            message += f"   {alert_type_text}\n"
            if time_info:
                message += f"   {time_info}\n"
            if alert.get("escalated"):
                message += f"   ⚠️ Escalated\n"
            message += "\n"
        
        if len(alerts) > 20:
            message += f"\n... و {len(alerts) - 20} هشدار دیگر"
        
        # Limit message length
        if len(message) > 4000:
            message = message[:3900] + "\n\n... (پیام طولانی است)"
        
        # Create keyboard with filter options and ticket details
        from app.telegram_bot.keyboards import sla_alerts_results_keyboard
        keyboard = sla_alerts_results_keyboard(alerts_to_show, language, filter_type)
        
        if update.message:
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            query = update.callback_query
            await query.edit_message_text(message, reply_markup=keyboard)
        
        # Store alerts in context
        context.user_data["alerts_list"] = alerts_to_show
        
        return AlertsState.RESULTS
        
    except Exception as e:
        logger.error(f"Error in show_alerts: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            query = update.callback_query
            await query.edit_message_text(error_msg)
        return ConversationHandler.END


async def alert_ticket_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب تیکت از لیست هشدارها برای مشاهده جزئیات"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        callback_data = query.data
        
        if not callback_data.startswith(CALLBACK_ALERTS_TICKET):
            return AlertsState.RESULTS
        
        ticket_id = int(callback_data.replace(CALLBACK_ALERTS_TICKET, ""))
        
        # Get ticket to get ticket number
        token = sessions.get_token(user_id)
        if not token:
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        ticket = await api_client.get_ticket_by_id(token, ticket_id)
        if not ticket:
            await query.edit_message_text(get_message("ticket_detail_not_found", language))
            return AlertsState.RESULTS
        
        ticket_number = ticket.get("ticket_number", f"T-{ticket_id}")
        
        # Redirect to ticket detail using callback
        from app.telegram_bot.handlers.ticket_detail import ticket_detail_start
        # Simulate callback query for ticket detail
        query.data = f"{CALLBACK_TICKET_DETAIL}{ticket_id}"
        return await ticket_detail_start(update, context)
        
    except Exception as e:
        logger.error(f"Error in alert_ticket_selected: {e}", exc_info=True)
        return AlertsState.RESULTS


def get_handler():
    """برگرداندن conversation handler برای مشاهده هشدارهای SLA"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("alerts", alerts_start),
            CallbackQueryHandler(alerts_start, pattern=f"^{CALLBACK_ALERTS}$"),
        ],
        states={
            AlertsState.FILTER: [
                CallbackQueryHandler(
                    alerts_filter_selected,
                    pattern=f"^({CALLBACK_ALERTS_FILTER_WARNING}|{CALLBACK_ALERTS_FILTER_BREACH}|{CALLBACK_ALERTS_FILTER_ALL})$"
                ),
            ],
            AlertsState.RESULTS: [
                CallbackQueryHandler(alert_ticket_selected, pattern=f"^{CALLBACK_ALERTS_TICKET}"),
                CallbackQueryHandler(
                    alerts_filter_selected,
                    pattern=f"^({CALLBACK_ALERTS_FILTER_WARNING}|{CALLBACK_ALERTS_FILTER_BREACH}|{CALLBACK_ALERTS_FILTER_ALL})$"
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "alerts_start",
    "alerts_filter_selected",
    "show_alerts",
    "alert_ticket_selected",
]

