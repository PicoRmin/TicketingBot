# راهنمای فاز ۹: سیستم گزارش‌گیری / Phase 9: Reporting System

## ✅ کارهای انجام شده (MVP)
- ایجاد سرویس گزارش‌ها: `app/services/report_service.py`
  - `tickets_by_status` — تعداد تیکت‌ها بر اساس وضعیت
  - `tickets_by_date` — تعداد تیکت‌ها به تفکیک تاریخ ایجاد (Day)
  - `tickets_overview` — آمار کلی (total + by-status)
- ایجاد API گزارش‌ها: `app/api/reports.py`
  - `GET /api/reports/overview`
  - `GET /api/reports/by-status`
  - `GET /api/reports/by-date?date_from&date_to`
  - `GET /api/reports/by-branch` — (Not Implemented) به دلیل نبود `branch_id` در Ticket
  - `GET /api/reports/response-time` — (Not Implemented) به دلیل نبود `resolved_at/closed_at`
- اضافه شدن Router به برنامه: `app/main.py`

## ℹ️ محدودیت‌ها
- مدل `Ticket` فعلی فاقد `branch_id` و `resolved_at/closed_at` است، به همین دلیل:
  - گزارش بر اساس شعبه و گزارش زمان پاسخ‌دهی در این نسخه پیاده‌سازی نشده‌اند و 501 باز می‌گردانند.
  - در صورت نیاز، باید فیلدها به مدل اضافه و داده‌ها تولید/به‌روزرسانی شوند.

## 🧪 تست سریع
```bash
uvicorn app.main:app --reload

# Overview
curl -s http://localhost:8000/api/reports/overview | jq

# By status
curl -s http://localhost:8000/api/reports/by-status | jq

# By date (مثال بازه)
curl -s "http://localhost:8000/api/reports/by-date?date_from=2025-01-01&date_to=2025-12-31" | jq

# By branch
curl -s http://localhost:8000/api/reports/by-branch | jq

# Response time (hours)
curl -s http://localhost:8000/api/reports/response-time | jq

# Export CSV (by-status)
curl -s "http://localhost:8000/api/reports/export?kind=by-status"

## 📤 Export Excel
```bash
# Overview
curl -s -OJ "http://localhost:8000/api/reports/export.xlsx?kind=overview"
# By status
curl -s -OJ "http://localhost:8000/api/reports/export.xlsx?kind=by-status"
# By date
curl -s -OJ "http://localhost:8000/api/reports/export.xlsx?kind=by-date&date_from=2025-01-01&date_to=2025-12-31"
# By branch
curl -s -OJ "http://localhost:8000/api/reports/export.xlsx?kind=by-branch"
```

Dependencies:
- openpyxl==3.1.2 (در requirements.txt اضافه شد)
```

## 🎯 گام‌های بعدی (در صورت توسعه)
- افزودن فیلدهای `branch_id`, `resolved_at`, `closed_at` به مدل Ticket
- تکمیل گزارش‌های `by-branch` و `response-time`
- افزودن Export به CSV/Excel در Endpoint جداگانه
- اتصال نمودارهای داشبورد فرانت‌اند به این Endpoints

---

**تاریخ:** 2025-11-11

