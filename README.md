# سیستم تیکتینگ ایرانمهر / Iranmehr Ticketing System

سیستم تیکتینگ پیشرفته برای مدیریت درخواست‌ها و مشکلات پرسنل موسسه زبان ایرانمهر.

## ویژگی‌ها / Features

- ✅ ایجاد و پیگیری تیکت از طریق ربات تلگرام
- ✅ پنل وب مدیریتی برای ادمین‌ها
- ✅ سیستم مدیریت نقش‌ها
- ✅ پشتیبانی دو زبانه (فارسی/انگلیسی)
- ✅ پیوست فایل
- ✅ سیستم گزارش‌گیری

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

## مستندات / Documentation

- [Roadmap](./roadmap.md) - راهنمای کامل توسعه پروژه

## مجوز / License

این پروژه برای استفاده داخلی موسسه زبان ایرانمهر است.

