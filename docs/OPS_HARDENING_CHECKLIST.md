# 🛡️ Iranmehr Ticketing – Ops Hardening Checklist

**نسخه**: 2025-11-24  
**هدف**: همگام‌سازی تمام فعالیت‌های Phase 2 (Hardening & Ops Excellence) با کد موجود و مستندات قبل از اجرای تغییرات بعدی.

---

## 1. وضعیت فعلی (Baseline)

| بخش | مشاهده | فایل/مسیر مرتبط |
| --- | --- | --- |
| تنظیمات برنامه | `app/config.py` تمام متغیرها (DB, SMTP, CORS, Logging) را از `.env` می‌خواند و در حالت Production اعتبارسنجی می‌کند؛ هشدار SQLite در Prod تنها warning است. | `app/config.py` |
| اعتبارسنجی Production | متد `validate_production_settings()` در `app/config.py` در زمان startup و داخل اسکریپت‌های setup/start فراخوانی می‌شود. | `app/config.py`, `scripts/setup_production.py`, `scripts/start_production.sh` |
| لاگینگ | `app/main.py` با FileHandler و StreamHandler روی مسیر `settings.LOG_FILE` تنظیم شده است؛ log path در env قابل تنظیم است. | `app/main.py`, `.env` |
| Health Check | Endpoint `/health` اتصال DB را تست می‌کند و در صورت خطا HTTP 503 می‌دهد. | `app/main.py` |
| استقرار | مستندات `docs/PRODUCTION_SETUP.md`, `docs/PRODUCTION_QUICK_START.md`, `DEPLOYMENT.md` و فایل service (`scripts/ticketing.service`) موجود است؛ اسکریپت‌های check/start/backup نیز آماده‌اند. | چند فایل |
| Backup | اسکریپت‌های کامل لینوکس/ویندوز با لاگ و retention در `scripts/backup.sh`, `scripts/backup.bat`. | `scripts/backup*.sh/.bat` |
| مانیتورینگ | مستند `docs/MONITORING.md` Health/Logging/Alerting را پوشش می‌دهد اما هنوز Prometheus/Grafana/ELK به صورت اجرایی تنظیم نشده است. | `docs/MONITORING.md` |
| امنیت | فایل service محدودیت‌های systemd را اعمال می‌کند، ولی Rate Limiting، API Keys، Audit Logging و 2FA هنوز در backlog است. | `scripts/ticketing.service`, `REMAINING_WORK_2025-11-24.md` |

---

## 2. اقدامات لازمه (Action Items)

| حوزه | شرح اقدام | وضعیت | فایل‌های متاثر |
| --- | --- | --- | --- |
| Domain & DNS | تهیه دامنه‌های نهایی (`api/admin/portal`) و مستندسازی رکوردهای A/CNAME + Failover | نیازمند ورودی کارفرما | `docs/CONFIG_INPUTS_CHECKLIST.md`, `docs/PRODUCTION_SETUP.md` |
| SSL & Webhook | تعیین ایمیل Let’s Encrypt، مسیر گواهی، تنظیم auto-renew و تعریف `TELEGRAM_WEBHOOK_URL` | نیازمند ورودی کارفرما | `docs/PRODUCTION_SETUP.md`, `.env` |
| CI/CD | طراحی pipeline (GitHub Actions یا GitLab CI): lint → tests → build → deploy (systemd/Nginx) + secrets | نیازمند ورودی کارفرما | `.github/workflows/*` (ایجاد)، `docs/EXECUTION_PLAN.md` |
| Observability | انتخاب استک (Prometheus + Grafana یا ELK/Loki)، تعریف metrics/alerts و مسیر لاگ مرکزی | نیازمند ورودی کارفرما | `docs/MONITORING.md`, آینده: `infra/` |
| Security | فعال‌سازی Rate Limit (FastAPI middleware/NGINX), API Keys برای Webhook/Integrations، Audit Logging، 2FA برای نقش‌های حساس | TODO | `app/main.py`, `app/api/*`, `docs/PRODUCTION_SETUP.md` |
| Redis/Cache | تصمیم‌گیری درباره استفاده Redis برای Session/Cache و ذخیره نشست ربات | نیازمند ورودی | `app/services/*`, `docs/PRODUCTION_SETUP.md` |
| Automation Runbooks | تدوین Runbook بازیابی (disaster recovery, failover, restore backup) و اتصال به Backup scripts | TODO | `docs/OPS_HARDENING_CHECKLIST.md` (این فایل), `docs/PRODUCTION_SETUP.md` |
| Access Management | مشخص کردن حساب systemd (پیش‌فرض `www-data`), کلید SSH، سیاست sudo و چرخش رمزها | نیازمند ورودی | `scripts/ticketing.service`, `docs/CONFIG_INPUTS_CHECKLIST.md` |

---

## 3. وابستگی‌ها / ورودی‌های لازم

تمام موارد زیر در `docs/CONFIG_INPUTS_CHECKLIST.md` اضافه یا به‌روزرسانی شد. لطفاً مقادیر موردنیاز را تأمین کنید:

1. دامنه‌ها، DNS Provider و TTL‌ پیشنهادی برای هر زیردامنه.  
2. ایمیل تماس Let’s Encrypt و سیاست تمدید (auto-renew, manual).  
3. اطلاعات کامل سرور Production (IP، سیستم‌عامل، دسترسی SSH/RDP، یوزر سرویس).  
4. جزئیات پایگاه‌داده PostgreSQL (هاست، پورت، نسخه، High Availability).  
5. تنظیمات SMTP نهایی (سرویس‌دهنده، کاربر، رمز، Reply-To، BCC).  
6. کانال‌های اعلان (Slack/Teams/Webhook) برای خطاهای بحرانی.  
7. اهداف عملکردی (حداکثر کاربر همزمان، SLA پاسخ/حل).  
8. سیاست امنیتی 2FA / Audit / API Keys.  
9. استراتژی مستندسازی و آموزش (زبان، قالب، مسئول).  
10. مقصد نهایی Backup (Storage محلی، S3، NAS و retention افزوده).  

> پس از دریافت ورودی‌ها، همین فایل و `docs/PRODUCTION_SETUP.md` به‌روزرسانی خواهد شد تا تمامی اقدامات عملیاتی قطعی شوند.

---

## 4. گام‌های بعدی

1. تکمیل `docs/CONFIG_INPUTS_CHECKLIST.md` توسط کارفرما.  
2. نهایی‌سازی تصمیمات CI/CD، Monitoring و Security بر اساس ورودی‌ها.  
3. اعمال تغییرات در کد/اسکریپت‌ها و به‌روزرسانی مستندات Production.  
4. اجرای Dry-run استقرار + تست Health/Backup/Alerting.  

برای هر اقدام پس از اتمام، وضعیت در جدول بالا به‌روزرسانی و commit خواهد شد.***

