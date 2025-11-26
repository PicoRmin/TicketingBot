## Phase 1 – Production Hardening & Security Foundations

> هدف: تضمین پایداری عملیاتی، امنیت و آمادگی استقرار Production قبل از اضافه کردن قابلیت‌های پیشرفته.

### 1. Rate Limiting & API Protection
- پایش ترافیک فعلی مسیرهای حساس (`/api/auth/*`, `/api/tickets`, `/api/files/*`) و تعیین سقف‌های اولیه (مثلاً 5 req/sec برای auth).
- پیاده‌سازی middleware (SlowAPI یا سفارشی) برای محدودسازی بر اساس IP/کاربر و ثبت لاگ نقض.
- فعال‌سازی `limit_req` و `limit_conn` در NGINX برای endpointهای عمومی.
- ایجاد جدول `api_clients` با key hashing، scope و وضعیت و مستندسازی فرآیند صدور/لغو کلید در `docs/PRODUCTION_SETUP.md`.

### 2. 2FA و OTP
- انتخاب TOTP (بر بستر برنامه‌هایی مثل Google Authenticator) به‌عنوان روش پایه و افزودن SMS/Telegram به‌صورت افزونه.
- ساخت جدول `user_mfa` شامل secret، backup codes، trusted devices و تاریخچه فعال‌سازی.
- APIهای `enroll`, `verify`, `disable` با dependency روی نقش و سیاست‌های امنیتی.
- UI تنظیمات حساب برای فعال‌سازی، نمایش QR، مدیریت دستگاه‌های مورد اعتماد و اجبار 2FA برای نقش‌های `central_admin` و `admin`.

### 3. Audit Trail & Session Intelligence
- طراحی جدول `audit_logs` با فیلدهای actor, action, resource, metadata, ip, ua + hash chain برای جلوگیری از دست‌کاری.
- hook در سرویس‌های Auth، مدیریت کاربر، تغییر نقش، حذف تیکت، تغییر قوانین SLA/Automation.
- ذخیره session/refresh tokens در Redis همراه با برچسب دستگاه، IP و زمان آخرین فعالیت.
- API و UI مدیریت session برای terminate دستی و محدودسازی تعداد session همزمان نقش‌های حساس.

### 4. Observability Stack
- استقرار Prometheus + Grafana یا ELK/Loki در کنار سرویس (Docker Compose یا Kubernetes namespace).
- اکسپوز متریک‌های FastAPI (latency، error rate، SLA scheduler cycle)، PostgreSQL، Redis و NGINX.
- ایجاد داشبوردهای SLA، نرخ خطا، استفاده منابع و تعریف Alert برای breach SLA، 5xx spike، انقضای SSL، خطای backup.
- ارسال لاگ‌های ساختاریافته به Loki/ELK با برچسب environment/stage و نگهداشت حداقل 30 روزه.

### 5. CI/CD & Infra-as-Code
- GitHub Actions با مراحل lint/test → build (Docker/Artifacts) → push → deploy staging → manual gate → deploy prod.
- مدیریت secrets با GitHub Encrypted Secrets + SOPS/Ansible Vault برای config حساس.
- Terraform جهت Provision سرورها، security group، load balancer؛ Ansible برای نصب Python, NGINX, systemd, logrotate, monitoring agents.
- افزودن health-check بعد از deploy و سناریوی rollback خودکار در صورت خطای status.

### 6. Redis & Caching Layer
- استقرار Redis (HA با Sentinel یا managed) و تعریف monitoring و backup برای آن.
- استفاده برای session store، rate limit counters، cache گزارش‌های پرمصرف و صف اعلان‌های لحظه‌ای.
- تعریف استراتژی failover و تست خروج اضطراری (failover drill) در Runbook.

### 7. Disaster Recovery & Backup Runbooks
- برنامه‌ریزی backup روزانه PostgreSQL (dump + WAL) با نگهداشت 30 روز در مقصدی امن (S3/NAS).
- سنکرون کردن `storage/uploads` و snapshot فایل‌های تنظیمات (`.env`, `nginx.conf`, `systemd`).
- مستندسازی Runbook بازیابی (DB, Files, Bot Token, Redis) و انجام تست بازگردانی فصلی با ثبت نتایج.
- مانیتورینگ وضعیت backup و ارسال هشدار در صورت شکست یا کمبود فضای ذخیره‌سازی.

---

### خروجی‌های مورد انتظار این فاز
- سرور Production با سیاست‌های امنیتی سخت‌گیرانه، 2FA، rate limit و audit trail فعال.
- Observability کامل (Metrics + Logs + Alerts) و pipeline CI/CD قابل تکرار.
- Runbook و Backup تاییدشده که در تست عملی موفق شده‌اند.

