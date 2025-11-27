"""
Ticket SLA handlers - EP3-S1: نمایش SLA تیکت
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language
from app.telegram_bot import sessions
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_message
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import TrackState
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


def get_status_color(status: Optional[str]) -> str:
    """دریافت رنگ بر اساس وضعیت SLA"""
    if not status:
        return "⚪ سفید"
    status_lower = status.lower()
    if status_lower == "on_time":
        return "🟢 سبز"
    elif status_lower == "warning":
        return "🟡 زرد"
    elif status_lower == "breached":
        return "🔴 قرمز"
    return "⚪ سفید"


def calculate_progress_percentage(ticket_created: datetime, target_time: datetime, current_time: datetime) -> float:
    """محاسبه درصد پیشرفت SLA"""
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    if ticket_created.tzinfo is None:
        ticket_created = ticket_created.replace(tzinfo=timezone.utc)
    
    # Calculate total duration (from ticket creation to target)
    total_seconds = (target_time - ticket_created).total_seconds()
    if total_seconds <= 0:
        return 100.0
    
    # Calculate elapsed time
    elapsed_seconds = (current_time - ticket_created).total_seconds()
    
    # Calculate progress percentage
    if elapsed_seconds < 0:
        progress = 0.0
    elif elapsed_seconds >= total_seconds:
        progress = 100.0
    else:
        progress = (elapsed_seconds / total_seconds) * 100.0
    
    return max(0.0, min(100.0, progress))


def create_progress_bar(percentage: float, length: int = 10) -> str:
    """ایجاد progress bar متنی"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty


async def sla_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای مشاهده SLA تیکت"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # بررسی اگر ticket number به عنوان آرگومان داده شده
    if update.message and update.message.text:
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            ticket_number = parts[1].strip()
            # Get ticket by number
            ticket = await api_client.get_ticket_by_number(token, ticket_number)
            if ticket:
                ticket_id = ticket.get("id")
                return await show_ticket_sla(update, context, ticket_id, ticket_number)
    
    # Prompt for ticket number
    prompt = get_message("sla_prompt", language)
    await update.message.reply_text(prompt)
    return TrackState.NUMBER


async def sla_ticket_number(update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت شماره تیکت برای مشاهده SLA"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)

        if not token:
            await update.message.reply_text(get_message("login_required", language))
            return ConversationHandler.END

        ticket_number = update.message.text.strip()
        logger.debug(f"User {user_id} viewing SLA for ticket: {ticket_number}")
        
        # Get ticket by number
        ticket = await api_client.get_ticket_by_number(token, ticket_number)
        
        if not ticket:
            await update.message.reply_text(get_message("ticket_detail_not_found", language))
            return ConversationHandler.END
        
        ticket_id = ticket.get("id")
        return await show_ticket_sla(update, context, ticket_id, ticket_number)
        
    except Exception as e:
        logger.error(f"Error in sla_ticket_number: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(
            get_message("error_occurred", language) or "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
        return ConversationHandler.END


async def show_ticket_sla(update, context: ContextTypes.DEFAULT_TYPE, ticket_id: int, ticket_number: str):
    """نمایش SLA تیکت"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        token = sessions.get_token(user_id)
        
        if not token:
            if update.message:
                await update.message.reply_text(get_message("login_required", language))
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=get_message("login_required", language)
                )
            return ConversationHandler.END
        
        # Get SLA log
        sla_log = await api_client.get_ticket_sla(token, ticket_id)
        
        if not sla_log:
            message = get_message("sla_not_found", language).format(ticket_number=ticket_number)
            if update.message:
                await update.message.reply_text(message)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Get ticket to get created_at
        ticket = await api_client.get_ticket_by_id(token, ticket_id)
        if not ticket:
            message = get_message("ticket_detail_not_found", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
            return ConversationHandler.END
        
        # Parse dates
        now = datetime.now(timezone.utc)
        ticket_created = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
        target_response_time = datetime.fromisoformat(sla_log["target_response_time"].replace("Z", "+00:00"))
        target_resolution_time = datetime.fromisoformat(sla_log["target_resolution_time"].replace("Z", "+00:00"))
        
        actual_response_time = None
        if sla_log.get("actual_response_time"):
            actual_response_time = datetime.fromisoformat(sla_log["actual_response_time"].replace("Z", "+00:00"))
        
        actual_resolution_time = None
        if sla_log.get("actual_resolution_time"):
            actual_resolution_time = datetime.fromisoformat(sla_log["actual_resolution_time"].replace("Z", "+00:00"))
        
        # Calculate time remaining
        response_remaining = (target_response_time - now).total_seconds()
        resolution_remaining = (target_resolution_time - now).total_seconds()
        
        # Get statuses
        response_status = sla_log.get("response_status")
        resolution_status = sla_log.get("resolution_status")
        
        # Build message
        message = get_message("sla_header", language).format(ticket_number=ticket_number)
        
        # SLA Rule name
        sla_rule_name = sla_log.get("sla_rule_name", "SLA پیش‌فرض")
        message += f"\n📋 قانون SLA: {sla_rule_name}\n"
        
        # Response SLA
        message += "\n" + "━" * 30 + "\n"
        message += "📞 زمان پاسخ:\n"
        
        response_emoji = get_status_emoji(response_status)
        response_color = get_status_color(response_status)
        message += f"{response_emoji} وضعیت: {response_color}\n"
        
        if actual_response_time:
            message += f"✅ پاسخ داده شده: {actual_response_time.strftime('%Y-%m-%d %H:%M')}\n"
            response_delay = (actual_response_time - target_response_time).total_seconds()
            if response_delay > 0:
                message += f"⏱️ تأخیر: {format_time_remaining(response_delay)}\n"
            else:
                message += f"✅ در مهلت: {format_time_remaining(abs(response_delay))} زودتر\n"
        else:
            message += f"⏰ مهلت پاسخ: {target_response_time.strftime('%Y-%m-%d %H:%M')}\n"
            message += f"⏳ زمان باقی‌مانده: {format_time_remaining(response_remaining)}\n"
            
            # Progress bar for response
            progress = calculate_progress_percentage(ticket_created, target_response_time, now)
            progress_bar = create_progress_bar(progress)
            message += f"📊 پیشرفت: {progress_bar} {progress:.0f}%\n"
        
        # Resolution SLA
        message += "\n" + "━" * 30 + "\n"
        message += "✅ زمان حل:\n"
        
        resolution_emoji = get_status_emoji(resolution_status)
        resolution_color = get_status_color(resolution_status)
        message += f"{resolution_emoji} وضعیت: {resolution_color}\n"
        
        if actual_resolution_time:
            message += f"✅ حل شده: {actual_resolution_time.strftime('%Y-%m-%d %H:%M')}\n"
            resolution_delay = (actual_resolution_time - target_resolution_time).total_seconds()
            if resolution_delay > 0:
                message += f"⏱️ تأخیر: {format_time_remaining(resolution_delay)}\n"
            else:
                message += f"✅ در مهلت: {format_time_remaining(abs(resolution_delay))} زودتر\n"
        else:
            message += f"⏰ مهلت حل: {target_resolution_time.strftime('%Y-%m-%d %H:%M')}\n"
            message += f"⏳ زمان باقی‌مانده: {format_time_remaining(resolution_remaining)}\n"
            
            # Progress bar for resolution
            progress = calculate_progress_percentage(ticket_created, target_resolution_time, now)
            progress_bar = create_progress_bar(progress)
            message += f"📊 پیشرفت: {progress_bar} {progress:.0f}%\n"
        
        # Escalation
        if sla_log.get("escalated"):
            escalated_at = sla_log.get("escalated_at")
            if escalated_at:
                escalated_time = datetime.fromisoformat(escalated_at.replace("Z", "+00:00"))
                message += f"\n⚠️ Escalated: {escalated_time.strftime('%Y-%m-%d %H:%M')}\n"
            else:
                message += "\n⚠️ Escalated\n"
        
        # Limit message length
        if len(message) > 4000:
            message = message[:3900] + "\n\n... (پیام طولانی است)"
        
        if update.message:
            await update.message.reply_text(message)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message
            )
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in show_ticket_sla: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_msg
            )
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای مشاهده SLA تیکت"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("sla", sla_ticket_start),
        ],
        states={
            TrackState.NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sla_ticket_number)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "sla_ticket_start",
    "sla_ticket_number",
    "show_ticket_sla",
]

