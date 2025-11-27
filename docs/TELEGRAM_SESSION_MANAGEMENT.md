# 📱 راهنمای Session Management در Telegram Bot

## معرفی

سیستم Session Management برای Telegram Bot به شما امکان مدیریت و کنترل sessions فعال کاربران را می‌دهد. این سیستم شامل timeout خودکار، ردیابی IP و آخرین فعالیت، و امکان مشاهده و مدیریت sessions است.

---

## ✨ ویژگی‌ها

### ✅ قابلیت‌های پیاده‌سازی شده:

1. **Session Timeout خودکار**
   - Sessions بعد از 30 دقیقه عدم فعالیت به صورت خودکار expire می‌شوند
   - Timeout در هر درخواست بررسی می‌شود
   - Background task برای cleanup expired sessions هر 10 دقیقه اجرا می‌شود

2. **مشاهده Sessions فعال**
   - دستور `/sessions` برای مشاهده تمام sessions فعال
   - نمایش اطلاعات هر session: تاریخ ایجاد، آخرین فعالیت، IP
   - نمایش session فعلی

3. **خروج از تمام Sessions**
   - دستور `/logout_all` برای خروج از تمام sessions
   - حذف session از دیتابیس و در-memory

4. **IP Tracking**
   - ثبت IP address برای هر session (به عنوان "Telegram" چون از طریق Telegram API است)
   - ثبت User Agent

5. **Activity Tracking**
   - به‌روزرسانی خودکار last_activity در هر درخواست
   - تمدید خودکار expires_at در هر فعالیت

---

## 🗄️ ساختار دیتابیس

### جدول `telegram_sessions`

```sql
CREATE TABLE telegram_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    telegram_user_id INTEGER NOT NULL,
    token VARCHAR(512) NOT NULL,
    ip_address VARCHAR(64),
    user_agent VARCHAR(255),
    last_activity DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Indexes:**
- `idx_telegram_sessions_user_id` - برای جستجوی سریع بر اساس user_id
- `idx_telegram_sessions_telegram_user_id` - برای جستجوی سریع بر اساس telegram_user_id
- `idx_telegram_sessions_last_activity` - برای مرتب‌سازی بر اساس آخرین فعالیت
- `idx_telegram_sessions_expires_at` - برای cleanup سریع expired sessions
- `idx_telegram_sessions_user_active` - برای جستجوی sessions فعال یک کاربر
- `idx_telegram_sessions_telegram_user` - برای جستجوی sessions فعال یک telegram user

---

## 🔧 استفاده

### دستورات موجود:

#### `/sessions`
مشاهده تمام sessions فعال کاربر

**مثال:**
```
📱 Sessions فعال (2):

🔹 Session 1 (فعلی)
🕐 ایجاد شده: 2025-01-26 10:30:00
⏰ آخرین فعالیت: 2025-01-26 11:15:00
🌐 IP: Telegram

🔹 Session 2
🕐 ایجاد شده: 2025-01-26 09:00:00
⏰ آخرین فعالیت: 2025-01-26 10:45:00
🌐 IP: Telegram
```

#### `/logout_all`
خروج از تمام sessions فعال

**مثال:**
```
✅ از 2 session خارج شدید.
```

---

## 🏗️ معماری

### فایل‌های مرتبط:

1. **`app/models/telegram_session.py`**
   - مدل SQLAlchemy برای TelegramSession
   - متد `is_expired()` برای بررسی انقضای session

2. **`app/services/telegram_session_service.py`**
   - Service layer برای مدیریت sessions
   - توابع: `create_session`, `update_session_activity`, `get_active_session`, `get_user_sessions`, `logout_session`, `logout_all_sessions`, `cleanup_expired_sessions`

3. **`app/telegram_bot/handlers/session_management.py`**
   - Handlers برای `/sessions` و `/logout_all`

4. **`app/telegram_bot/handlers/auth.py`**
   - به‌روزرسانی شده برای ثبت session در دیتابیس هنگام login
   - به‌روزرسانی شده برای حذف session از دیتابیس هنگام logout

5. **`app/telegram_bot/handlers/common.py`**
   - `require_token` به‌روزرسانی شده برای بررسی session timeout و به‌روزرسانی activity

6. **`app/tasks/telegram_session_tasks.py`**
   - Background task برای cleanup expired sessions

7. **`scripts/migrate_v21_create_telegram_sessions.py`**
   - Migration script برای ایجاد جدول

---

## 🔄 جریان کار

### Login Flow:
1. کاربر لاگین می‌کند
2. Token دریافت می‌شود
3. Session در دیتابیس ثبت می‌شود با:
   - `user_id` (backend user ID)
   - `telegram_user_id` (Telegram user ID)
   - `token` (JWT access token)
   - `ip_address` ("Telegram")
   - `user_agent` (Telegram Bot - username)
   - `expires_at` (30 دقیقه از حالا)

### Request Flow:
1. کاربر درخواستی ارسال می‌کند
2. `require_token` فراخوانی می‌شود
3. Session در دیتابیس بررسی می‌شود
4. اگر session expired باشد، کاربر باید دوباره لاگین کند
5. اگر session فعال باشد، `last_activity` و `expires_at` به‌روزرسانی می‌شود

### Logout Flow:
1. کاربر `/logout` یا `/logout_all` را اجرا می‌کند
2. Session در دیتابیس به `is_active = 0` تنظیم می‌شود
3. Session در-memory پاک می‌شود

### Cleanup Flow:
1. Background task هر 10 دقیقه اجرا می‌شود
2. تمام sessions با `expires_at < now` پیدا می‌شوند
3. `is_active = 0` تنظیم می‌شود

---

## ⚙️ تنظیمات

### Session Timeout:
```python
# در app/services/telegram_session_service.py
SESSION_TIMEOUT_MINUTES = 30  # 30 دقیقه عدم فعالیت
```

### Cleanup Interval:
```python
# در app/tasks/telegram_session_tasks.py
await asyncio.sleep(10 * 60)  # هر 10 دقیقه
```

---

## 🚀 راه‌اندازی

### 1. اجرای Migration:
```bash
python scripts/migrate_v21_create_telegram_sessions.py
```

### 2. راه‌اندازی Bot:
Background scheduler به صورت خودکار در `app/main.py` startup شروع می‌شود.

---

## 📝 نکات مهم

1. **IP Address:** در Telegram Bot API، IP address کاربر در دسترس نیست. بنابراین IP به عنوان "Telegram" ذخیره می‌شود.

2. **Timezone:** تمام timestamps با timezone-aware datetime ذخیره می‌شوند (UTC).

3. **Session Extension:** در هر فعالیت، `expires_at` به 30 دقیقه از زمان فعلی تمدید می‌شود.

4. **Cleanup:** Background task expired sessions را به صورت خودکار cleanup می‌کند.

5. **Backward Compatibility:** سیستم در-memory sessions برای backward compatibility حفظ شده است.

---

## 🧪 تست

### تست دستی:

1. **تست Session Timeout:**
   - لاگین کنید
   - 30 دقیقه صبر کنید (یا `expires_at` را در دیتابیس تغییر دهید)
   - یک دستور اجرا کنید
   - باید پیام "لطفاً ابتدا وارد سیستم شوید" دریافت کنید

2. **تست `/sessions`:**
   - لاگین کنید
   - `/sessions` را اجرا کنید
   - باید لیست sessions فعال را ببینید

3. **تست `/logout_all`:**
   - لاگین کنید
   - `/logout_all` را اجرا کنید
   - باید از تمام sessions خارج شوید

---

**تاریخ ایجاد:** 2025-01-26  
**نسخه:** 1.0

