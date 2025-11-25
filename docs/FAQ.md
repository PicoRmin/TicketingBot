## پرسش‌های پرتکرار (FAQ)

این بخش به صورت دو زبانه تهیه شده است؛ در هر سؤال ابتدا نسخه فارسی، سپس ترجمه انگلیسی آمده است.

---

### 1. چگونه وارد پنل شوم؟ / How do I log in?
- **FA:** از آدرس `http://localhost:5173` یا دامنه سازمانی استفاده کنید، روی «🔐 ورود» کلیک کرده و نام کاربری/رمز خود را وارد کنید. اگر حساب ندارید، ادمین سیستم باید کاربر شما را بسازد.
- **EN:** Visit `http://localhost:5173` (or your corporate domain), click “🔐 Login”, and enter your credentials. If you do not have an account, contact the system administrator.

### 2. توکن من منقضی شده؛ چه کنم؟ / My token expired, what should I do?
- **FA:** دکمه خروج را بزنید، صفحه را تازه کنید و دوباره وارد شوید. در صورت تکرار، از بخش Troubleshooting چک‌لیست “رفع خطاهای جاری” را دنبال کنید.
- **EN:** Click “Logout”, refresh the page, and log in again. If the issue persists, follow the “Current error checklist” in `TROUBLESHOOTING.md`.

### 3. چرا از پنل وب نمی‌توانم به API وصل شوم؟ / Why can’t the web panel reach the API?
- **FA:** اول مطمئن شوید backend روی `http://127.0.0.1:8000` اجرا است. سپس مقدار `CORS_ORIGINS` را بررسی و با `curl -I` از وجود هدر `access-control-allow-origin` مطمئن شوید.
- **EN:** Ensure the backend is running on `http://127.0.0.1:8000`. Then check `CORS_ORIGINS` in `.env` and verify the `access-control-allow-origin` header via `curl -I`.

### 4. چطور تیکت جدید ثبت کنم؟ / How do I create a new ticket?
- **FA:** به `/user-portal` بروید، فرم “ثبت تیکت” را تکمیل کنید، فیلدهای سفارشی مرتبط را پر کنید و دکمه “ثبت” را بزنید. برای هر دسته‌بندی فیلدهای خاص نمایش داده می‌شود.
- **EN:** Navigate to `/user-portal`, fill out the “Create Ticket” form, complete the relevant custom fields, and click submit.

### 5. چرا نمی‌توانم تیکت‌های دیگران را ببینم؟ / Why can’t I see other users’ tickets?
- **FA:** سیاست سیستم این است که کاربران فقط تیکت‌های خود را ببینند. ادمین‌ها و نقش‌های تخصصی (مثل IT Specialist) می‌توانند همه تیکت‌ها را مشاهده یا مدیریت کنند.
- **EN:** Regular users are restricted to their own tickets by design. Admins and specialists can access all tickets depending on their role.

### 6. چگونه صادرات گزارش‌ها کار می‌کند؟ / How does report export work?
- **FA:** در داشبورد و سایر صفحات گزارش، آیکون “📥 CSV” یا “📄 PDF” را بزنید. این عملیات با توکن فعلی انجام می‌شود؛ اگر دانلود شروع نشد، ممکن است توکن منقضی شده باشد.
- **EN:** Use the “📥 CSV” or “📄 PDF” buttons on dashboards. Downloads rely on your active token; if nothing happens, your session might have expired.

### 7. چطور تلگرام‌بات را فعال کنم؟ / How do I enable the Telegram bot?
- **FA:** در `.env` مقدار `TELEGRAM_BOT_TOKEN` را تنظیم کنید، backend را ری‌استارت کنید و اسکریپت `python -m app.telegram_bot.run` را اجرا کنید. برای وب‌هوک، مقدار `TELEGRAM_WEBHOOK_URL` را تنظیم کنید.
- **EN:** Set `TELEGRAM_BOT_TOKEN` in `.env`, restart the backend, and run `python -m app.telegram_bot.run`. For webhook mode, configure `TELEGRAM_WEBHOOK_URL`.

### 8. بکاپ‌های سیستم کجا ذخیره می‌شود؟ / Where are backups stored?
- **FA:** اسکریپت‌های `scripts/backup.sh` و `backup.bat` در مسیر `backups/` خروجی می‌گیرند. سیاست نگهداری و زمان‌بندی در `docs/PRODUCTION_SETUP.md` توضیح داده شده است.
- **EN:** The backup scripts (`scripts/backup.sh`, `backup.bat`) store archives under `backups/`. Retention and schedule are documented in `docs/PRODUCTION_SETUP.md`.

### 9. برای به‌روزرسانی سیستم چه مراحلی لازم است؟ / What steps are required to update the system?
- **FA:** ابتدا از DB و فایل‌ها بکاپ بگیرید، سپس تست‌ها (`pytest`, `npm run build`) را اجرا کنید، مایگریشن‌ها را با `scripts/migrate_*` اعمال کنید و در نهایت سرویس‌ها را ری‌استارت کنید. چک‌لیست کامل در `docs/PRODUCTION_QUICK_START.md`.
- **EN:** Take database/file backups, run tests (`pytest`, `npm run build`), apply migrations (`scripts/migrate_*`), and restart services. See `docs/PRODUCTION_QUICK_START.md` for the checklist.

### 10. ساختار دسترسی و نقش‌ها چگونه است؟ / How does role-based access work?
- **FA:** نقش‌ها شامل `central_admin`, `admin`, `branch_admin`, `it_specialist`, `report_manager`, `user` هستند. ProtectedRoute در فرانت و Decoratorهای `require_admin`/`require_role` در بک‌اند تضمین می‌کنند هر صفحه/endpoint فقط برای نقش مجاز باز باشد.
- **EN:** Roles include `central_admin`, `admin`, `branch_admin`, `it_specialist`, `report_manager`, and `user`. ProtectedRoute (frontend) plus backend decorators ensure each route/endpoint is restricted to the allowed roles.

---

در صورت نیاز به افزودن سؤال جدید، کافی است همین ساختار (FA/EN) را تکرار کنید و لینک مربوطه را به README یا User Guide اضافه نمایید.

