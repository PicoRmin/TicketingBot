"""
Internationalization for Telegram Bot
"""
from typing import Dict
from app.core.enums import Language

# Persian messages
MESSAGES_FA: Dict[str, str] = {
    "welcome": "👋 به سیستم تیکتینگ ایرانمهر خوش آمدید!\n\n"
               "با استفاده از این ربات می‌توانید:\n"
               "• تیکت جدید ایجاد کنید\n"
               "• تیکت‌های خود را مشاهده کنید\n"
               "• وضعیت تیکت‌ها را پیگیری کنید\n\n"
               "از منوی زیر دستورات را انتخاب کنید:",
    "main_menu": "🔽 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "menu_new_ticket": "📝 تیکت جدید",
    "menu_my_tickets": "📋 تیکت‌های من",
    "menu_track_ticket": "🔍 پیگیری تیکت",
    "menu_help": "❓ راهنما",
    "menu_language": "🌐 تغییر زبان",
    "menu_login": "🔐 ورود",
    "menu_logout": "🚪 خروج",
    
    "help": "📖 راهنمای استفاده از ربات:\n\n"
            "دستورات موجود:\n"
            "/start - شروع ربات\n"
            "/newticket - ایجاد تیکت جدید\n"
            "/mytickets - مشاهده تیکت‌های من\n"
            "/track - پیگیری تیکت\n"
            "/help - نمایش این راهنما\n\n"
            "برای ایجاد تیکت جدید، از دستور /newticket استفاده کنید.",
    "login_prompt_username": "🔐 لطفاً نام کاربری خود را وارد کنید:",
    "login_prompt_password": "🔐 لطفاً رمز عبور خود را وارد کنید:",
    "login_failed": "❌ ورود ناموفق بود. لطفاً دوباره تلاش کنید.",
    "login_success": "✅ ورود با موفقیت انجام شد!",
    "login_required": "⚠️ لطفاً ابتدا وارد سیستم شوید.",
    "logout_success": "✅ با موفقیت از حساب کاربری خود خارج شدید.",
    "language_prompt": "🌐 لطفاً زبان مورد نظر خود را انتخاب کنید:",
    "language_set": "✅ زبان شما به {language_name} تغییر یافت.",
    "language_name_fa": "🇮🇷 فارسی",
    "language_name_en": "🇺🇸 انگلیسی",
    
    "new_ticket_start": "📝 ایجاد تیکت جدید\n\n"
                        "لطفاً عنوان تیکت را وارد کنید:",
    
    "new_ticket_title": "✅ عنوان دریافت شد: {title}\n\n"
                        "لطفاً توضیحات تیکت را وارد کنید:",
    
    "new_ticket_description": "✅ توضیحات دریافت شد\n\n"
                              "لطفاً شعبه را انتخاب کنید:",
    
    "new_ticket_branch": "✅ شعبه انتخاب شد: {branch_name}\n\n"
                         "لطفاً دسته‌بندی تیکت را انتخاب کنید:",
    
    "branch_skip": "⏩ بدون شعبه",
    
    "new_ticket_category": "✅ دسته‌بندی انتخاب شد: {category}\n\n"
                           "در حال ایجاد تیکت...",
    
    "ticket_created": "✅ تیکت با موفقیت ایجاد شد!\n\n"
                      "📋 شماره تیکت: {ticket_number}\n"
                      "📌 عنوان: {title}\n"
                      "📂 دسته‌بندی: {category}\n"
                      "📊 وضعیت: {status}",
    
    "ticket_created_error": "❌ خطا در ایجاد تیکت\n\n"
                            "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
    
    "description_too_short": "⚠️ توضیحات تیکت باید حداقل {min_length} کاراکتر باشد.\n\n"
                             "لطفاً توضیحات کامل‌تری وارد کنید:",
    
    "my_tickets_empty": "📭 شما هیچ تیکتی ندارید.\n\n"
                        "برای ایجاد تیکت جدید از دستور /newticket استفاده کنید.",
    
    "my_tickets_list": "📋 تیکت‌های شما:\n\n",
    
    "ticket_item": "🔹 شماره: {ticket_number}\n"
                   "📌 عنوان: {title}\n"
                   "📊 وضعیت: {status}\n"
                   "📂 دسته: {category}\n"
                   "📅 تاریخ: {created_at}\n"
                   "━━━━━━━━━━━━━━━━\n",
    
    "track_ticket_prompt": "🔍 پیگیری تیکت\n\n"
                           "لطفاً شماره تیکت را وارد کنید (مثال: T-20241111-0001):",
    
    "track_ticket_not_found": "❌ تیکت یافت نشد.\n\n"
                              "لطفاً شماره تیکت را صحیح وارد کنید.",
    
    "track_ticket_details": "📋 جزئیات تیکت:\n\n"
                            "🔹 شماره: {ticket_number}\n"
                            "📌 عنوان: {title}\n"
                            "📝 توضیحات: {description}\n"
                            "📂 دسته‌بندی: {category}\n"
                            "📊 وضعیت: {status}\n"
                            "📅 تاریخ ایجاد: {created_at}\n"
                            "🔄 آخرین به‌روزرسانی: {updated_at}",
    
    "cancel": "❌ عملیات لغو شد.",
    "cancelled": "❌ عملیات لغو شد.",
    
    "error": "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
    
    "invalid_input": "⚠️ ورودی نامعتبر است. لطفاً دوباره تلاش کنید.",
    "attachments_prompt": "📎 می‌توانید فایل‌های مرتبط با تیکت را ارسال کنید (تصاویر یا اسناد).\n"
                          "برای پایان، گزینه «تمام» را بفرستید یا دکمه زیر را بزنید.",
    "attachments_skip_button": "⏩ بدون فایل",
    "attachments_done": "✅ فرآیند ایجاد تیکت به پایان رسید.",
    "attachments_text_hint": "ℹ️ اگر می‌خواهید بدون فایل ادامه دهید، «تمام» را ارسال کنید یا از دستور /skip استفاده کنید.",
    "attachment_saved": "✅ فایل {file_name} با موفقیت ذخیره شد.",
    "attachment_error": "❌ خطا در ذخیره فایل. لطفاً دوباره تلاش کنید.",
    
    "category_internet": "🌐 اینترنت",
    "category_equipment": "💻 تجهیزات",
    "category_software": "📱 نرم‌افزار",
    "category_other": "📦 سایر",
    
    "status_pending": "⏳ در انتظار",
    "status_in_progress": "🔄 در حال انجام",
    "status_resolved": "✅ حل شده",
    "status_closed": "🔒 بسته شده",
}

# English messages
MESSAGES_EN: Dict[str, str] = {
    "welcome": "👋 Welcome to Iranmehr Ticketing System!\n\n"
               "Using this bot you can:\n"
               "• Create new tickets\n"
               "• View your tickets\n"
               "• Track ticket status\n\n"
               "Select commands from the menu below:",
    "main_menu": "🔽 Please choose one of the options below:",
    "menu_new_ticket": "📝 New Ticket",
    "menu_my_tickets": "📋 My Tickets",
    "menu_track_ticket": "🔍 Track Ticket",
    "menu_help": "❓ Help",
    "menu_language": "🌐 Change Language",
    "menu_login": "🔐 Login",
    "menu_logout": "🚪 Logout",
    
    "help": "📖 Bot Usage Guide:\n\n"
            "Available commands:\n"
            "/start - Start the bot\n"
            "/newticket - Create new ticket\n"
            "/mytickets - View my tickets\n"
            "/track - Track a ticket\n"
            "/help - Show this help\n\n"
            "To create a new ticket, use /newticket command.",
    "login_prompt_username": "🔐 Please enter your username:",
    "login_prompt_password": "🔐 Please enter your password:",
    "login_failed": "❌ Login failed. Please try again.",
    "login_success": "✅ Logged in successfully!",
    "login_required": "⚠️ Please login first.",
    "logout_success": "✅ You have been logged out successfully.",
    "language_prompt": "🌐 Please choose your preferred language:",
    "language_set": "✅ Your language has been set to {language_name}.",
    "language_name_fa": "🇮🇷 Persian",
    "language_name_en": "🇺🇸 English",
    
    "new_ticket_start": "📝 Create New Ticket\n\n"
                        "Please enter the ticket title:",
    
    "new_ticket_title": "✅ Title received: {title}\n\n"
                        "Please enter the ticket description:",
    
    "new_ticket_description": "✅ Description received\n\n"
                             "Please select the branch:",
    
    "new_ticket_branch": "✅ Branch selected: {branch_name}\n\n"
                        "Please select the ticket category:",
    
    "branch_skip": "⏩ No branch",
    
    "new_ticket_category": "✅ Category selected: {category}\n\n"
                          "Creating ticket...",
    
    "ticket_created": "✅ Ticket created successfully!\n\n"
                      "📋 Ticket Number: {ticket_number}\n"
                      "📌 Title: {title}\n"
                      "📂 Category: {category}\n"
                      "📊 Status: {status}",
    
    "ticket_created_error": "❌ Error creating ticket\n\n"
                            "Please try again or contact support.",
    
    "description_too_short": "⚠️ Ticket description must be at least {min_length} characters.\n\n"
                             "Please enter a more detailed description:",
    
    "my_tickets_empty": "📭 You have no tickets.\n\n"
                        "Use /newticket to create a new ticket.",
    
    "my_tickets_list": "📋 Your Tickets:\n\n",
    
    "ticket_item": "🔹 Number: {ticket_number}\n"
                   "📌 Title: {title}\n"
                   "📊 Status: {status}\n"
                   "📂 Category: {category}\n"
                   "📅 Date: {created_at}\n"
                   "━━━━━━━━━━━━━━━━\n",
    
    "track_ticket_prompt": "🔍 Track Ticket\n\n"
                          "Please enter the ticket number (e.g., T-20241111-0001):",
    
    "track_ticket_not_found": "❌ Ticket not found.\n\n"
                              "Please enter a valid ticket number.",
    
    "track_ticket_details": "📋 Ticket Details:\n\n"
                            "🔹 Number: {ticket_number}\n"
                            "📌 Title: {title}\n"
                            "📝 Description: {description}\n"
                            "📂 Category: {category}\n"
                            "📊 Status: {status}\n"
                            "📅 Created: {created_at}\n"
                            "🔄 Updated: {updated_at}",
    
    "cancel": "❌ Operation cancelled.",
    "cancelled": "❌ Operation cancelled.",
    
    "error": "❌ An error occurred. Please try again.",
    
    "invalid_input": "⚠️ Invalid input. Please try again.",
    "attachments_prompt": "📎 You can send related files (images or documents).\n"
                          "Send \"done\" or use the button below when finished.",
    "attachments_skip_button": "⏩ Skip Attachments",
    "attachments_done": "✅ Ticket creation completed.",
    "attachments_text_hint": "ℹ️ To finish without files, send \"done\" or use /skip.",
    "attachment_saved": "✅ File {file_name} saved successfully.",
    "attachment_error": "❌ Failed to save the file. Please try again.",
    
    "category_internet": "🌐 Internet",
    "category_equipment": "💻 Equipment",
    "category_software": "📱 Software",
    "category_other": "📦 Other",
    
    "status_pending": "⏳ Pending",
    "status_in_progress": "🔄 In Progress",
    "status_resolved": "✅ Resolved",
    "status_closed": "🔒 Closed",
}


def get_message(key: str, language: Language = Language.FA) -> str:
    """
    Get localized message
    
    Args:
        key: Message key
        language: Language (FA or EN)
        
    Returns:
        Localized message string
    """
    messages = MESSAGES_EN if language == Language.EN else MESSAGES_FA
    return messages.get(key, f"[{key}]")


def get_category_name(category: str, language: Language = Language.FA) -> str:
    """Get localized category name"""
    key = f"category_{category.lower()}"
    return get_message(key, language)


def get_status_name(status: str, language: Language = Language.FA) -> str:
    """Get localized status name"""
    key = f"status_{status.lower()}"
    return get_message(key, language)

