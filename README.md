# سیستم تیکتینگ ایرانمهر / Iranmehr Ticketing System

سیستم تیکتینگ پیشرفته برای مدیریت درخواست‌ها و مشکلات پرسنل موسسه زبان ایرانمهر.

## ویژگی‌ها / Features

### ✨ ویژگی‌های اصلی:
- ✅ **Telegram Bot پیشرفته** - سیستم تیکتینگ کامل از طریق تلگرام:
  - ✅ ایجاد و پیگیری تیکت
  - ✅ مشاهده جزئیات کامل تیکت (تاریخچه، کامنت‌ها، فایل‌ها)
  - ✅ پاسخ و کامنت روی تیکت (با امکان attach فایل)
  - ✅ فیلتر و جستجوی پیشرفته تیکت‌ها
  - ✅ مدیریت اولویت تیکت
  - ✅ تخصیص تیکت (با نمایش workload)
  - ✅ عملیات دسته‌ای تیکت‌ها (Bulk Actions)
  - ✅ Session Management و Timeout
  - ✅ پشتیبانی دو زبانه (فارسی/انگلیسی)
- ✅ پنل وب مدیریتی پیشرفته برای ادمین‌ها
- ✅ پورتال کاربران برای کاربران عادی
- ✅ سیستم مدیریت نقش‌ها (6 نقش)
- ✅ پشتیبانی دو زبانه کامل (فارسی/انگلیسی)
- ✅ پیوست فایل با اعتبارسنجی
- ✅ سیستم گزارش‌گیری پیشرفته با Export (CSV, Excel, PDF)
- ✅ سیستم SLA (Service Level Agreement) کامل
- ✅ Automation Rules (تخصیص خودکار، بستن خودکار، اعلان خودکار)
- ✅ فیلدهای سفارشی (Custom Fields) - 11 نوع فیلد
- ✅ Time Tracker (زمان‌سنج کار)
- ✅ Bulk Actions (عملیات گروهی)
- ✅ Quick Actions (عملیات سریع)
- ✅ Headless UI Header & Navigation (جستجوی سراسری، انتخاب زبان و منوی پروفایل دسترس‌پذیر)
- ✅ **ثبت‌نام چندمرحله‌ای با GSAP + OTP** — فرم چهاربخشی با Progress Tracker، ارسال OTP و Refactor کامل State Machine
- ✅ **Dashboard KPI انیمیشن‌دار** — کارت‌های KPI با GSAP Stagger، Counter Animation، Pulse هشدار و React Query Data Source
- ✅ Email Notifications (اعلان‌رسانی ایمیل پیشرفته)
- ✅ Telegram Notifications (اعلان‌رسانی تلگرام)
- ✅ Dashboard پیشرفته با نمودارهای جذاب
- ✅ مدیریت کامل شعب و دپارتمان‌ها
- ✅ زیرساخت شعب
- ✅ تست‌های کامل (Unit Tests) - 70+ تست
- ✅ تست‌های یکپارچه‌سازی (Integration Tests) - 60+ تست
- ✅ تست‌های End-to-End (E2E) - 2 سناریو جامع
- ✅ تست‌های امنیتی (Security Tests) - احراز هویت، مجوز، اعتبارسنجی ورودی
- ✅ تست‌های کارایی (Performance Tests) - اسکریپت Load/Stress اختصاصی
- ✅ کل تست‌ها: 185+ تست
- ✅ راهنمای کامل Production Setup
- ✅ اسکریپت‌های استقرار و Backup

## پیش‌نیازها / Prerequisites

- Python 3.10+
- pip
- Git

## نصب و راه‌اندازی / Installation

### 1. کلون کردن پروژه
```bash
git clone <repository-url>
cd imehrTicketing
```

### 2. ایجاد Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. نصب Dependencies
```bash
pip install -r requirements.txt
```

### 4. پیکربندی Environment Variables
```bash
copy .env.example .env
# سپس فایل .env را ویرایش کنید
```

### 5. راه‌اندازی Database
```bash
# ایجاد جداول
python scripts/init_db.py

# ایجاد کاربر ادمین
python scripts/create_admin.py

# تست مدل‌ها (اختیاری)
python scripts/test_models.py
```

### 6. اجرای Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Documentation در آدرس زیر در دسترس است:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ساختار پروژه / Project Structure

```
imehrTicketing/
├── app/
│   ├── main.py          # FastAPI Application
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API routes
│   ├── core/            # Core utilities
│   ├── services/        # Business logic
│   └── telegram_bot/    # Telegram bot
├── web_admin/           # Web admin panel
├── scripts/             # Utility scripts
└── tests/               # Tests
```

## استقرار Production / Production Deployment

برای استقرار در محیط Production:

```bash
# راه‌اندازی خودکار
python scripts/setup_production.py

# بررسی وضعیت
./scripts/check_production.sh  # Linux
# یا
scripts\check_production.bat  # Windows
```

برای راهنمای کامل، به [راهنمای Production Setup](./docs/PRODUCTION_SETUP.md) مراجعه کنید.

## مستندات / Documentation

### 📚 مستندات کاربری و راهنماها:
- **[راهنمای کامل نقش‌ها](./docs/ROLES_GUIDE.md)** - راهنمای کامل تمام نقش‌ها، دسترسی‌ها و تب‌های سیستم
- **[راهنمای کاربران تلگرام](./docs/TELEGRAM_USER_GUIDE.md)** - راهنمای کامل استفاده از ربات تلگرام
- **[راهنمای دیپلوی اوبونتو 24.04](./docs/DEPLOYMENT_UBUNTU_24.md)** - راهنمای قدم به قدم دیپلوی روی سرور اوبونتو با دامنه corlink.ir
- [User Guide](./docs/USER_GUIDE.md) - راهنمای کاربران نهایی (پورتال وب)
- [Admin Guide](./docs/ADMIN_GUIDE.md) - راهنمای مدیران و کارشناسان (پنل مدیریتی)

### 📚 مستندات فنی:
- [Roadmap](./roadmap.md) - راهنمای کامل توسعه پروژه
- [Backend Backlog](./docs/BACKEND_BACKLOG.md) - بک‌لاگ کامل توسعه Backend
- [Custom Fields Guide](./docs/CUSTOM_FIELDS.md) - راهنمای فیلدهای سفارشی
- [Lint Refactoring Report](./docs/LINT_REFACTORING.md) - گزارش بازنویسی برای Green Lint
- [Email Notifications Guide](./docs/EMAIL_NOTIFICATIONS.md) - راهنمای اعلان‌رسانی ایمیل
- [SLA Management Guide](./docs/SLA_MANAGEMENT.md) - راهنمای مدیریت SLA
- [Testing Guide](./docs/TESTING.md) - راهنمای کامل تست‌ها
- [Performance Tests Guide](./docs/PERFORMANCE_TESTS.md) - تست‌های Load/Stress
- [Integration Tests Guide](./docs/INTEGRATION_TESTS.md) - راهنمای تست‌های یکپارچه‌سازی
- [End-to-End Tests Guide](./docs/END_TO_END_TESTS.md) - راهنمای تست‌های سرتاسری
- [Production Setup Guide](./docs/PRODUCTION_SETUP.md) - راهنمای کامل استقرار Production (عمومی)
- [Monitoring Guide](./docs/MONITORING.md) - راهنمای Monitoring و Logging
- [Architecture Overview](./docs/ARCHITECTURE_OVERVIEW.md) - معماری کلان و روابط دیتابیس
- [Backend Backlog](./docs/BACKEND_BACKLOG.md) - وضعیت اپیک‌ها و برنامه توسعه Backend

### 📋 راهنماهای نصب و راه‌اندازی:
- [Quick Start](./QUICK_START.md) - راهنمای سریع
- [Setup Guide](./SETUP.md) - راهنمای کامل نصب
- [Telegram Bot Setup](./TELEGRAM_BOT_SETUP.md) - راهنمای راه‌اندازی ربات تلگرام

### 📊 مستندات پروژه:
- [Project Complete Features](./docs/PROJECT_COMPLETE_FEATURES.md) - فهرست کامل ویژگی‌ها
- [Remaining Work](./REMAINING_WORK.md) - کارهای باقی‌مانده
- [FAQ](./docs/FAQ.md) - پرسش‌های پرتکرار کاربران و کارشناسان
- [Future Enhancements](./docs/FUTURE_ENHANCEMENTS.md) - مسیر توسعه نسخه‌های بعدی

## مجوز / License

این پروژه برای استفاده داخلی موسسه زبان ایرانمهر است.

