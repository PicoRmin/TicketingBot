# 📦 Backend Backlog — IranMehr Ticketing

> آخرین بروزرسانی: 2025-11-27 — وضعیت کنونی Backend براساس کد، مستندات (README, PROJECT_STATUS, BACKLOG\_UI\_UX, ...)، فازنامه‌ها و لاگ‌های توسعه.
>
> ساختار سند:
> - **Epic**
> - **User Story** (As a / I want to / So that)
> - **Tasks** (با نشانه ✅ انجام شده، ⚠️ در حال پیشرفت، ❌ انجام نشده)
> - **Acceptance Criteria**
> - **Ideas & Notes** (ایده‌های پیشنهادی برای مرحله بعدی)

---

## وضعیت کلی

| بخش | وضعیت | توضیح |
| --- | --- | --- |
| هسته تیکتینگ، پروفایل‌ها، نقش‌ها | ✅ پایدار | APIهای تیکت، کاربران، نقش‌ها و پیوست‌ها عملیاتی هستند. |
| SLA Engine + Scheduler | ✅ فعال | سرویس SLA و هشدارهای پاسخ/حل و Escalation طبق اسناد SLA\_MANAGEMENT راه‌اندازی شده است. |
| Automation Engine | ⚠️ تکمیل اولیه | API/CRUD اتوماسیون فعال است اما rule types محدود به auto-assign/close/notify است. |
| Notification Layer (Email/Telegram) | ✅ | ایمیل و تلگرام پیاده‌سازی شده‌ است؛ نیاز به مانیتورینگ خطا و rate-limit. |
| Observability & Ops | ⚠️ جزئی | لاگ و فایل‌های مانیتورینگ موجود است اما Metrics و health-check جامع نیست. |
| Performance & Scalability | ❌ محدود | تست‌های بار انجام شده اما Auto-scaling، queue و cache هنوز در backlog است. |
| DevEx & Tooling | ⚠️ | اسکریپت‌های فازها و setup وجود دارد؛ نیاز به lint/test pipelines و upgrade TypeScript/backend libs. |

---

## EPIC 1 — Core Ticketing Platform (CRUD, RBAC, Attachments) ✅ 85%

### Story BE1-S1 — Ticket CRUD & Workflow
- **As a** support lead  
  **I want to** manage tickets end-to-end  
  **So that** تیم پشتیبانی بتواند lifecycle کامل را پوشش دهد.
- **Tasks**
  - ✅ API endpoints `/api/tickets`, status transitions، فیلدهای سفارشی و Time Tracker.
  - ✅ Attachments (upload/download) با محدودیت اندازه و پسوند.
  - ⚠️ Validation خطاهای رایج (duplicate, concurrency) مستندسازی شده اما تست Integration نیاز به گسترش دارد.
- **Acceptance Criteria**
  - CRUD کامل + فیلترها + pagination + search.
  - رویدادهای تیکت در SLA/Automation مصرف شوند.
- **Ideas**
  - افزودن optimistic locking (ETag) برای جلوگیری از overwrite.
  - اضافه‌کردن bulk update در API برای هماهنگی با UI (Bulk Actions).

### Story BE1-S2 — RBAC & Profiles
- **Tasks**
  - ✅ مدل نقش‌ها (6 نقش) + middleware بررسی role.
  - ⚠️ Endpoint مدیریت نقش‌ها فقط برای Admin موجود؛ نیاز به audit trail.
  - ❌ عدم وجود feature flag برای نقش‌های جدید.
- **Ideas**
  - Audit log قابل جستجو برای تغییر نقش.
  - ادغام با SSO یا OAuth در مراحل آینده.

---

## EPIC 2 — SLA Engine & Compliance ✅ 80%

### Story BE2-S1 — SLA Rule Engine
- **Tasks**
  - ✅ مدل `SLARule`, `SLALog`, هشدارهای warning/breach.
  - ✅ Scheduler هر 5 دقیقه (ارجاع دهید به SLA\_MANAGEMENT.md).
  - ⚠️ Escalation فقط یک مرحله دارد؛ Chain escalation در backlog.
  - ⚠️ برخی گزارش‌ها (Compliance by department) هنوز API ندارند.
- **Acceptance Criteria**
  - SLA براساس priority/category/department اعمال شود.
  - هشدار و لاگ در Dashboard قابل دسترس باشد.
- **Ideas**
  - Multi-threshold escalation + webhook به سیستم‌های خارجی.
  - API برای بازپخش (Backfill) لاگ‌ها در صورت تنظیم قانون جدید.

### Story BE2-S2 — SLA Analytics & Reporting
- **Tasks**
  - ✅ Endpoint `/api/reports/sla-compliance` (توسط Dashboard مصرف می‌شود).
  - ⚠️ گزارش‌های advanced (Trend, per agent) هنوز تولید نشده است.
  - ❌ API برای export مستقیم (CSV/PDF) از گزارش SLA.
- **Ideas**
  - جداسازی لایه گزارش به سرویس مستقل با caching.
  - استفاده از materialized views یا Redis برای سرعت بیشتر.

---

## EPIC 3 — Automation & Rules ⚠️ 60%

### Story BE3-S1 — Automation CRUD
- **Tasks**
  - ✅ CRUD کامل با rule types پایه.
  - ✅ Triggers روی تیکت‌ها.
  - ⚠️ Actions محدود به assign/close/notify؛ هنوز Webhook, SLA adjust, comment inject وجود ندارد.
  - ⚠️ Validation پیچیده (مثلا conflict شرط‌ها) ساده است.
- **Acceptance Criteria**
  - اعمال rule در صف queue و idempotent باشد.
  - تست Performance برای تعداد rule بالا.
- **Ideas**
  - Rule Simulator API برای تست قوانین.
  - ذخیره history اجرای rule در log table جهت audit.

### Story BE3-S2 — Rule Engine Reliability
- **Tasks**
  - ❌ Retry و dead-letter queue برای اجرای ناموفق.
  - ❌ Feature flag برای فعال/غیرفعال کردن rule بدون حذف.
- **Ideas**
  - ادغام با سیستم message queue (Redis, RabbitMQ).
  - اضافه‌کردن rate limit روی actions حساس (اعلان‌ها).

---

## EPIC 4 — Notifications & Integrations ✅ 75%

### Story BE4-S1 — Email & Telegram
- **Tasks**
  - ✅ Email templates (Subject, body) + variables (تیکت).
  - ✅ Telegram Bot (ارسال اعلان).
  - ⚠️ QoS: عدم وجود retry/backoff منظم.
  - ⚠️ عدم وجود health monitor برای webhook تلگرام.
- **Ideas**
  - Notification preference per user.
  - اضافه‌کردن push notifications یا SMS.
  - قابلیت silence window (خواب اعلان).

### Story BE4-S2 — Webhook/API Integrations
- **Tasks**
  - ❌ Generic webhook برای اطلاع‌رسانی به سیستم‌های بیرونی.
  - ❌ API token management در UI/Backend (در REMAINING\_WORK ذکر شده).
- **Ideas**
  - ایجاد جدول `integration_hooks` با secret + retry policy.

---

## EPIC 5 — Observability, Ops & Security ⚠️ 50%

### Story BE5-S1 — Monitoring & Logging
- **Tasks**
  - ⚠️ لاگ‌ها موجود است اما ساختار centralized (ELK/ Loki) تعریف نشده.
  - ❌ Metrics (Prometheus) برای SLA، Queue، Errors.
  - ⚠️ Health-check ها محدود به `/health`; نیاز به readiness/liveness.
- **Acceptance Criteria**
  - داشبورد مانیتورینگ با KPI های SLA/Automation/Notifications.
- **Ideas**
  - استفاده از OpenTelemetry.
  - تعریف alert policy برای breach rate بالا.

### Story BE5-S2 — Security & Compliance
- **Tasks**
  - ⚠️ Rate limit روی APIهای حساس محدوده است.
  - ❌ Password rotation policy و 2FA هنوز مطرح نشده.
  - ⚠️ نیاز به بررسی مداوم CORS و CSRF (مستندات QUICK\_CORS\_FIX وجود دارد، ولی خودکار نشده).
- **Ideas**
  - افزودن Security checklist در pipeline.
  - Static analysis (Bandit, Safety) در CI.

---

## EPIC 6 — Performance & Scalability ❌ 35%

### Story BE6-S1 — Caching & Query Optimization
- **Tasks**
  - ❌ Redis/Cache layer پیاده‌سازی نشده.
  - ⚠️ برخی گزارش‌ها از View ها استفاده می‌کنند اما index tuning نیاز به برنامه دارد (ارجاع به PERFORMANCE\_TESTS.md).
- **Ideas**
  - Cache برای lookups (departments, branches).
  - Lazy load بزرگ‌داده (logs, attachments).

### Story BE6-S2 — Queue & Background Jobs
- **Tasks**
  - ⚠️ Scheduler SLA وجود دارد اما Job runner یکپارچه نیست.
  - ❌ صف background برای email/automation (Celery/RQ) تعریف نشده.
- **Ideas**
  - Unified job service با قابلیت retry/backoff.
  - شکست jobs به صورت observable (Dashboard).

---

## EPIC 7 — Data Lifecycle & Compliance ⚠️ 40%

### Story BE7-S1 — File Lifecycle
- **Tasks**
  - ✅ Upload/Download + محدودیت حجم.
  - ❌ سیاست retention برای فایل‌ها (cleanup).
- **Ideas**
  - انتقال آرشیو به object storage (S3/MinIO).
  - اسکن بدافزار هنگام upload.

### Story BE7-S2 — Data Export & Backup
- **Tasks**
  - ⚠️ اسکریپت‌های backup موجود است اما Automation و alert ندارد.
  - ❌ API برای export داده‌ها بر اساس GDPR/DSAR.
- **Ideas**
  - Snapshot jobs + گزارش موفق/ناموفق.
  - ابزار self-service برای کاربران جهت export تیکت‌ها.

---

## EPIC 8 — DevEx & Tooling ⚠️ 55%

### Story BE8-S1 — Testing & CI
- **Tasks**
  - ✅ بیش از 180 تست (unit/integration/e2e) طبق README.
  - ⚠️ لاین lint/ type-check برای backend در CI کامل نیست.
  - ⚠️ TypeScript نسخه 5.9 در frontend باعث هشدار tooling شده؛ باید هماهنگ با backend scripts شود.
- **Ideas**
  - GitHub Actions یا GitLab CI با stages (lint, test, build, deploy).
  - Test matrix برای Python 3.10/3.11.

### Story BE8-S2 — Documentation & Runbooks
- **Tasks**
  - ✅ مستندات متعدد (README, PHASE docs, FAQ, OPS Hardening).
  - ⚠️ Runbook برای Failure (سرور down, queue backlog) ناقص است.
- **Ideas**
  - مستند Runbook حادثه و escalation chain.
  - خودکارسازی لینک مستندات در UI (Tooltips).

---

## گام‌های پیشنهادی بعدی (Roadmap)
1. **تثبیت Observability:** اضافه‌کردن health metrics، alerting، log aggregation.
2. **گسترش Automation:** Rule simulator، webhook actions، queue-based execution.
3. **Performance Layer:** Cache، async jobs، scale-out scheduler.
4. **Security و Compliance:** Rate-limit، 2FA، data retention و GDPR export.
5. **DevEx/CICD:** Pipeline استاندارد با lint/type/test برای Python + frontend، upgrade TypeScript به نسخه پشتیبانی‌شده.

---

> این backlog با مرور تمامی مستندات `.md` پروژه، README، گزارش‌های وضعیت و فازها تنظیم شد تا تصویری واحد از وضعیت Backend ارائه دهد. لطفاً در صورت اضافه‌شدن قابلیت جدید یا تغییر معماری، این سند را همزمان به‌روزرسانی کنید.

