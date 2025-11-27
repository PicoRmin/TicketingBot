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
    "session_expired": "⚠️ Session شما منقضی شده است. لطفاً دوباره وارد شوید.",
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
                            "{priority_line}"
                            "{assigned_line}"
                            "📅 تاریخ ایجاد: {created_at}\n"
                            "🔄 آخرین به‌روزرسانی: {updated_at}",
    
    "cancel": "❌ عملیات لغو شد.",
    "cancelled": "❌ عملیات لغو شد.",
    
    "error": "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
    "error_occurred": "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
    
    "invalid_input": "⚠️ ورودی نامعتبر است. لطفاً دوباره تلاش کنید.",
    "attachments_prompt": "📎 می‌توانید فایل‌های مرتبط با تیکت را ارسال کنید (تصاویر یا اسناد).\n"
                          "برای پایان، گزینه «تمام» را بفرستید یا دکمه زیر را بزنید.",
    "attachments_skip_button": "⏩ بدون فایل",
    "attachments_finish_button": "✅ پایان آپلود",
    "attachments_done": "✅ فرآیند ایجاد تیکت به پایان رسید.",
    "attachments_text_hint": "ℹ️ اگر می‌خواهید بدون فایل ادامه دهید، «تمام» را ارسال کنید یا از دستور /skip استفاده کنید.",
    "attachment_saved": "✅ فایل {file_name} با موفقیت ذخیره شد.",
    "attachment_error": "❌ خطا در ذخیره فایل. لطفاً دوباره تلاش کنید.",
    "file_validation_error": "⚠️ خطا در اعتبارسنجی فایل:\n{error}\n\nلطفاً فایل دیگری ارسال کنید.",
    
    "category_internet": "🌐 اینترنت",
    "category_equipment": "💻 تجهیزات",
    "category_software": "📱 نرم‌افزار",
    "category_other": "📦 سایر",
    
    "status_pending": "⏳ در انتظار",
    "status_in_progress": "🔄 در حال انجام",
    "status_resolved": "✅ حل شده",
    "status_closed": "🔒 بسته شده",
    
    "menu_change_status": "🔄 تغییر وضعیت تیکت",
    "change_status_prompt": "🔄 تغییر وضعیت تیکت\n\n"
                            "لطفاً شماره تیکت را وارد کنید (مثال: T-20241111-0001):",
    "change_status_not_allowed": "❌ شما مجاز به تغییر وضعیت تیکت نیستید.\n\n"
                                 "فقط مدیران ارشد و کارشناسان IT می‌توانند وضعیت تیکت را تغییر دهند.",
    "change_status_ticket_not_found": "❌ تیکت یافت نشد.\n\n"
                                       "لطفاً شماره تیکت را صحیح وارد کنید.",
    "change_status_select": "✅ تیکت یافت شد:\n\n"
                            "🔹 شماره: {ticket_number}\n"
                            "📊 وضعیت فعلی: {current_status}\n\n"
                            "لطفاً وضعیت جدید را انتخاب کنید:",
    "change_status_success": "✅ وضعیت تیکت با موفقیت تغییر یافت!\n\n"
                             "🔹 شماره تیکت: {ticket_number}\n"
                             "📊 وضعیت جدید: {new_status}",
    "change_status_error": "❌ خطا در تغییر وضعیت تیکت.\n\n"
                           "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
    
    "priority_critical": "بحرانی",
    "priority_high": "بالا",
    "priority_medium": "متوسط",
    "priority_low": "پایین",
    
    # Ticket detail messages
    "ticket_detail_prompt": "📋 مشاهده جزئیات تیکت\n\n"
                            "لطفاً شماره تیکت را وارد کنید (مثال: T-20241111-0001):",
    "ticket_detail_not_found": "❌ تیکت یافت نشد.\n\n"
                               "لطفاً شماره تیکت را صحیح وارد کنید.",
    "ticket_detail_header": "📋 جزئیات تیکت:\n\n"
                            "🔹 شماره: {ticket_number}\n"
                            "📌 عنوان: {title}\n"
                            "📝 توضیحات: {description}\n"
                            "📂 دسته‌بندی: {category}\n"
                            "📊 وضعیت: {status}\n"
                            "{priority_line}"
                            "{assigned_line}"
                            "📅 تاریخ ایجاد: {created_at}\n"
                            "🔄 آخرین به‌روزرسانی: {updated_at}\n\n"
                            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "ticket_detail_actions": "🔽 عملیات:",
    "ticket_detail_reply": "💬 پاسخ به تیکت",
    "ticket_detail_comments": "💬 مشاهده کامنت‌ها",
    "ticket_detail_history": "📜 تاریخچه تیکت",
    "ticket_detail_attachments": "📎 فایل‌های پیوست",
    "ticket_detail_priority": "⚡ تغییر اولویت",
    "ticket_detail_assign": "👤 تخصیص تیکت",
    
    # Reply/Comment messages
    "reply_prompt": "💬 پاسخ به تیکت\n\n"
                    "لطفاً شماره تیکت را وارد کنید:",
    "reply_comment_prompt": "✅ تیکت یافت شد: {ticket_number}\n\n"
                            "لطفاً پیام خود را وارد کنید:",
    "reply_success": "✅ پیام شما با موفقیت ارسال شد!",
    "reply_error": "❌ خطا در ارسال پیام.\n\n"
                   "لطفاً دوباره تلاش کنید.",
    "reply_attachment_prompt": "📎 می‌توانید فایل مرتبط را ارسال کنید (اختیاری):\n\n"
                               "برای پایان، «تمام» را بفرستید.",
    
    # Comments messages
    "comments_header": "💬 کامنت‌های تیکت {ticket_number}:\n\n",
    "comments_empty": "📭 هیچ کامنتی برای این تیکت وجود ندارد.",
    "comment_item": "👤 {author}\n"
                    "📅 {created_at}\n"
                    "💬 {comment}\n"
                    "{internal_tag}\n"
                    "━━━━━━━━━━━━━━━━\n",
    "comment_internal": "🔒 (یادداشت داخلی)",
    
    # History messages
    "history_header": "📜 تاریخچه تیکت {ticket_number}:\n\n",
    "history_empty": "📭 هیچ تاریخچه‌ای برای این تیکت وجود ندارد.",
    "history_item": "📅 {created_at}\n"
                    "👤 {changed_by}\n"
                    "📊 وضعیت: {status}\n"
                    "💬 {comment}\n"
                    "━━━━━━━━━━━━━━━━\n",
    
    # Attachments messages
    "attachments_header": "📎 فایل‌های پیوست تیکت {ticket_number}:\n\n",
    "attachments_empty": "📭 هیچ فایلی برای این تیکت وجود ندارد.",
    "attachment_item": "📎 {file_name}\n"
                       "📊 حجم: {file_size}\n"
                       "📅 تاریخ: {created_at}\n"
                       "━━━━━━━━━━━━━━━━\n",
    
    # Priority messages
    "priority_prompt": "⚡ تغییر اولویت تیکت\n\n"
                       "لطفاً شماره تیکت را وارد کنید:",
    "priority_select": "✅ تیکت یافت شد: {ticket_number}\n\n"
                        "وضعیت فعلی: {current_priority}\n\n"
                        "لطفاً اولویت جدید را انتخاب کنید:",
    "priority_success": "✅ اولویت تیکت با موفقیت تغییر یافت!\n\n"
                        "🔹 شماره تیکت: {ticket_number}\n"
                        "⚡ اولویت جدید: {new_priority}",
    "priority_error": "❌ خطا در تغییر اولویت.\n\n"
                      "لطفاً دوباره تلاش کنید.",
    "priority_not_allowed": "❌ شما مجاز به تغییر اولویت تیکت نیستید.\n\n"
                            "فقط مدیران می‌توانند اولویت تیکت را تغییر دهند.",
    
    # Assign messages
    "assign_prompt": "👤 تخصیص تیکت\n\n"
                     "لطفاً شماره تیکت را وارد کنید:",
    "assign_select": "✅ تیکت یافت شد: {ticket_number}\n\n"
                      "کارشناس فعلی: {current_assignee}\n\n"
                      "لطفاً کارشناس جدید را انتخاب کنید:",
    "assign_success": "✅ تیکت با موفقیت تخصیص داده شد!\n\n"
                      "🔹 شماره تیکت: {ticket_number}\n"
                      "👤 کارشناس: {assignee_name}",
    "assign_error": "❌ خطا در تخصیص تیکت.\n\n"
                    "لطفاً دوباره تلاش کنید.",
    "assign_not_allowed": "❌ شما مجاز به تخصیص تیکت نیستید.\n\n"
                          "فقط مدیران و کارشناسان IT می‌توانند تیکت را تخصیص دهند.",
    "assign_no_users": "❌ هیچ کارشناسی یافت نشد.",
    "assign_search_too_short": "⚠️ متن جستجو باید حداقل 2 کاراکتر باشد.\n\n"
                                "لطفاً نام کارشناس را وارد کنید:",
    "assign_search_no_results": "❌ هیچ کارشناسی با نام «{search}» یافت نشد.\n\n"
                                "لطفاً نام دیگری جستجو کنید:",
    "assign_search_results": "🔍 نتایج جستجو برای «{search}»:\n\n"
                             "تعداد: {count} کارشناس",
    
    # Search messages
    "search_prompt": "🔍 جستجو و فیلتر تیکت‌ها\n\n"
                     "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
    "search_filter_status": "📊 فیلتر بر اساس وضعیت",
    "search_filter_priority": "⚡ فیلتر بر اساس اولویت",
    "search_filter_category": "📂 فیلتر بر اساس دسته‌بندی",
    "search_filter_date": "📅 فیلتر بر اساس تاریخ",
    "search_text": "🔤 جستجوی متنی",
    "search_results": "🔍 نتایج جستجو:\n\n",
    "search_empty": "📭 هیچ تیکتی یافت نشد.",
    "search_text_prompt": "🔤 جستجوی متنی\n\n"
                          "لطفاً متن مورد نظر را وارد کنید (جستجو در عنوان و توضیحات):",
    
    # Bulk action messages
    "bulk_prompt": "📦 عملیات دسته‌ای\n\n"
                   "لطفاً نوع عملیات را انتخاب کنید:",
    "bulk_action_prompt": "⚡ عملیات دسته‌ای تیکت‌ها\n\n"
                          "لطفاً نوع عملیات را انتخاب کنید:",
    "bulk_action_status": "📊 تغییر وضعیت",
    "bulk_action_assign": "👤 تخصیص",
    "bulk_action_unassign": "❌ حذف تخصیص",
    "bulk_action_delete": "🗑️ حذف",
    "bulk_status_select": "📊 تغییر وضعیت دسته‌ای\n\n"
                         "لطفاً وضعیت جدید را انتخاب کنید:",
    "bulk_assign_select": "👤 تخصیص دسته‌ای\n\n"
                         "لطفاً کارشناس را انتخاب کنید:",
    "bulk_ticket_selection": "📋 انتخاب تیکت‌ها\n\n"
                            "عملیات: {action}\n"
                            "تعداد کل تیکت‌ها: {total}\n"
                            "تعداد انتخاب شده: {selected}\n\n"
                            "لطفاً تیکت‌ها را انتخاب کنید:",
    "bulk_confirm_button": "✅ تایید و اجرا",
    "bulk_no_tickets": "❌ هیچ تیکتی برای انتخاب یافت نشد.",
    "bulk_no_tickets_selected": "⚠️ لطفاً حداقل یک تیکت را انتخاب کنید.",
    "bulk_select_tickets": "✅ عملیات: {action}\n\n"
                            "لطفاً شماره تیکت‌ها را وارد کنید (با کاما جدا کنید):",
    "bulk_confirm": "✅ تایید",
    "bulk_cancel": "❌ لغو",
    "bulk_cancelled": "❌ عملیات دسته‌ای لغو شد.",
    
    # SLA messages
    "sla_prompt": "⏰ مشاهده SLA تیکت\n\n"
                  "لطفاً شماره تیکت را وارد کنید (مثال: T-20241111-0001):",
    "sla_header": "⏰ اطلاعات SLA تیکت {ticket_number}:\n",
    "sla_not_found": "❌ برای تیکت {ticket_number} لاگ SLA یافت نشد.\n\n"
                     "این تیکت ممکن است قبل از فعال‌سازی SLA ایجاد شده باشد.",
    
    # SLA Alerts messages
    "alerts_prompt": "⚠️ هشدارهای SLA\n\n"
                     "لطفاً نوع فیلتر را انتخاب کنید:",
    "alerts_header": "⚠️ هشدارهای SLA\n\n"
                     "فیلتر: {filter}\n"
                     "تعداد کل: {count} هشدار\n"
                     "نمایش: {showing} هشدار\n\n",
    "alerts_filter_all": "📋 همه",
    "alerts_filter_warning": "🟡 هشدارها",
    "alerts_filter_breach": "🔴 نقض‌ها",
    "alerts_no_alerts": "✅ هیچ هشداری با فیلتر «{filter}» یافت نشد.",
    "alerts_not_allowed": "❌ شما مجاز به مشاهده هشدارهای SLA نیستید.\n\n"
                          "فقط مدیران و کارشناسان IT می‌توانند هشدارها را مشاهده کنند.",
    
    # SLA Report messages
    "sla_report_prompt": "📊 گزارش SLA\n\n"
                         "لطفاً نوع گزارش را انتخاب کنید:",
    "sla_report_type_compliance": "📈 گزارش رعایت SLA",
    "sla_report_type_by_priority": "📋 گزارش بر اساس اولویت",
    "sla_report_compliance_header": "📊 گزارش رعایت SLA\n",
    "sla_report_priority_header": "📋 گزارش SLA بر اساس اولویت\n",
    "sla_report_not_allowed": "❌ شما مجاز به مشاهده گزارش SLA نیستید.\n\n"
                              "فقط مدیران و کارشناسان IT می‌توانند گزارش‌ها را مشاهده کنند.",
    "sla_report_error": "❌ خطا در دریافت گزارش SLA.\n\n"
                        "لطفاً دوباره تلاش کنید.",
    "sla_report_no_data": "⚠️ هیچ داده‌ای برای نمایش گزارش یافت نشد.",
    "bulk_success": "✅ عملیات دسته‌ای با موفقیت انجام شد!\n\n"
                    "تعداد تیکت‌های پردازش شده: {count}\n"
                    "عملیات: {action}",
    "bulk_partial_success": "⚠️ عملیات دسته‌ای با موفقیت نسبی انجام شد!\n\n"
                            "✅ موفق: {success} تیکت\n"
                            "❌ ناموفق: {failed} تیکت\n"
                            "عملیات: {action}",
    "bulk_error": "❌ خطا در انجام عملیات دسته‌ای.\n\n"
                   "لطفاً دوباره تلاش کنید.",
    "bulk_not_allowed": "❌ شما مجاز به انجام عملیات دسته‌ای نیستید.\n\n"
                        "فقط مدیران می‌توانند عملیات دسته‌ای انجام دهند.",
    
    # Comment/Reply additional messages
    "comment_too_short": "⚠️ پیام شما باید حداقل {min_length} کاراکتر باشد.\n\n"
                          "لطفاً پیام کامل‌تری وارد کنید:",
    "comment_internal_yes": "🔒 یادداشت داخلی",
    "comment_internal_no": "🌐 یادداشت عمومی",
    "comment_skip_internal": "⏩ بدون انتخاب",
    
    # Search and filter additional messages
    "search_filter_status_prompt": "📊 فیلتر بر اساس وضعیت\n\n"
                                   "لطفاً وضعیت مورد نظر را انتخاب کنید:",
    "search_filter_priority_prompt": "⚡ فیلتر بر اساس اولویت\n\n"
                                     "لطفاً اولویت مورد نظر را انتخاب کنید:",
    "search_filter_category_prompt": "📂 فیلتر بر اساس دسته‌بندی\n\n"
                                     "لطفاً دسته‌بندی مورد نظر را انتخاب کنید:",
    "search_filter_date_prompt": "📅 فیلتر بر اساس تاریخ\n\n"
                                 "لطفاً بازه زمانی مورد نظر را انتخاب کنید:",
    "search_filter_status_selected": "✅ فیلتر وضعیت انتخاب شد: {status}",
    "search_filter_priority_selected": "✅ فیلتر اولویت انتخاب شد: {priority}",
    "search_filter_category_selected": "✅ فیلتر دسته‌بندی انتخاب شد: {category}",
    "search_filter_date_selected": "✅ فیلتر تاریخ انتخاب شد: {date}",
    "search_filters_reset": "✅ فیلترها پاک شدند.\n\n"
                            "لطفاً فیلتر جدید انتخاب کنید:",
    "search_execute": "🔍 اجرای جستجو",
    "search_reset": "🔄 پاک کردن فیلترها",
    "search_text_too_short": "⚠️ متن جستجو باید حداقل 2 کاراکتر باشد.\n\n"
                             "لطفاً متن کامل‌تری وارد کنید:",
    "search_date_today": "📅 امروز",
    "search_date_week": "📅 هفته گذشته",
    "search_date_month": "📅 ماه گذشته",
    "search_date_all": "📅 همه تاریخ‌ها",
    
    # Priority management additional messages
    "priority_no_change": "ℹ️ اولویت تیکت {ticket_number} قبلاً {priority} است.\n\n"
                          "تغییری اعمال نشد.",
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
    "session_expired": "⚠️ Your session has expired. Please log in again.",
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
                            "{priority_line}"
                            "{assigned_line}"
                            "📅 Created: {created_at}\n"
                            "🔄 Updated: {updated_at}",
    
    "cancel": "❌ Operation cancelled.",
    "cancelled": "❌ Operation cancelled.",
    
    "error": "❌ An error occurred. Please try again.",
    "error_occurred": "❌ An error occurred. Please try again.",
    
    "invalid_input": "⚠️ Invalid input. Please try again.",
    "attachments_prompt": "📎 You can send related files (images or documents).\n"
                          "Send \"done\" or use the button below when finished.",
    "attachments_skip_button": "⏩ Skip Attachments",
    "attachments_finish_button": "✅ Finish Upload",
    "attachments_done": "✅ Ticket creation completed.",
    "attachments_text_hint": "ℹ️ To finish without files, send \"done\" or use /skip.",
    "attachment_saved": "✅ File {file_name} saved successfully.",
    "attachment_error": "❌ Failed to save the file. Please try again.",
    "file_validation_error": "⚠️ File validation error:\n{error}\n\nPlease send another file.",
    
    "category_internet": "🌐 Internet",
    "category_equipment": "💻 Equipment",
    "category_software": "📱 Software",
    "category_other": "📦 Other",
    
    "status_pending": "⏳ Pending",
    "status_in_progress": "🔄 In Progress",
    "status_resolved": "✅ Resolved",
    "status_closed": "🔒 Closed",
    
    "menu_change_status": "🔄 Change Ticket Status",
    "change_status_prompt": "🔄 Change Ticket Status\n\n"
                            "Please enter the ticket number (e.g., T-20241111-0001):",
    "change_status_not_allowed": "❌ You are not allowed to change ticket status.\n\n"
                                 "Only senior managers and IT specialists can change ticket status.",
    "change_status_ticket_not_found": "❌ Ticket not found.\n\n"
                                       "Please enter a valid ticket number.",
    "change_status_select": "✅ Ticket found:\n\n"
                            "🔹 Number: {ticket_number}\n"
                            "📊 Current status: {current_status}\n\n"
                            "Please select the new status:",
    "change_status_success": "✅ Ticket status changed successfully!\n\n"
                             "🔹 Ticket Number: {ticket_number}\n"
                             "📊 New Status: {new_status}",
    "change_status_error": "❌ Error changing ticket status.\n\n"
                           "Please try again or contact support.",
    
    "priority_critical": "Critical",
    "priority_high": "High",
    "priority_medium": "Medium",
    "priority_low": "Low",
    
    # Ticket detail messages
    "ticket_detail_prompt": "📋 View Ticket Details\n\n"
                            "Please enter the ticket number (e.g., T-20241111-0001):",
    "ticket_detail_not_found": "❌ Ticket not found.\n\n"
                               "Please enter a valid ticket number.",
    "ticket_detail_header": "📋 Ticket Details:\n\n"
                            "🔹 Number: {ticket_number}\n"
                            "📌 Title: {title}\n"
                            "📝 Description: {description}\n"
                            "📂 Category: {category}\n"
                            "📊 Status: {status}\n"
                            "{priority_line}"
                            "{assigned_line}"
                            "📅 Created: {created_at}\n"
                            "🔄 Updated: {updated_at}\n\n"
                            "Please select one of the options below:",
    "ticket_detail_actions": "🔽 Actions:",
    "ticket_detail_reply": "💬 Reply to Ticket",
    "ticket_detail_comments": "💬 View Comments",
    "ticket_detail_history": "📜 Ticket History",
    "ticket_detail_attachments": "📎 Attachments",
    "ticket_detail_priority": "⚡ Change Priority",
    "ticket_detail_assign": "👤 Assign Ticket",
    
    # Reply/Comment messages
    "reply_prompt": "💬 Reply to Ticket\n\n"
                    "Please enter the ticket number:",
    "reply_comment_prompt": "✅ Ticket found: {ticket_number}\n\n"
                            "Please enter your message:",
    "reply_success": "✅ Your message has been sent successfully!",
    "reply_error": "❌ Error sending message.\n\n"
                   "Please try again.",
    "reply_attachment_prompt": "📎 You can send a related file (optional):\n\n"
                               "Send \"done\" to finish.",
    
    # Comments messages
    "comments_header": "💬 Comments for Ticket {ticket_number}:\n\n",
    "comments_empty": "📭 No comments for this ticket.",
    "comment_item": "👤 {author}\n"
                    "📅 {created_at}\n"
                    "💬 {comment}\n"
                    "{internal_tag}\n"
                    "━━━━━━━━━━━━━━━━\n",
    "comment_internal": "🔒 (Internal Note)",
    
    # History messages
    "history_header": "📜 History for Ticket {ticket_number}:\n\n",
    "history_empty": "📭 No history for this ticket.",
    "history_item": "📅 {created_at}\n"
                    "👤 {changed_by}\n"
                    "📊 Status: {status}\n"
                    "💬 {comment}\n"
                    "━━━━━━━━━━━━━━━━\n",
    
    # Attachments messages
    "attachments_header": "📎 Attachments for Ticket {ticket_number}:\n\n",
    "attachments_empty": "📭 No attachments for this ticket.",
    "attachment_item": "📎 {file_name}\n"
                       "📊 Size: {file_size}\n"
                       "📅 Date: {created_at}\n"
                       "━━━━━━━━━━━━━━━━\n",
    
    # Priority messages
    "priority_prompt": "⚡ Change Ticket Priority\n\n"
                       "Please enter the ticket number:",
    "priority_select": "✅ Ticket found: {ticket_number}\n\n"
                        "Current priority: {current_priority}\n\n"
                        "Please select the new priority:",
    "priority_success": "✅ Ticket priority changed successfully!\n\n"
                        "🔹 Ticket Number: {ticket_number}\n"
                        "⚡ New Priority: {new_priority}",
    "priority_error": "❌ Error changing priority.\n\n"
                      "Please try again.",
    "priority_not_allowed": "❌ You are not allowed to change ticket priority.\n\n"
                            "Only managers can change ticket priority.",
    
    # Assign messages
    "assign_prompt": "👤 Assign Ticket\n\n"
                     "Please enter the ticket number:",
    "assign_select": "✅ Ticket found: {ticket_number}\n\n"
                      "Current assignee: {current_assignee}\n\n"
                      "Please select the new assignee:",
    "assign_success": "✅ Ticket assigned successfully!\n\n"
                      "🔹 Ticket Number: {ticket_number}\n"
                      "👤 Assignee: {assignee_name}",
    "assign_error": "❌ Error assigning ticket.\n\n"
                    "Please try again.",
    "assign_not_allowed": "❌ You are not allowed to assign tickets.\n\n"
                          "Only managers and IT specialists can assign tickets.",
    "assign_no_users": "❌ No specialists found.",
    "assign_search_too_short": "⚠️ Search text must be at least 2 characters.\n\n"
                                "Please enter the agent name:",
    "assign_search_no_results": "❌ No agents found with name «{search}».\n\n"
                                "Please search with another name:",
    "assign_search_results": "🔍 Search results for «{search}»:\n\n"
                             "Count: {count} agents",
    
    # Search messages
    "search_prompt": "🔍 Search and Filter Tickets\n\n"
                     "Please select one of the options below:",
    "search_filter_status": "📊 Filter by Status",
    "search_filter_priority": "⚡ Filter by Priority",
    "search_filter_category": "📂 Filter by Category",
    "search_filter_date": "📅 Filter by Date",
    "search_text": "🔤 Text Search",
    "search_results": "🔍 Search Results:\n\n",
    "search_empty": "📭 No tickets found.",
    "search_text_prompt": "🔤 Text Search\n\n"
                          "Please enter the text to search (searches in title and description):",
    
    # Bulk action messages
    "bulk_prompt": "📦 Bulk Actions\n\n"
                   "Please select the action type:",
    "bulk_select_tickets": "✅ Action: {action}\n\n"
                            "Please enter ticket numbers (separated by commas):",
    "bulk_confirm": "✅ Confirm",
    "bulk_cancel": "❌ Cancel",
    "bulk_action_prompt": "⚡ Bulk Ticket Actions\n\n"
                          "Please select the action type:",
    "bulk_action_status": "📊 Change Status",
    "bulk_action_assign": "👤 Assign",
    "bulk_action_unassign": "❌ Unassign",
    "bulk_action_delete": "🗑️ Delete",
    "bulk_status_select": "📊 Bulk Status Change\n\n"
                          "Please select the new status:",
    "bulk_assign_select": "👤 Bulk Assign\n\n"
                          "Please select the agent:",
    "bulk_ticket_selection": "📋 Select Tickets\n\n"
                            "Action: {action}\n"
                            "Total tickets: {total}\n"
                            "Selected: {selected}\n\n"
                            "Please select tickets:",
    "bulk_confirm_button": "✅ Confirm & Execute",
    "bulk_no_tickets": "❌ No tickets found for selection.",
    "bulk_no_tickets_selected": "⚠️ Please select at least one ticket.",
    "bulk_success": "✅ Bulk action completed successfully!\n\n"
                    "Processed tickets: {count}\n"
                    "Action: {action}",
    "bulk_partial_success": "⚠️ Bulk action completed with partial success!\n\n"
                            "✅ Success: {success} tickets\n"
                            "❌ Failed: {failed} tickets\n"
                            "Action: {action}",
    "bulk_error": "❌ Error performing bulk action.\n\n"
                  "Please try again.",
    "bulk_not_allowed": "❌ You are not allowed to perform bulk actions.\n\n"
                        "Only managers can perform bulk actions.",
    "bulk_cancelled": "❌ Bulk action cancelled.",
    
    # SLA messages
    "sla_prompt": "⏰ View Ticket SLA\n\n"
                  "Please enter the ticket number (e.g., T-20241111-0001):",
    "sla_header": "⏰ SLA Information for Ticket {ticket_number}:\n",
    "sla_not_found": "❌ No SLA log found for ticket {ticket_number}.\n\n"
                     "This ticket may have been created before SLA was enabled.",
    
    # SLA Alerts messages
    "alerts_prompt": "⚠️ SLA Alerts\n\n"
                     "Please select the filter type:",
    "alerts_header": "⚠️ SLA Alerts\n\n"
                     "Filter: {filter}\n"
                     "Total: {count} alerts\n"
                     "Showing: {showing} alerts\n\n",
    "alerts_filter_all": "📋 All",
    "alerts_filter_warning": "🟡 Warnings",
    "alerts_filter_breach": "🔴 Breaches",
    "alerts_no_alerts": "✅ No alerts found with filter «{filter}».",
    "alerts_not_allowed": "❌ You are not allowed to view SLA alerts.\n\n"
                          "Only managers and IT specialists can view alerts.",
    
    # SLA Report messages
    "sla_report_prompt": "📊 SLA Report\n\n"
                         "Please select the report type:",
    "sla_report_type_compliance": "📈 SLA Compliance Report",
    "sla_report_type_by_priority": "📋 Report by Priority",
    "sla_report_compliance_header": "📊 SLA Compliance Report\n",
    "sla_report_priority_header": "📋 SLA Report by Priority\n",
    "sla_report_not_allowed": "❌ You are not allowed to view SLA reports.\n\n"
                              "Only managers and IT specialists can view reports.",
    "sla_report_error": "❌ Error retrieving SLA report.\n\n"
                        "Please try again.",
    "sla_report_no_data": "⚠️ No data found to display the report.",
    
    # Comment/Reply additional messages
    "comment_too_short": "⚠️ Your message must be at least {min_length} characters.\n\n"
                          "Please enter a more complete message:",
    "comment_internal_yes": "🔒 Internal Note",
    "comment_internal_no": "🌐 Public Comment",
    "comment_skip_internal": "⏩ Skip Selection",
    
    # Search and filter additional messages
    "search_filter_status_prompt": "📊 Filter by Status\n\n"
                                  "Please select the status:",
    "search_filter_priority_prompt": "⚡ Filter by Priority\n\n"
                                     "Please select the priority:",
    "search_filter_category_prompt": "📂 Filter by Category\n\n"
                                     "Please select the category:",
    "search_filter_date_prompt": "📅 Filter by Date\n\n"
                                 "Please select the date range:",
    "search_filter_status_selected": "✅ Status filter selected: {status}",
    "search_filter_priority_selected": "✅ Priority filter selected: {priority}",
    "search_filter_category_selected": "✅ Category filter selected: {category}",
    "search_filter_date_selected": "✅ Date filter selected: {date}",
    "search_filters_reset": "✅ Filters cleared.\n\n"
                            "Please select a new filter:",
    "search_execute": "🔍 Execute Search",
    "search_reset": "🔄 Clear Filters",
    "search_text_too_short": "⚠️ Search text must be at least 2 characters.\n\n"
                             "Please enter a more complete text:",
    "search_date_today": "📅 Today",
    "search_date_week": "📅 Last Week",
    "search_date_month": "📅 Last Month",
    "search_date_all": "📅 All Dates",
    
    # Priority management additional messages
    "priority_no_change": "ℹ️ Ticket {ticket_number} priority is already {priority}.\n\n"
                          "No changes were made.",
}


def get_message(key: str, language: Language = Language.FA, default: str = None) -> str:
    """
    Get localized message
    
    Args:
        key: Message key
        language: Language (FA or EN)
        default: Default value if key not found
        
    Returns:
        Localized message string
    """
    messages = MESSAGES_EN if language == Language.EN else MESSAGES_FA
    result = messages.get(key)
    if result is None:
        return default if default is not None else f"[{key}]"
    return result


def get_category_name(category: str, language: Language = Language.FA) -> str:
    """Get localized category name"""
    key = f"category_{category.lower()}"
    return get_message(key, language)


def get_status_name(status: str, language: Language = Language.FA) -> str:
    """Get localized status name"""
    key = f"status_{status.lower()}"
    return get_message(key, language)

