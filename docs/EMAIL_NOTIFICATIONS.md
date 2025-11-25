# 📧 راهنمای کامل سیستم اطلاع‌رسانی ایمیل

## فهرست مطالب
1. [معرفی](#معرفی)
2. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
3. [تنظیمات SMTP](#تنظیمات-smtp)
4. [انواع ایمیل‌های ارسالی](#انواع-ایمیل‌های-ارسالی)
5. [یکپارچه‌سازی](#یکپارچه‌سازی)
6. [قالب‌های ایمیل](#قالب‌های-ایمیل)
7. [تست و عیب‌یابی](#تست-و-عیب‌یابی)
8. [بهترین روش‌ها](#بهترین-روش‌ها)

---

## معرفی

سیستم اطلاع‌رسانی ایمیل یک سیستم پیشرفته و حرفه‌ای برای ارسال اعلان‌های خودکار به کاربران از طریق ایمیل است. این سیستم به صورت کامل با سیستم تیکتینگ یکپارچه شده و از قالب‌های HTML زیبا و حرفه‌ای استفاده می‌کند.

### ویژگی‌های کلیدی:
- ✅ پشتیبانی از SMTP با TLS/SSL
- ✅ قالب‌های HTML زیبا و Responsive
- ✅ پشتیبانی از چندزبانه (فارسی و انگلیسی)
- ✅ ارسال ایمیل‌های خودکار برای رویدادهای مختلف
- ✅ پشتیبانی از فایل‌های پیوست
- ✅ مدیریت خطا و Retry خودکار
- ✅ Logging کامل برای عیب‌یابی

---

## نصب و راه‌اندازی

### مرحله 1: نصب وابستگی‌ها

#### روش 1: نصب مستقیم

```bash
pip install aiosmtplib==3.0.1 email-validator==2.1.0 jinja2==3.1.2
```

#### روش 2: نصب از requirements.txt (توصیه می‌شود)

```bash
pip install -r requirements.txt
```

این دستور تمام وابستگی‌های پروژه از جمله کتابخانه‌های ایمیل را نصب می‌کند.

**نکته:** اگر از محیط مجازی (virtual environment) استفاده می‌کنید، ابتدا آن را فعال کنید:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

---

### مرحله 2: اجرای Migration

برای اضافه کردن فیلد `email` به جدول `users` در دیتابیس، باید migration را اجرا کنید:

#### Windows:
```bash
.venv\Scripts\python.exe scripts\migrate_v17_add_email_to_users.py
```

#### Linux/Mac:
```bash
python scripts/migrate_v17_add_email_to_users.py
```

یا اگر از محیط مجازی استفاده می‌کنید:
```bash
python3 scripts/migrate_v17_add_email_to_users.py
```

**خروجی موفق:**
```
INFO:__main__:Migration v17 completed: Added email field to users table
```

**نکته:** اگر migration قبلاً اجرا شده باشد، پیام زیر نمایش داده می‌شود:
```
INFO:__main__:Migration v17 skipped: email field already exists
```

---

### مرحله 3: تنظیمات SMTP در فایل .env

#### 3.1. پیدا کردن فایل .env

فایل `.env` در ریشه پروژه قرار دارد. اگر وجود ندارد، آن را ایجاد کنید:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

#### 3.2. افزودن تنظیمات SMTP

فایل `.env` را با یک ویرایشگر متن باز کنید و تنظیمات زیر را اضافه کنید:

```env
# ============================================
# Email Configuration (تنظیمات ایمیل)
# ============================================

# فعال/غیرفعال کردن سرویس ایمیل
EMAIL_ENABLED=true

# آدرس سرور SMTP
EMAIL_SMTP_HOST=smtp.gmail.com

# پورت SMTP (معمولاً 587 برای TLS یا 465 برای SSL)
EMAIL_SMTP_PORT=587

# نام کاربری SMTP (معمولاً آدرس ایمیل شما)
EMAIL_SMTP_USER=your-email@gmail.com

# رمز عبور SMTP (برای Gmail: App Password)
EMAIL_SMTP_PASSWORD=your-app-password-here

# استفاده از TLS (برای پورت 587)
EMAIL_SMTP_USE_TLS=true

# استفاده از SSL (برای پورت 465)
EMAIL_SMTP_USE_SSL=false

# آدرس ایمیل فرستنده
EMAIL_FROM_ADDRESS=noreply@iranmehr.com

# نام فرستنده (نمایش داده می‌شود در inbox)
EMAIL_FROM_NAME=سیستم تیکتینگ ایرانمهر

# آدرس Reply-To (اختیاری)
EMAIL_REPLY_TO=support@iranmehr.com

# آدرس‌های BCC (اختیاری - با کاما جدا کنید)
EMAIL_BCC_ADDRESSES=admin@iranmehr.com,logs@iranmehr.com
```

#### 3.3. تنظیمات برای سرویس‌های مختلف

برای تنظیمات دقیق‌تر هر سرویس، به بخش [تنظیمات SMTP](#تنظیمات-smtp) مراجعه کنید.

**⚠️ نکته امنیتی مهم:**
- هرگز فایل `.env` را در Git commit نکنید
- فایل `.env` باید در `.gitignore` باشد
- در Production، از متغیرهای محیطی سیستم استفاده کنید

---

### مرحله 4: تنظیم ایمیل کاربران در دیتابیس

پس از اجرای migration، باید برای هر کاربر یک آدرس ایمیل تنظیم کنید. روش‌های مختلف:

#### روش 1: از طریق API (توصیه می‌شود)

##### 4.1. استفاده از API Update User

```bash
# مثال با curl
curl -X PATCH "http://localhost:8000/api/users/{user_id}" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

##### 4.2. استفاده از Frontend Admin Panel

1. وارد پنل مدیریت شوید
2. به بخش "کاربران" بروید
3. کاربر مورد نظر را انتخاب کنید
4. فیلد "ایمیل" را پر کنید
5. تغییرات را ذخیره کنید

#### روش 2: از طریق دیتابیس (برای کاربران متعدد)

##### 4.3. استفاده از SQLite (Development)

```bash
# باز کردن دیتابیس SQLite
sqlite3 ticketing.db
```

```sql
-- مشاهده کاربران
SELECT id, username, full_name, email FROM users;

-- به‌روزرسانی ایمیل یک کاربر
UPDATE users SET email = 'user@example.com' WHERE id = 1;

-- به‌روزرسانی ایمیل چند کاربر
UPDATE users SET email = 'user1@example.com' WHERE username = 'user1';
UPDATE users SET email = 'user2@example.com' WHERE username = 'user2';

-- بررسی تغییرات
SELECT id, username, email FROM users WHERE email IS NOT NULL;
```

##### 4.4. استفاده از PostgreSQL (Production)

```bash
# اتصال به دیتابیس PostgreSQL
psql -U postgres -d ticketing_db
```

```sql
-- مشاهده کاربران
SELECT id, username, full_name, email FROM users;

-- به‌روزرسانی ایمیل یک کاربر
UPDATE users SET email = 'user@example.com' WHERE id = 1;

-- به‌روزرسانی ایمیل چند کاربر با یک query
UPDATE users 
SET email = CASE 
    WHEN username = 'user1' THEN 'user1@example.com'
    WHEN username = 'user2' THEN 'user2@example.com'
    WHEN username = 'admin' THEN 'admin@example.com'
    ELSE email
END
WHERE username IN ('user1', 'user2', 'admin');

-- بررسی تغییرات
SELECT id, username, email FROM users WHERE email IS NOT NULL;
```

#### روش 3: استفاده از Script Python (برای به‌روزرسانی انبوه)

یک فایل Python ایجاد کنید (`scripts/update_user_emails.py`):

```python
"""
اسکریپت برای به‌روزرسانی ایمیل کاربران
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app.models import User

def update_user_emails():
    """به‌روزرسانی ایمیل کاربران"""
    db = SessionLocal()
    try:
        # لیست کاربران و ایمیل‌هایشان
        email_mapping = {
            'admin': 'admin@iranmehr.com',
            'user1': 'user1@iranmehr.com',
            'user2': 'user2@iranmehr.com',
            # ... سایر کاربران
        }
        
        for username, email in email_mapping.items():
            user = db.query(User).filter(User.username == username).first()
            if user:
                user.email = email
                print(f"✓ ایمیل {email} برای کاربر {username} تنظیم شد")
            else:
                print(f"✗ کاربر {username} یافت نشد")
        
        db.commit()
        print("\n✓ همه ایمیل‌ها با موفقیت به‌روزرسانی شدند")
        
    except Exception as e:
        db.rollback()
        print(f"✗ خطا: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_user_emails()
```

اجرای اسکریپت:
```bash
python scripts/update_user_emails.py
```

#### 4.5. بررسی تنظیمات

برای اطمینان از اینکه ایمیل‌ها به درستی تنظیم شده‌اند:

```sql
-- تعداد کاربران با ایمیل
SELECT COUNT(*) as users_with_email FROM users WHERE email IS NOT NULL;

-- لیست کاربران بدون ایمیل
SELECT id, username, full_name FROM users WHERE email IS NULL;

-- لیست کاربران با ایمیل
SELECT id, username, full_name, email FROM users WHERE email IS NOT NULL;
```

---

### مرحله 5: تست سیستم ایمیل

#### 5.1. بررسی تنظیمات

```python
from app.config import settings

print(f"Email Enabled: {settings.EMAIL_ENABLED}")
print(f"SMTP Host: {settings.EMAIL_SMTP_HOST}")
print(f"SMTP Port: {settings.EMAIL_SMTP_PORT}")
print(f"SMTP User: {settings.EMAIL_SMTP_USER}")
```

#### 5.2. تست اتصال SMTP

یک فایل Python برای تست ایجاد کنید (`test_email_connection.py`):

```python
"""
تست اتصال SMTP
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.email_service import email_service

async def test_email():
    """تست ارسال ایمیل"""
    result = await email_service.send_custom_email(
        to_addresses=["your-test-email@example.com"],
        subject="تست اتصال سیستم ایمیل",
        html_content="""
        <h1>تست اتصال</h1>
        <p>اگر این ایمیل را دریافت کردید، سیستم ایمیل به درستی کار می‌کند.</p>
        """
    )
    
    if result:
        print("✓ ایمیل با موفقیت ارسال شد")
    else:
        print("✗ خطا در ارسال ایمیل - لطفاً لاگ‌ها را بررسی کنید")

if __name__ == "__main__":
    asyncio.run(test_email())
```

اجرای تست:
```bash
python test_email_connection.py
```

#### 5.3. بررسی لاگ‌ها

```bash
# Windows
type logs\app.log | findstr /i email

# Linux/Mac
tail -f logs/app.log | grep -i email
```

---

### مرحله 6: فعال‌سازی کامل

پس از انجام مراحل بالا:

1. ✅ وابستگی‌ها نصب شده
2. ✅ Migration اجرا شده
3. ✅ تنظیمات SMTP در `.env` تنظیم شده
4. ✅ `EMAIL_ENABLED=true` تنظیم شده
5. ✅ ایمیل کاربران در دیتابیس تنظیم شده
6. ✅ تست اتصال موفق بوده

**سیستم آماده استفاده است!** 🎉

---

### نکات مهم

#### ✅ چک‌لیست قبل از استفاده:

- [ ] فایل `.env` ایجاد و تنظیمات SMTP اضافه شده
- [ ] `EMAIL_ENABLED=true` تنظیم شده
- [ ] Migration v17 اجرا شده
- [ ] ایمیل کاربران در دیتابیس تنظیم شده
- [ ] تست اتصال SMTP موفق بوده
- [ ] لاگ‌ها بررسی شده و خطایی وجود ندارد

#### ⚠️ مشکلات رایج:

1. **ایمیل‌ها ارسال نمی‌شوند:**
   - بررسی کنید `EMAIL_ENABLED=true` باشد
   - بررسی کنید تنظیمات SMTP صحیح باشد
   - بررسی کنید کاربران ایمیل داشته باشند
   - لاگ‌ها را بررسی کنید

2. **خطای Authentication:**
   - برای Gmail: از App Password استفاده کنید
   - رمز عبور را دوباره بررسی کنید

3. **ایمیل‌ها در Spam قرار می‌گیرند:**
   - از سرویس‌های معتبر استفاده کنید
   - SPF, DKIM, DMARC را تنظیم کنید

---

## تنظیمات SMTP

### تنظیمات Gmail

برای استفاده از Gmail:

1. **ایجاد App Password:**
   - به [Google Account Security](https://myaccount.google.com/security) بروید
   - "2-Step Verification" را فعال کنید
   - "App passwords" را انتخاب کنید
   - یک App Password برای "Mail" ایجاد کنید

2. **تنظیمات در `.env`:**
   ```env
   EMAIL_SMTP_HOST=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_SMTP_USER=your-email@gmail.com
   EMAIL_SMTP_PASSWORD=your-16-char-app-password
   EMAIL_SMTP_USE_TLS=true
   ```

### تنظیمات Outlook/Office 365

```env
EMAIL_SMTP_HOST=smtp.office365.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@outlook.com
EMAIL_SMTP_PASSWORD=your-password
EMAIL_SMTP_USE_TLS=true
```

### تنظیمات SendGrid

```env
EMAIL_SMTP_HOST=smtp.sendgrid.net
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=apikey
EMAIL_SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_SMTP_USE_TLS=true
```

### تنظیمات Mailgun

```env
EMAIL_SMTP_HOST=smtp.mailgun.org
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=postmaster@your-domain.mailgun.org
EMAIL_SMTP_PASSWORD=your-mailgun-password
EMAIL_SMTP_USE_TLS=true
```

---

## انواع ایمیل‌های ارسالی

### 1. ایمیل ایجاد تیکت (`ticket_created`)

**زمان ارسال:** وقتی کاربر یک تیکت جدید ایجاد می‌کند

**گیرندگان:**
- صاحب تیکت
- مدیران سیستم

**محتوا:**
- شماره تیکت
- عنوان تیکت
- دسته‌بندی
- لینک مشاهده تیکت

### 2. ایمیل تغییر وضعیت (`ticket_status_changed`)

**زمان ارسال:** وقتی وضعیت تیکت تغییر می‌کند

**گیرندگان:**
- صاحب تیکت
- مدیران سیستم

**محتوا:**
- شماره تیکت
- وضعیت قبلی و جدید
- لینک مشاهده تیکت

### 3. ایمیل تخصیص تیکت (`ticket_assigned`)

**زمان ارسال:** وقتی تیکت به یک کارشناس تخصیص داده می‌شود

**گیرندگان:**
- کارشناس تخصیص داده شده

**محتوا:**
- شماره تیکت
- عنوان تیکت
- نام شخص تخصیص‌دهنده
- لینک مشاهده تیکت

### 4. ایمیل افزودن کامنت (`comment_added`)

**زمان ارسال:** وقتی یک کامنت جدید به تیکت اضافه می‌شود (فقط کامنت‌های عمومی)

**گیرندگان:**
- صاحب تیکت (اگر خودش کامنت نگذاشته باشد)
- کارشناس مسئول (اگر خودش کامنت نگذاشته باشد)

**محتوا:**
- شماره تیکت
- نام فرستنده کامنت
- متن کامنت
- لینک مشاهده تیکت

### 5. ایمیل هشدار SLA (`sla_warning`)

**زمان ارسال:** وقتی تیکت به مهلت SLA نزدیک می‌شود

**گیرندگان:**
- کارشناس مسئول
- مدیران سیستم

**محتوا:**
- شماره تیکت
- نوع هشدار (زمان پاسخ یا زمان حل)
- زمان باقی‌مانده
- لینک مشاهده تیکت

### 6. ایمیل نقض SLA (`sla_breach`)

**زمان ارسال:** وقتی تیکت از مهلت SLA گذشته است

**گیرندگان:**
- کارشناس مسئول
- مدیران سیستم

**محتوا:**
- شماره تیکت
- نوع نقض (زمان پاسخ یا زمان حل)
- زمان تاخیر
- لینک مشاهده تیکت

---

## یکپارچه‌سازی

### استفاده در کد

```python
from app.services.email_service import email_service

# ارسال ایمیل ایجاد تیکت
await email_service.send_ticket_created_email(
    to_email="user@example.com",
    ticket_number="T-20240123-0001",
    ticket_title="مشکل در سیستم",
    ticket_category="نرم‌افزار",
    language=Language.FA
)

# ارسال ایمیل سفارشی
await email_service.send_custom_email(
    to_addresses=["user1@example.com", "user2@example.com"],
    subject="موضوع ایمیل",
    html_content="<h1>محتوای HTML</h1>",
    text_content="محتوای متنی",
    cc_addresses=["cc@example.com"],
    attachments=[
        {"path": "/path/to/file.pdf", "filename": "document.pdf"}
    ]
)
```

### یکپارچه‌سازی خودکار

سیستم به صورت خودکار در موارد زیر ایمیل ارسال می‌کند:

1. **ایجاد تیکت:** در `notify_ticket_created()`
2. **تغییر وضعیت:** در `notify_ticket_status_changed()`
3. **تخصیص تیکت:** در `notify_ticket_assigned()`
4. **افزودن کامنت:** در `create_comment()`
5. **هشدار SLA:** در `_send_response_warning_notification()` و `_send_resolution_warning_notification()`
6. **نقض SLA:** در `_send_response_breach_notification()` و `_send_resolution_breach_notification()`

---

## قالب‌های ایمیل

### ساختار قالب‌ها

قالب‌های ایمیل در پوشه `app/templates/email/` قرار دارند:

```
app/templates/email/
├── base_fa.html          # قالب پایه فارسی
├── base_en.html          # قالب پایه انگلیسی
├── ticket_created_fa.html
├── ticket_created_en.html
├── ticket_status_changed_fa.html
├── ticket_status_changed_en.html
├── ticket_assigned_fa.html
├── ticket_assigned_en.html
├── comment_added_fa.html
├── comment_added_en.html
├── sla_warning_fa.html
├── sla_warning_en.html
├── sla_breach_fa.html
└── sla_breach_en.html
```

### ویرایش قالب‌ها

قالب‌ها از Jinja2 استفاده می‌کنند. برای ویرایش:

```html
{% extends "base_fa.html" %}

{% block content %}
<h2>عنوان ایمیل</h2>
<p>سلام {{ user_name }}،</p>
<p>متن ایمیل...</p>
{% endblock %}
```

### متغیرهای در دسترس

- `ticket_number`: شماره تیکت
- `ticket_title`: عنوان تیکت
- `app_name`: نام برنامه
- `ticket_url`: لینک مشاهده تیکت
- `support_url`: لینک پشتیبانی
- سایر متغیرها بر اساس نوع ایمیل

---

## تست و عیب‌یابی

### فعال‌سازی Logging

در `app/config.py`:

```python
LOG_LEVEL = "DEBUG"
```

### تست اتصال SMTP

```python
from app.services.email_service import email_service

# تست ارسال ایمیل
result = await email_service.send_custom_email(
    to_addresses=["test@example.com"],
    subject="تست اتصال",
    html_content="<h1>این یک ایمیل تست است</h1>"
)

if result:
    print("ایمیل با موفقیت ارسال شد")
else:
    print("خطا در ارسال ایمیل")
```

### بررسی لاگ‌ها

```bash
tail -f logs/app.log | grep -i email
```

### مشکلات رایج

#### 1. خطای Authentication

```
Error: Authentication failed
```

**راه حل:**
- بررسی صحت نام کاربری و رمز عبور
- برای Gmail: استفاده از App Password به جای رمز عبور اصلی
- بررسی فعال بودن "Less secure app access" (برای برخی سرویس‌ها)

#### 2. خطای Connection Timeout

```
Error: Connection timeout
```

**راه حل:**
- بررسی صحت آدرس SMTP و پورت
- بررسی فایروال و شبکه
- استفاده از TLS به جای SSL

#### 3. ایمیل‌ها در Spam قرار می‌گیرند

**راه حل:**
- استفاده از SPF, DKIM, DMARC
- استفاده از سرویس‌های معتبر مانند SendGrid یا Mailgun
- اجتناب از استفاده از کلمات کلیدی spam

---

## بهترین روش‌ها

### 1. امنیت

- ✅ استفاده از App Password به جای رمز عبور اصلی
- ✅ ذخیره‌سازی رمز عبور در متغیرهای محیطی
- ✅ استفاده از TLS/SSL
- ✅ محدود کردن دسترسی به تنظیمات SMTP

### 2. عملکرد

- ✅ استفاده از Connection Pooling
- ✅ ارسال غیرهمزمان (Async)
- ✅ Retry خودکار برای خطاهای موقت
- ✅ Queue برای ایمیل‌های زیاد

### 3. قالب‌بندی

- ✅ استفاده از قالب‌های Responsive
- ✅ تست در کلاینت‌های مختلف ایمیل
- ✅ استفاده از Fallback برای متن ساده
- ✅ بهینه‌سازی تصاویر

### 4. مدیریت خطا

- ✅ Logging کامل
- ✅ مدیریت خطاهای موقت
- ✅ اطلاع‌رسانی به مدیران در صورت خطاهای مکرر
- ✅ ذخیره‌سازی ایمیل‌های ناموفق برای Retry

---

## پشتیبانی

برای سوالات و مشکلات:
- 📧 ایمیل: support@iranmehr.com
- 📚 مستندات: [docs/EMAIL_NOTIFICATIONS.md](EMAIL_NOTIFICATIONS.md)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**آخرین به‌روزرسانی:** 2025-01-23
**نسخه:** 1.0.0

