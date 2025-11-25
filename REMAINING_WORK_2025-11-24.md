# 📋 کارهای باقی‌مانده (نسخه به‌روز شده 2025-11-24)
## Iranmehr Ticketing – Remaining Work Snapshot

> این فایل نسخه جدید و پیشرفته سند REMAINING_WORK است که برای سخت‌سازی Production و برنامه توسعه آینده استفاده می‌شود. نسخه اصلی همچنان در `REMAINING_WORK.md` موجود است.

---

### 🎯 وضعیت کلان

| فاز | وضعیت | توضیح |
| --- | --- | --- |
| فاز 0 تا 6 | 100% ✅ | تحلیل، طراحی، بک‌اند، فرانت‌اند، تست‌های پایه، استقرار مرجع |
| فاز 7 (مستندسازی/آموزش) | 60% | نیازمند تکمیل راهنماهای کاربری و ویدیوها |
| فاز 8 (قابلیت‌های آینده) | 10% | Knowledge Base، Real-time، AI، Multi-tenant |
| DevOps & Ops Excellence | 70% | Domain/SSL automation، CI/CD، Monitoring، Security hardening |

**جمع‌بندی**: نسخه عملیاتی آماده بهره‌برداری است؛ تمرکز فعلی روی hardening، بانک دانش، Real-time/Webhook و دارایی‌های آموزشی است.

---

### 🚀 اولویت‌های اصلی

#### 1. Production Hardening (High)
- کانفیگ دامنه‌ها (`api/admin/portal.iranmehr.com`) + Nginx
- Let’s Encrypt automation + مانیتورینگ انقضای SSL
- CI/CD با GitHub Actions (lint/test → build → deploy)
- مانیتورینگ و لاگ‌گیری (Prom, Grafana, Loki/ELK)
- امنیت کاربردی: Rate Limiting، API Keys، Audit Log، 2FA
- Redis برای Session/Cache و تدوین Runbook های Disaster Recovery

#### 2. Knowledge Experience (High)
- موتور بانک دانش (CRUD، تگ، versioning، سطح دسترسی)
- جستجوی تمام‌متنی + پیشنهاد مقاله در فرم ثبت تیکت
- نمایش KB در پورتال و محدودیت بر اساس نقش/شعبه
- مستندات کاربری/ادمین دو زبانه، FAQ و تارگت ویدیوهای آموزشی

#### 3. Real-time & Integrations (Medium)
- WebSocket Gateway و Notification Center
- Webhook Platform با امضا، retry و dashboard
- CRM Connector (Dynamics/Zoho) برای سنک مشتریان/تیکت‌ها
- Performance/Load Testing (k6 یا Locust) برای 500 کاربر همزمان

#### 4. Intelligent & Scale Features (Low/R&D)
- AI Assist (summaries, templates, sentiment)
- Real-time Chat در تیکت‌ها
- Multi-Tenant (schema isolation, branding, delegation)
- Self-healing automation و escalation نسل بعد

---

### ⏱️ تخمین زمان

| محور | زمان |
| --- | --- |
| Hardening & Ops | 8-10 روز |
| Knowledge Base + Portal Integration | 5-7 روز |
| WebSocket + Webhook | 6-8 روز |
| Performance Testing | 2-3 روز |
| Documentation & Training Assets | 4-5 روز |
| قابلیت‌های آینده (CRM/AI/Multi-Tenant) | 20-30 روز (اختیاری) |

**Production Hardened ETA**: ~20-25 روز کاری  
**Future Features ETA**: +30-40 روز کاری

---

### 📝 نکات کلیدی
1. مسیرهای حیاتی (Ticketing، SLA، Automation، Notifications، Bot، Web Admin، Portal) در Staging پایدار هستند.
2. اسکریپت‌های مهاجرت (`scripts/migrate_v*`, `setup_production.py`) آماده PostgreSQL هستند؛ تنها Runbook نهایی لازم است.
3. RBAC، JWT، CORS و تست‌های امنیتی موجودند؛ Rate Limit، API Keys، Audit Trail و 2FA باید اضافه شوند.
4. نیاز فوری به Observability یکپارچه برای تضمین SLA 99.5%.
5. این فایل با `SUMMARY.md`, `PROJECT_STATUS_UPDATE.md`, `PHASE_ROADMAP.md` و اسناد بخش `docs/` همسو است. نقشه اجرایی مرحله‌به‌مرحله در `docs/EXECUTION_PLAN.md` نگهداری می‌شود و ورودی‌های موردنیاز کارفرما در `docs/CONFIG_INPUTS_CHECKLIST.md` ثبت خواهد شد.

---

📌 این نسخه برای جلسات Sync و مدیریت برنامه پایش ماهانه به‌روز می‌شود. برای تغییرات بعدی، نسخه‌بندی جداگانه انجام دهید.***

