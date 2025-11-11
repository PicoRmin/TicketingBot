# راهنمای نصب و راه‌اندازی / Setup Guide

## فاز ۱: راه‌اندازی پایه - تکمیل شده ✅

### مراحل نصب

#### ۱. ایجاد Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### ۲. نصب Dependencies
```bash
pip install -r requirements.txt
```

#### ۳. پیکربندی Environment Variables
```bash
# کپی کردن فایل نمونه
copy env.example .env
```

**سپس فایل `.env` را ویرایش کنید:**

##### الف) تولید SECRET_KEY
برای تولید یک کلید امنیتی تصادفی، از اسکریپت استفاده کنید:
```bash
python scripts/generate_secret_key.py
```
این اسکریپت یک کلید امنیتی تصادفی تولید می‌کند. آن را کپی کرده و در فایل `.env` در قسمت `SECRET_KEY` قرار دهید.

**یا به صورت دستی:**
در فایل `.env` مقدار `SECRET_KEY` را با یک رشته تصادفی قوی جایگزین کنید (حداقل 32 کاراکتر).

##### ب) دریافت TELEGRAM_BOT_TOKEN
برای دریافت توکن ربات تلگرام:
1. در تلگرام به `@BotFather` بروید
2. دستور `/newbot` را ارسال کنید
3. نام و username ربات را انتخاب کنید
4. توکن دریافتی را در فایل `.env` در قسمت `TELEGRAM_BOT_TOKEN` قرار دهید

📖 **راهنمای کامل**: فایل `TELEGRAM_BOT_SETUP.md` را مطالعه کنید.

**نکته**: برای شروع می‌توانید `TELEGRAM_BOT_TOKEN` را خالی بگذارید و بعداً تنظیم کنید.

#### ۴. تست اجرای Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

سپس در مرورگر به آدرس‌های زیر بروید:
- API Root: http://localhost:8000
- Health Check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### ساختار پروژه ایجاد شده

```
imehrTicketing/
├── app/
│   ├── __init__.py
│   ├── main.py              ✅ FastAPI Application
│   ├── config.py            ✅ Configuration
│   ├── database.py          ✅ Database setup
│   ├── models/              ✅ Ready for models
│   ├── schemas/             ✅ Ready for schemas
│   ├── api/                 ✅ Ready for API routes
│   ├── core/                ✅ Ready for utilities
│   ├── services/            ✅ Ready for business logic
│   ├── telegram_bot/        ✅ Ready for bot
│   └── i18n/                ✅ Ready for translations
├── scripts/                 ✅ Utility scripts
├── web_admin/               ✅ Web admin panel
├── storage/                 ✅ File storage
├── logs/                    ✅ Log files
├── requirements.txt        ✅ Dependencies
├── requirements-dev.txt     ✅ Dev dependencies
├── .gitignore              ✅ Git ignore
├── README.md                ✅ Documentation
└── env.example              ✅ Environment template
```

### بررسی صحت نصب

پس از نصب dependencies، می‌توانید با دستور زیر تست کنید:

```bash
python -c "from app.main import app; print('✅ Application loaded successfully!')"
```

### مراحل بعدی

پس از اطمینان از کارکرد صحیح فاز ۱، می‌توانید به فاز ۲ بروید:
- **فاز ۲**: ایجاد مدل‌های داده (User, Ticket)

### نکات مهم

1. **SECRET_KEY**: حتماً یک کلید امنیتی قوی برای Production استفاده کنید
2. **Database**: در حال حاضر از SQLite استفاده می‌کنیم که برای توسعه مناسب است
3. **Logs**: فایل‌های لاگ در پوشه `logs/` ذخیره می‌شوند

### مشکلات رایج

**مشکل**: Import errors در IDE
**راه‌حل**: مطمئن شوید که Virtual Environment فعال است و IDE شما آن را شناسایی کرده است.

**مشکل**: Port 8000 در حال استفاده است
**راه‌حل**: می‌توانید در فایل `.env` پورت دیگری تنظیم کنید یا از `--port` در uvicorn استفاده کنید.

