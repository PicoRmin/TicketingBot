## Architecture Overview

این سند خلاصه‌ای از معماری ایرانمهر تیکتینگ را ارائه می‌کند تا تیم فنی بتواند قبل از استقرار، شناخت دقیقی از اجزای سیستم داشته باشد.

---

### 1. لایه‌ها (High-Level Diagram)

```
[User/Agent]
    │
    ├─ Web Admin (React + Vite, i18next, REST client)
    ├─ User Portal (React Shared Components)
    ├─ Telegram Bot (Python)
    │
    ▼
[FastAPI Backend]
    ├─ API Routers (auth, tickets, sla, reports, custom_fields, ...)
    ├─ Services Layer (business logic: ticket_service, sla_service, ...)
    ├─ Models (SQLAlchemy ORM)
    ├─ Tasks/Schedulers (automation_tasks, sla_tasks)
    └─ Middlewares (i18n, CORS)
    │
    ▼
[Database]
    ├─ PostgreSQL (Production)
    └─ SQLite (Development / Tests)
    │
    ▼
[External Services]
    ├─ SMTP / Email Provider
    ├─ Telegram Bot API
    ├─ File Storage (local `storage/uploads`)
```

---

### 2. اجزای اصلی

1. **Frontend (web_admin)**
   - زبان‌ها: React 18, TypeScript, Vite
   - i18n: `i18next` با ذخیره‌سازی انتخاب زبان در `localStorage`
   - ProtectedRoute برای کنترل نقش‌ها
   - سرویس API مشترک (`src/services/api.ts`) با Error Bus و Global Toast
   - صفحات کلیدی: Dashboard، Tickets، SLA، Custom Fields، User Portal

2. **Backend (FastAPI)**
   - ساختار ماژولار تحت `app/api/*` و `app/services/*`
   - تمامی Routerها زیر `/api/` قرار گرفته‌اند (auth، tickets، reports، sla و …)
   - استفاده از SQLAlchemy + Alembic-style migrations (در `scripts/migrate_*`)
   - Schedulerهای مستقل برای Automation و SLA (`app/tasks`)
   - i18n middleware برای تعیین زبان پاسخ‌ها (FA/EN)

3. **Database**
   - مدل‌های اصلی: `User`, `Ticket`, `Comment`, `SLARule`, `SLALog`, `CustomField`, `TimeLog`, `Branch`, `Department`, `AutomationRule`
   - وابستگی‌ها:
     - هر Ticket به User، Branch، Department متصل است.
     - `TicketCustomFieldValue` نگهدارنده داده‌های پویا است.
     - `SLALog` ارتباطی مستقیم با Ticket و SLARule دارد تا تاریخچه SLA ذخیره شود.
   - تولید دیتای اولیه: اسکریپت‌های `scripts/create_admin.py`, `create_default_departments.py`, …

4. **Telegram Bot**
   - ماژول `app/telegram_bot` با امکان Login و ایجاد تیکت
   - قابل اجرا در دو حالت Polling و Webhook

5. **External Integrations**
   - Email (SMTP) با سرویس `notification_service` و قالب‌های HTML
   - File uploads روی دیسک (`storage/uploads`)؛ در Production توصیه به استفاده از Volume یا Object Storage

---

### 3. استقرار و Infra

- **Backend**: FastAPI + Uvicorn/Gunicorn پشت Nginx، با systemd یا NSSM
- **Frontend**: Build استاتیک Vite، سرو شده توسط Nginx یا CDN
- **Database**: PostgreSQL (با بکاپ‌گیری خودکار و مانیتورینگ)
- **Monitoring**: Health Check `/health`, لاگ‌ها در `logs/app.log`, اسکریپت `check_production.sh`
- **Backup**: اسکریپت‌های `scripts/backup.sh` و `.bat` برای DB و فایل‌ها

---

### 4. Flowهای کلیدی (Sequence خلاصه)

#### الف) ایجاد تیکت کاربر
1. کاربر در User Portal فرم را پر می‌کند.
2. Frontend با `POST /api/tickets` تماس می‌گیرد.
3. `ticket_service.create_ticket` رکورد را می‌سازد، فیلدهای سفارشی را ذخیره می‌کند.
4. Automation و SLA ruleها بررسی می‌شوند؛ در صورت نیاز، لاگ‌های اولیه SLA ثبت می‌شود.
5. اعلان ایمیل/تلگرام به کارشناسان یا کاربر ارسال می‌گردد.

#### ب) مانیتورینگ SLA
1. Scheduler (`sla_tasks.start_sla_scheduler`) دوره‌ای SLAها را بررسی می‌کند.
2. اگر تیکتی خارج از هدف است، `SLALog` به‌روزرسانی شده و Escalation فعال می‌شود.
3. Dashboard با Endpointهای `/api/reports/sla-*` وضعیت را نمایش می‌دهد.

#### ج) جریان ربات تلگرام
1. کاربر دستور `/login` را ارسال می‌کند؛ Bot به `/api/auth/login` متصل می‌شود و توکن دریافت می‌کند.
2. کاربر لیست شعب/دپارتمان‌ها را می‌بیند (`/api/branches`, `/api/departments`).
3. با ارسال جزئیات، `/api/tickets` صدا زده می‌شود؛ شماره تیکت برگشت داده می‌شود.

---

### 5. ERD متنی (فهرست روابط مهم)

- `User` 1─∞ `Ticket`
- `Ticket` ∞─∞ `CustomField` (از طریق `TicketCustomFieldValue`)
- `Ticket` 1─∞ `Comment`, `TimeLog`, `SLALog`
- `Branch` 1─∞ `Ticket` و `User`
- `Department` 1─∞ `Ticket` و `User`
- `SLARule` 1─∞ `SLALog`
- `AutomationRule` 1─∞ `Ticket` (از طریق اجرای قوانین)

برای جزئیات schema می‌توان از فایل‌های `app/models/*.py` یا اسکریپت‌های مهاجرت کمک گرفت.

---

### 6. پیشنهادهای بعدی

1. خروجی گرفتن از این سند به صورت Diagram رسمی (Draw.io / PlantUML)
2. نگاشت CI/CD Pipeline و زیرساخت Monitoring در همین سند
3. پیوست کردن ERD گرافیکی و Sequence Diagram کامل برای Flowهای SLA و Automation

---

**آخرین به‌روزرسانی:** 2025-11-24

