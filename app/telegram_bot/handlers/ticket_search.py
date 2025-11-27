"""
Ticket search and filter handlers - EP2-S3: فیلتر و جستجوی پیشرفته تیکت‌ها
"""
import logging
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.enums import Language, TicketStatus, TicketPriority, TicketCategory
from app.telegram_bot import sessions
from app.telegram_bot.callbacks import (
    CALLBACK_SEARCH,
    CALLBACK_SEARCH_FILTER_STATUS,
    CALLBACK_SEARCH_FILTER_PRIORITY,
    CALLBACK_SEARCH_FILTER_CATEGORY,
    CALLBACK_SEARCH_FILTER_DATE,
)
from app.telegram_bot.handlers.common import cancel_command, require_token, send_main_menu
from app.telegram_bot.i18n import get_category_name, get_message, get_status_name
from app.telegram_bot.keyboards import (
    search_filter_keyboard,
    status_keyboard,
    priority_keyboard,
    category_keyboard,
    date_filter_keyboard,
)
from app.telegram_bot.runtime import api_client
from app.telegram_bot.states import SearchState
from app.telegram_bot.utils import get_chat_id, get_user_id

logger = logging.getLogger(__name__)


def format_datetime(dt_str: str, language: Language) -> str:
    """فرمت‌بندی تاریخ برای نمایش"""
    try:
        if not dt_str:
            return ""
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        if language == Language.FA:
            return dt.strftime("%Y/%m/%d %H:%M")
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_str[:16] if dt_str else ""


async def search_ticket_start(update, context: ContextTypes.DEFAULT_TYPE):
    """نقطه ورود برای جستجو و فیلتر تیکت‌ها"""
    token = await require_token(update, context)
    if not token:
        return ConversationHandler.END

    user_id = get_user_id(update)
    language = sessions.get_language(user_id)
    
    # Initialize search filters
    context.user_data["search_filters"] = {}
    
    prompt = get_message("search_prompt", language)
    
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(
            chat_id=get_chat_id(update),
            text=prompt,
            reply_markup=search_filter_keyboard(language)
        )
    else:
        await update.message.reply_text(
            prompt,
            reply_markup=search_filter_keyboard(language)
        )
    
    return SearchState.FILTER


async def search_filter_selection(update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت انتخاب نوع فیلتر"""
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
        search_filters = context.user_data.setdefault("search_filters", {})
        
        # Handle filter type selection
        if callback_data == "search_status":
            # Filter by status
            await query.edit_message_text(
                get_message("search_filter_status_prompt", language),
                reply_markup=status_keyboard(language)
            )
            return SearchState.FILTER
            
        elif callback_data == "search_priority":
            # Filter by priority
            await query.edit_message_text(
                get_message("search_filter_priority_prompt", language),
                reply_markup=priority_keyboard(language)
            )
            return SearchState.FILTER
            
        elif callback_data == "search_category":
            # Filter by category
            await query.edit_message_text(
                get_message("search_filter_category_prompt", language),
                reply_markup=category_keyboard(language)
            )
            return SearchState.FILTER
            
        elif callback_data == "search_date":
            # Filter by date
            await query.edit_message_text(
                get_message("search_filter_date_prompt", language),
                reply_markup=date_filter_keyboard(language)
            )
            return SearchState.FILTER
            
        elif callback_data == "search_text":
            # Text search
            await query.edit_message_text(get_message("search_text_prompt", language))
            return SearchState.RESULTS
            
        elif callback_data == "search_execute":
            # Execute search with current filters
            return await execute_search(update, context)
            
        elif callback_data == "search_reset":
            # Reset filters
            context.user_data["search_filters"] = {}
            await query.edit_message_text(
                get_message("search_filters_reset", language),
                reply_markup=search_filter_keyboard(language)
            )
            return SearchState.FILTER
            
        elif callback_data.startswith("status_"):
            # Status selected (from status_keyboard)
            from app.telegram_bot.callbacks import CALLBACK_STATUS_PREFIX
            status_value = callback_data.replace(CALLBACK_STATUS_PREFIX, "")
            search_filters["status"] = status_value
            await query.edit_message_text(
                get_message("search_filter_status_selected", language).format(
                    status=get_status_name(status_value, language)
                ),
                reply_markup=search_filter_keyboard(language, search_filters)
            )
            return SearchState.FILTER
            
        elif callback_data.startswith("priority_"):
            # Priority selected (from priority_keyboard)
            from app.telegram_bot.callbacks import CALLBACK_PRIORITY_PREFIX
            priority_value = callback_data.replace(CALLBACK_PRIORITY_PREFIX, "")
            search_filters["priority"] = priority_value
            priority_text = get_message(f"priority_{priority_value}", language, default=priority_value)
            await query.edit_message_text(
                get_message("search_filter_priority_selected", language).format(
                    priority=priority_text
                ),
                reply_markup=search_filter_keyboard(language, search_filters)
            )
            return SearchState.FILTER
            
        elif callback_data.startswith("category_"):
            # Category selected (from category_keyboard)
            from app.telegram_bot.callbacks import CALLBACK_CATEGORY_PREFIX
            category_value = callback_data.replace(CALLBACK_CATEGORY_PREFIX, "")
            search_filters["category"] = category_value
            await query.edit_message_text(
                get_message("search_filter_category_selected", language).format(
                    category=get_category_name(category_value, language)
                ),
                reply_markup=search_filter_keyboard(language, search_filters)
            )
            return SearchState.FILTER
            
        elif callback_data.startswith(CALLBACK_SEARCH_FILTER_DATE):
            # Date filter selected
            date_value = callback_data.replace(CALLBACK_SEARCH_FILTER_DATE, "")
            search_filters["date_filter"] = date_value
            
            # Calculate date range
            today = date.today()
            if date_value == "today":
                date_from = today.isoformat()
                date_to = today.isoformat()
            elif date_value == "week":
                date_from = (today - timedelta(days=7)).isoformat()
                date_to = today.isoformat()
            elif date_value == "month":
                date_from = (today - timedelta(days=30)).isoformat()
                date_to = today.isoformat()
            else:
                date_from = None
                date_to = None
            
            if date_from:
                search_filters["date_from"] = date_from
                search_filters["date_to"] = date_to
            
            date_name = get_message(f"search_date_{date_value}", language, default=date_value)
            await query.edit_message_text(
                get_message("search_filter_date_selected", language).format(date=date_name),
                reply_markup=search_filter_keyboard(language, search_filters)
            )
            return SearchState.FILTER
        
    except Exception as e:
        logger.error(f"Error in search_filter_selection: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await query.edit_message_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def search_text_input(update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت متن جستجو"""
    try:
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        
        search_text = update.message.text.strip()
        
        if len(search_text) < 2:
            await update.message.reply_text(
                get_message("search_text_too_short", language)
            )
            return SearchState.RESULTS
        
        context.user_data.setdefault("search_filters", {})["search_text"] = search_text
        
        return await execute_search(update, context)
        
    except Exception as e:
        logger.error(f"Error in search_text_input: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        await update.message.reply_text(get_message("error_occurred", language))
        return ConversationHandler.END


async def execute_search(update, context: ContextTypes.DEFAULT_TYPE):
    """اجرای جستجو با فیلترهای انتخاب شده"""
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
        
        search_filters = context.user_data.get("search_filters", {})
        
        # Prepare search parameters
        status = search_filters.get("status")
        priority = search_filters.get("priority")
        category = search_filters.get("category")
        date_from = search_filters.get("date_from")
        date_to = search_filters.get("date_to")
        search_text = search_filters.get("search_text")
        
        # Execute search
        results = await api_client.search_tickets(
            token=token,
            page=1,
            page_size=20,
            status=status,
            priority=priority,
            category=category,
            date_from=date_from,
            date_to=date_to,
            search_text=search_text
        )
        
        if not results or results.get("total", 0) == 0:
            message = get_message("search_empty", language)
            if update.message:
                await update.message.reply_text(message)
            else:
                query = update.callback_query
                await query.edit_message_text(message)
            await send_main_menu(update, context)
            return ConversationHandler.END
        
        # Build results message
        total = results.get("total", 0)
        items = results.get("items", [])
        
        header = get_message("search_results", language).format(total=total)
        message_parts = [header]
        
        # Build filter summary
        filter_summary_parts = []
        if status:
            filter_summary_parts.append(
                f"📊 وضعیت: {get_status_name(status, language)}"
            )
        if priority:
            filter_summary_parts.append(
                f"⚡ اولویت: {get_message(f'priority_{priority}', language, default=priority)}"
            )
        if category:
            filter_summary_parts.append(
                f"📂 دسته: {get_category_name(category, language)}"
            )
        if date_from:
            filter_summary_parts.append(
                f"📅 تاریخ: {date_from} تا {date_to or date_from}"
            )
        if search_text:
            filter_summary_parts.append(
                f"🔤 جستجو: {search_text}"
            )
        
        if filter_summary_parts:
            message_parts.append("\n" + " | ".join(filter_summary_parts) + "\n")
        
        # Add ticket items
        for ticket in items[:10]:  # Limit to 10 tickets
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(ticket.get("priority", "medium"), "🟡")
            
            created_at = format_datetime(ticket.get("created_at", ""), language)
            
            ticket_priority = ticket.get("priority", "medium")
            priority_text = get_message(f"priority_{ticket_priority}", language, default="متوسط")
            ticket_item = (
                f"🔹 {ticket.get('ticket_number', '')}\n"
                f"📌 {ticket.get('title', '')}\n"
                f"{priority_emoji} {priority_text} | "
                f"📊 {get_status_name(ticket.get('status', ''), language)}\n"
                f"📅 {created_at}\n"
                f"━━━━━━━━━━━━━━━━\n"
            )
            message_parts.append(ticket_item)
        
        if len(items) > 10:
            message_parts.append(f"\n... و {len(items) - 10} تیکت دیگر")
        
        message = "\n".join(message_parts)
        
        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n... (نتایج بیشتر در پنل وب قابل مشاهده است)"
        
        if update.message:
            await update.message.reply_text(message)
        else:
            query = update.callback_query
            await query.edit_message_text(message)
        
        logger.info(f"User {user_id} searched tickets: filters={search_filters}, results={total}")
        
        # Cleanup
        context.user_data.pop("search_filters", None)
        
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in execute_search: {e}", exc_info=True)
        user_id = get_user_id(update)
        language = sessions.get_language(user_id)
        error_msg = get_message("error_occurred", language)
        if update.message:
            await update.message.reply_text(error_msg)
        else:
            query = update.callback_query
            await query.edit_message_text(error_msg)
        return ConversationHandler.END


def get_handler():
    """برگرداندن conversation handler برای جستجو و فیلتر"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("search", search_ticket_start),
            CallbackQueryHandler(search_ticket_start, pattern=f"^{CALLBACK_SEARCH}$"),
        ],
        states={
            SearchState.FILTER: [
                CallbackQueryHandler(search_filter_selection),
            ],
            SearchState.RESULTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_text_input),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
        per_message=False,
    )


__all__ = [
    "get_handler",
    "search_ticket_start",
    "search_filter_selection",
    "search_text_input",
    "execute_search",
]

