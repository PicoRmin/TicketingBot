"""
SLA Report handlers - EP3-S3: گزارش SLA
"""
import logging
from typing import Any, Dict, List, Optional

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)

from app.core.enums import Language
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_SLA_REPORT,
    CALLBACK_SLA_REPORT_COMPLIANCE,
    CALLBACK_SLA_REPORT_BY_PRIORITY,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.keyboards import sla_report_type_keyboard
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import SLAReportState
from app.telegram_bot.utils import get_user_id

logger = logging.getLogger(__name__)


def create_progress_bar(percentage: float, length: int = 20) -> str:
    """ایجاد progress bar متنی"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty


def get_priority_label(priority: str) -> str:
    """دریافت label اولویت به فارسی"""
    priority_map = {
        "critical": "🔴 بحرانی",
        "high": "🟠 بالا",
        "medium": "🟡 متوسط",
        "low": "🟢 پایین"
    }
    return priority_map.get(priority.lower(), priority)


async def sla_report_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای مشاهده گزارش SLA"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Check if user is admin (reports are admin-only)
    current_user = await api_client.get_current_user(token)
    if not current_user:
        if update.message:
            await update.message.reply_text(get_message("login_required", language))
        else:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(get_message("login_required", language))
        return ConversationHandler.END
    
    user_role = current_user.get("role")
    admin_roles = ["admin", "central_admin", "branch_admin", "it_specialist"]
    if user_role not in admin_roles and str(user_role).lower() not in [r.lower() for r in admin_roles]:
        message = get_message("sla_report_not_allowed", language)
        if update.message:
            await update.message.reply_text(message)
        else:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(message)
        await send_main_menu(update, context)
        return ConversationHandler.END
    
    # Show report type selection
    message = get_message("sla_report_prompt", language)
    keyboard = sla_report_type_keyboard(language)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(message, reply_markup=keyboard)
    
    return SLAReportState.TYPE


async def sla_report_type_selected(update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب نوع گزارش SLA"""
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
        
        if callback_data == CALLBACK_SLA_REPORT_COMPLIANCE:
            return await show_compliance_report(update, context)
        elif callback_data == CALLBACK_SLA_REPORT_BY_PRIORITY:
            return await show_priority_report(update, context)
        else:
            await query.edit_message_text(get_message("error_occurred", language))
            return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in sla_report_type_selected: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def show_compliance_report(update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزارش رعایت SLA"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            query = update.callback_query
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # Get compliance report
        report = await api_client.get_sla_compliance_report(token)
        
        if not report:
            message = get_message("sla_report_error", language)
            query = update.callback_query
            await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Build message
        message = get_message("sla_report_compliance_header", language)
        
        # Overall statistics
        total = report.get("total_tickets_with_sla", 0)
        message += f"\n📊 آمار کلی:\n"
        message += f"📋 کل تیکت‌های دارای SLA: {total}\n"
        message += f"⚠️ Escalated: {report.get('escalated_count', 0)}\n"
        
        # Response statistics
        message += "\n" + "━" * 30 + "\n"
        message += "📞 آمار پاسخ:\n"
        response_on_time = report.get("response_on_time", 0)
        response_warning = report.get("response_warning", 0)
        response_breached = report.get("response_breached", 0)
        response_compliance = report.get("response_compliance_rate", 0.0)
        
        message += f"🟢 در مهلت: {response_on_time}\n"
        message += f"🟡 هشدار: {response_warning}\n"
        message += f"🔴 نقض شده: {response_breached}\n"
        message += f"📈 نرخ رعایت: {response_compliance:.2f}%\n"
        
        # Progress bar for response compliance
        progress_bar = create_progress_bar(response_compliance)
        message += f"📊 {progress_bar} {response_compliance:.1f}%\n"
        
        # Resolution statistics
        message += "\n" + "━" * 30 + "\n"
        message += "✅ آمار حل:\n"
        resolution_on_time = report.get("resolution_on_time", 0)
        resolution_warning = report.get("resolution_warning", 0)
        resolution_breached = report.get("resolution_breached", 0)
        resolution_compliance = report.get("resolution_compliance_rate", 0.0)
        
        message += f"🟢 در مهلت: {resolution_on_time}\n"
        message += f"🟡 هشدار: {resolution_warning}\n"
        message += f"🔴 نقض شده: {resolution_breached}\n"
        message += f"📈 نرخ رعایت: {resolution_compliance:.2f}%\n"
        
        # Progress bar for resolution compliance
        progress_bar = create_progress_bar(resolution_compliance)
        message += f"📊 {progress_bar} {resolution_compliance:.1f}%\n"
        
        # Summary
        message += "\n" + "━" * 30 + "\n"
        message += "📊 خلاصه:\n"
        total_breached = response_breached + resolution_breached
        total_warning = response_warning + resolution_warning
        message += f"🔴 کل نقض‌ها: {total_breached}\n"
        message += f"🟡 کل هشدارها: {total_warning}\n"
        avg_compliance = (response_compliance + resolution_compliance) / 2
        message += f"📈 میانگین رعایت: {avg_compliance:.2f}%\n"
        
        # Limit message length
        if len(message) > 4000:
            message = message[:3900] + "\n\n... (پیام طولانی است)"
        
        query = update.callback_query
        await query.edit_message_text(message)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in show_compliance_report: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        query = update.callback_query
        await query.edit_message_text(error_msg)
        return ConversationHandler.END


async def show_priority_report(update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزارش SLA بر اساس اولویت"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            query = update.callback_query
            await query.edit_message_text(get_message("login_required", language))
            return ConversationHandler.END
        
        # Get priority report
        report = await api_client.get_sla_by_priority_report(token)
        
        if not report or len(report) == 0:
            message = get_message("sla_report_no_data", language)
            query = update.callback_query
            await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Build message
        message = get_message("sla_report_priority_header", language)
        
        # Add data for each priority
        for priority_data in report:
            priority = priority_data.get("priority", "unknown")
            priority_label = get_priority_label(priority)
            
            message += "\n" + "━" * 30 + "\n"
            message += f"{priority_label}:\n"
            
            total = priority_data.get("total_tickets", 0)
            message += f"📋 کل تیکت‌ها: {total}\n"
            
            # Response stats
            response_on_time = priority_data.get("response_on_time", 0)
            response_breached = priority_data.get("response_breached", 0)
            response_compliance = priority_data.get("response_compliance_rate", 0.0)
            
            message += f"📞 پاسخ:\n"
            message += f"  🟢 در مهلت: {response_on_time}\n"
            message += f"  🔴 نقض شده: {response_breached}\n"
            message += f"  📈 رعایت: {response_compliance:.2f}%\n"
            
            # Progress bar for response
            progress_bar = create_progress_bar(response_compliance, 15)
            message += f"  📊 {progress_bar} {response_compliance:.1f}%\n"
            
            # Resolution stats
            resolution_on_time = priority_data.get("resolution_on_time", 0)
            resolution_breached = priority_data.get("resolution_breached", 0)
            resolution_compliance = priority_data.get("resolution_compliance_rate", 0.0)
            
            message += f"✅ حل:\n"
            message += f"  🟢 در مهلت: {resolution_on_time}\n"
            message += f"  🔴 نقض شده: {resolution_breached}\n"
            message += f"  📈 رعایت: {resolution_compliance:.2f}%\n"
            
            # Progress bar for resolution
            progress_bar = create_progress_bar(resolution_compliance, 15)
            message += f"  📊 {progress_bar} {resolution_compliance:.1f}%\n"
        
        # Limit message length
        if len(message) > 4000:
            message = message[:3900] + "\n\n... (پیام طولانی است)"
        
        query = update.callback_query
        await query.edit_message_text(message)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in show_priority_report: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        query = update.callback_query
        await query.edit_message_text(error_msg)
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای مشاهده گزارش SLA"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("sla_report", sla_report_start),
            CallbackQueryHandler(sla_report_start, pattern=f"^{CALLBACK_SLA_REPORT}$"),
        ],
        states={
            SLAReportState.TYPE: [
                CallbackQueryHandler(
                    sla_report_type_selected,
                    pattern=f"^({CALLBACK_SLA_REPORT_COMPLIANCE}|{CALLBACK_SLA_REPORT_BY_PRIORITY})$"
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "sla_report_start",
    "sla_report_type_selected",
    "show_compliance_report",
    "show_priority_report",
]

