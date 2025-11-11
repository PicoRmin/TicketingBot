## راهنمای اجرا (Windows 11) - سیستم تیکتینگ ایرانمهر

این سند به صورت کامل و مرحله‌به‌مرحله توضیح می‌دهد چطور پروژه را روی ویندوز 11 اجرا کنید: بک‌اند (FastAPI)، ربات تلگرام، و پنل وب (React).

### ۰) پیش‌نیازها
- Python 3.10+ (پیشنهادی 3.10 یا 3.11). بررسی نسخه:
  - در PowerShell: `python --version`
- Node.js 18+ و npm. بررسی نسخه:
  - `node -v` و `npm -v`
- Git (اختیاری اما پیشنهاد می‌شود)

اگر نصب نیست:
- Python: از `https://www.python.org/downloads/` دانلود کنید و گزینه "Add Python to PATH" را تیک بزنید.
- Node.js: نسخه LTS را از `https://nodejs.org/` دانلود کنید.


### ۱) دریافت/آماده‌سازی پوشه پروژه
اگر پوشه پروژه را دارید، مرحله کلون را رد کنید.

```powershell
cd C:\PersonalProject
git clone <repository-url> imehrTicketing
cd .\imehrTicketing
```


### ۲) ساخت و فعال‌سازی محیط مجازی (Backend)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
اگر PowerShell اجرای اسکریپت را مسدود کرد، یک‌بار (نیاز به ادمین) اجرا کنید:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
سپس دوباره اکتیو کردن venv را اجرا کنید.


### ۳) نصب وابستگی‌های پایتون
```powershell
pip install -r requirements.txt
```
پکیج‌های کلیدی: FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-jose, passlib, python-telegram-bot, openpyxl (برای خروجی Excel).


### ۴) تنظیم فایل محیطی (.env)
1) ساخت فایل `.env` از نمونه:
```powershell
copy .\env.example .\.env
```
2) فایل `.env` را باز و مقادیر را تنظیم کنید. کلیدهای رایج:
- SECRET_KEY=... (می‌توانید با `python .\scripts\generate_secret_key.py` بسازید)
- ACCESS_TOKEN_EXPIRE_MINUTES=1440
- DATABASE_URL=sqlite:///./ticketing.db
- UPLOAD_DIR=storage\uploads
- TELEGRAM_BOT_TOKEN=<توکن_ربات> (اگر خالی بماند، ربات همراه با FastAPI اجرا نمی‌شود)
- API_BASE_URL=http://127.0.0.1:8000

مطمئن شوید پوشه `storage\uploads` وجود دارد (در مخزن هست). در صورت نبود:
```powershell
mkdir .\storage\uploads -Force
```


### ۵) مقداردهی اولیه دیتابیس و ساخت ادمین (اختیاری)
اسکریپت‌ها را اجرا کنید:
```powershell
python .\scripts\init_db.py
python .\scripts\create_admin.py
```
طبق پیام‌ها پیش بروید یا در صورت نیاز اسکریپت‌ها را ویرایش کنید.


### ۶) اجرای بک‌اند (FastAPI)
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- مستندات API: `http://127.0.0.1:8000/docs`
- بررسی سلامت: فراخوانی یکی از اندپوینت‌ها (مثلاً `/api/auth/me` بعد از لاگین).

این ترمینال را باز نگه دارید. برای کارهای دیگر، یک PowerShell جدید باز کنید.


### ۷) اجرای ربات تلگرام (اختیاری)
نیاز به `TELEGRAM_BOT_TOKEN` معتبر در `.env` و فعال بودن بک‌اند روی پورت 8000 دارد.

در یک PowerShell جدید (مسیر ریشه پروژه):
```powershell
.\venv\Scripts\Activate.ps1
python -m app.telegram_bot.bot
```
ربات شروع به polling می‌کند. در تلگرام با ربات گفتگو کنید.


### ۸) اجرای پنل وب (React + Vite)
در یک PowerShell جدید:
```powershell
cd C:\PersonalProject\imehrTicketing\web_admin
npm install
npm run dev
```
Vite یک آدرس محلی نمایش می‌دهد، معمولاً `http://127.0.0.1:5173`.

اگر لازم است آدرس API را تنظیم کنید، فایل `web_admin/src/services/api.ts` را چک کنید تا به `http://127.0.0.1:8000` اشاره کند.


### ۹) جریان تست سریع
1) از طریق API یا پنل وب لاگین کنید.
2) چند تیکت ایجاد کنید (از UI یا ربات تلگرام).
3) در صفحه تیکت‌ها از فیلترها استفاده کنید (وضعیت/دسته؛ فیلتر شعبه فقط برای ادمین نمایش داده می‌شود).
4) داشبورد را باز کنید:
   - نمای کلی، نمودار بر اساس وضعیت/تاریخ/شعب
   - نمایش میانگین زمان پاسخ‌دهی (ساعت)
   - لینک‌های خروجی CSV و Excel


### ۱۰) گزارش‌ها و خروجی‌ها
- CSV:
  - `GET http://127.0.0.1:8000/api/reports/export?kind=overview`
  - حالت‌ها: `overview|by-status|by-date|by-branch`
- Excel (XLSX):
  - `GET http://127.0.0.1:8000/api/reports/export.xlsx?kind=overview`
  - پشتیبانی از بازه تاریخ:
    - `GET .../export.xlsx?kind=by-date&date_from=2025-01-01&date_to=2025-12-31`


### ۱۱) نکات محیط ویندوز
- اگر پورت 8000 مشغول بود، پورت را عوض کنید: `--port 8080` و در صورت نیاز آدرس API فرانت‌اند را نیز به‌روزرسانی کنید.
- اگر اجرای `Activate.ps1` مسدود بود، مرحله ۲ (Set-ExecutionPolicy) را انجام دهید.
- اگر خروجی Excel خطای 500 با پیام “openpyxl is not installed” داد، مطمئن شوید `pip install -r requirements.txt` موفق بوده است.
- اگر آپلود فایل خطا داد، وجود مسیر `UPLOAD_DIR` و دسترسی نوشتن کاربر ویندوز را بررسی کنید.


### ۱۲) عیب‌یابی
- مشکل: “ModuleNotFoundError”
  - مطمئن شوید venv فعال است و `pip install -r requirements.txt` را اجرا کرده‌اید.
- مشکل: خطای CORS در مرورگر
  - تنظیمات CORS بک‌اند را چک کنید (در `app/main.py` یا تنظیمات). در توسعه، اجازه `http://127.0.0.1:5173` را بدهید.
- مشکل: ربات به API متصل نمی‌شود
  - مقدار `TELEGRAM_API_BASE_URL` را بررسی کنید و از دسترسی بک‌اند اطمینان حاصل کنید.
- مشکل: ناسازگاری/ساختار دیتابیس
  - دوباره `python .\scripts\init_db.py` را اجرا کنید. برای Production از Alembic استفاده کنید.


### ۱۳) اسکریپت‌های مفید
- ساخت کلید محرمانه:
  ```powershell
  python .\scripts\generate_secret_key.py
  ```
- مقداردهی دیتابیس:
  ```powershell
  python .\scripts\init_db.py
  ```
- تست‌های ساده API (نمونه‌ها در `scripts\` مثل `test_auth.py`, `test_tickets.py`):
  ```powershell
  python .\scripts\test_auth.py
  python .\scripts\test_tickets.py
  ```


### ۱۴) نکات Production (مروری)
- به‌جای SQLite از Postgres استفاده کنید.
- `DATABASE_URL` و `SECRET_KEY`، HTTPS و Reverse Proxy (Nginx) را تنظیم کنید.
- بک‌اند را با Service/NSSM اجرا و قوانین فایروال ویندوز را پیکربندی کنید.


### ۱۵) خلاصه مراحل
1) ساخت venv، نصب وابستگی‌ها، تنظیم `.env`.
2) مقداردهی دیتابیس و ساخت ادمین.
3) اجرای بک‌اند روی پورت 8000.
4) (اختیاری) اجرای ربات تلگرام.
5) اجرای پنل وب با `npm run dev`.
6) استفاده از داشبورد و لیست تیکت‌ها؛ خروجی CSV/XLSX از گزارش‌ها.


