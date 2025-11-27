## Product Backlog جامع سیستم Helpdesk + Monitoring + ITSM + Asset Management + Telegram Bot

این فایل یک **Backlog کامل، ساختارمند و توسعه‌محور** برای استفاده در **Jira / GitHub Issues** است.  
تمام آیتم‌ها به صورت:

- **Epic**
- **User Story** (با فرمت: As a / I want / So that)
- **Tasks**
- **Acceptance Criteria**

ساختاردهی شده‌اند تا:

- به‌راحتی در Jira به عنوان Epic / Story / Sub-task ثبت شوند.
- یا در GitHub به صورت Issue / Label / Checklist استفاده شوند.

در هر Story یک **کد یکتا** (`EPx-Sy`) آمده که می‌توانی از آن برای Key یا Summary استفاده کنی.

---

## 📊 وضعیت کلی Backlog

**تاریخ آخرین به‌روزرسانی:** 2025-01-26  
**وضعیت کلی:** ⚠️ **حدود 67% از Backlog تکمیل شده**

### 📊 جدول وضعیت Epic‌ها:

| Epic | عنوان | وضعیت | درصد تکمیل |
|------|-------|-------|------------|
| EPIC 1 | احراز هویت و مدیریت کاربران | ⚠️ | 60% |
| EPIC 2 | سیستم Helpdesk | ✅ | 100% |
| EPIC 3 | سیستم مانیتورینگ | ❌ | 15% |
| EPIC 4 | Asset Management | ❌ | 0% |
| EPIC 5 | Telegram Bot Integration | ⚠️ | 67% |
| EPIC 6 | ITSM Processes | ❌ | 0% |
| EPIC 7 | Notifications & Alerts | ✅ | 71% |
| EPIC 8 | داشبورد مدیریتی | ✅ | 100% |
| EPIC 9 | سیستم تنظیمات | ✅ | 86% |
| EPIC 10 | زیرساخت و DevOps | ❌ | 0% |

### ✅ قابلیت‌های پیاده‌سازی شده:
- ✅ سیستم Helpdesk کامل (ایجاد، لیست، جزئیات، کامنت، تغییر وضعیت، SLA، فایل)
- ✅ احراز هویت با JWT و Refresh Token
- ✅ RBAC کامل با نقش‌های مختلف
- ✅ مدیریت پروفایل و Onboarding
- ✅ **Telegram Bot پیشرفته**:
  - ✅ اتصال حساب، نوتیفیکیشن، منوی اینلاین
  - ✅ مشاهده جزئیات کامل تیکت (تاریخچه، کامنت‌ها، فایل‌ها)
  - ✅ پاسخ و کامنت روی تیکت (با امکان attach فایل)
  - ✅ فیلتر و جستجوی پیشرفته تیکت‌ها
  - ✅ مدیریت اولویت تیکت
  - ✅ تخصیص تیکت (با نمایش workload)
  - ✅ عملیات دسته‌ای تیکت‌ها (Bulk Actions)
- ✅ Email Notifications با 14 قالب HTML
- ✅ Telegram Alerts
- ✅ SLA Management و Monitoring
- ✅ Automation Rules (Auto-Assign, Auto-Close, Auto-Notify)
- ✅ Custom Fields (11 نوع فیلد)
- ✅ Time Tracker
- ✅ Knowledge Base
- ✅ داشبورد کامل با گزارش‌ها و نمودارها
- ✅ Export به CSV/Excel/PDF
- ✅ سیستم تنظیمات (شعب، دپارتمان‌ها، اولویت‌ها، SLA، Automation)
- ✅ Branch Infrastructure (ثبت اطلاعات)

### ❌ قابلیت‌های اصلی کمبود:
- ❌ ثبت‌نام کاربر (کاربران از طریق Admin ایجاد می‌شوند)
- ❌ بازیابی رمز عبور
- ❌ Audit Log
- ❌ تنظیمات امنیتی (Password Policy, Session Policy)
- ❌ Monitoring Real-time (Agent، روترها، سرویس‌ها)
- ❌ Asset Management (تمام Storyها)
- ❌ ITSM Processes (Incident، Problem، Change)
- ❌ SMS Notifications
- ❌ Web Push Notifications
- ❌ مدیریت Templateهای اعلانات از UI
- ❌ DevOps (Docker، CI/CD، Backup)

---

## 🔵 EPIC 1 — سیستم احراز هویت و مدیریت کاربران (Authentication & Authorization) ⚠️ **60% تکمیل شده**

هدف: پیاده‌سازی یک سیستم امن برای ثبت‌نام، لاگین، مدیریت نقش‌ها و پروفایل کاربران.

### Story EP1-S1 — ثبت‌نام کاربر جدید با ایمیل/موبایل ❌ **انجام نشده - کاربران از طریق Admin ایجاد می‌شوند**

**As a** new user  
**I want to** register with email or mobile  
**So that I can** access the system securely

- **Tasks**
  - ❌ **Task 1**: API `POST /auth/register` وجود ندارد
  - ✅ **Task 2**: مدل `User` با فیلدهای لازم موجود است
  - ❌ **Task 3**: اعتبارسنجی ثبت‌نام وجود ندارد
  - ❌ **Task 4**: ارسال کد تأیید پیاده‌سازی نشده
  - ❌ **Task 5**: Audit Log برای ثبت‌نام وجود ندارد
  - ❌ **Task 6**: تست‌ها نوشته نشده

- **Acceptance Criteria**
  - ❌ کاربر نمی‌تواند خودش ثبت‌نام کند (کاربران از طریق Admin ایجاد می‌شوند).
  - ❌ API ثبت‌نام وجود ندارد.
  - ❌ کد تأیید ارسال نمی‌شود.
  - ❌ Audit Log وجود ندارد.

---

### Story EP1-S2 — ورود کاربر (Login با JWT) ✅ **انجام شده**

**As a** registered user  
**I want to** log in using my email/mobile and password  
**So that I can** access protected resources

- **Tasks**
  - ✅ **Task 1**: API `POST /api/auth/login` و `POST /api/auth/login-form` موجود است
  - ✅ **Task 2**: JWT با `HS256` و کلید مخفی از `.env` استفاده می‌شود
  - ❌ **Task 3**: Rate Limiting روی لاگین پیاده‌سازی نشده
  - ✅ **Task 4**: Refresh Token در جدول `refresh_tokens` ذخیره می‌شود
  - ✅ **Task 5**: API `POST /api/auth/refresh` موجود است
  - ✅ **Task 6**: سناریوهای خطا مدیریت می‌شوند

- **Acceptance Criteria**
  - ✅ ورود با **username/رمز عبور** امکان‌پذیر است.
  - ✅ در صورت نامعتبر بودن اطلاعات، پیام خطای استاندارد برگردانده می‌شود.
  - ✅ در صورت موفقیت، **JWT Access Token** و **Refresh Token** بازگردانده می‌شود.
  - ❌ پس از چند تلاش ناموفق، حساب قفل نمی‌شود.
  - ⚠️ تلاش‌های ورود لاگ می‌شوند اما Audit Log کامل نیست.

---

### Story EP1-S3 — مدیریت نقش‌ها و دسترسی‌ها (RBAC) ✅ **انجام شده**

**As an** Admin  
**I want to** define roles and permissions  
**So that I can** control what each user can access

- **Tasks**
  - ✅ **Task 1**: نقش‌ها در Enum `UserRole` تعریف شده
  - ✅ **Task 2**: نقش‌های پیش‌فرض موجود است: `central_admin`, `admin`, `branch_admin`, `it_specialist`, `report_manager`, `user`
  - ✅ **Task 3**: Dependencies کامل موجود است (`get_current_user`, `require_admin`, `require_central_admin`, `require_branch_admin`, `require_report_access`)
  - ✅ **Task 4**: APIهای مدیریت کاربران موجود است: `GET/POST/PATCH/DELETE /api/users`
  - ❌ **Task 5**: Middleware برای ثبت لاگ دسترسی‌های رد شده وجود ندارد

- **Acceptance Criteria**
  - ✅ فقط **Admin** می‌تواند کاربر جدید ایجاد یا ویرایش کند.
  - ✅ کاربران با نقش `it_specialist` فقط تیکت‌های تخصیص داده شده به خود را می‌بینند.
  - ✅ `Branch Admin` فقط تیکت‌های **شعبه خودش** را می‌بیند.
  - ✅ اگر کاربری مجوز دسترسی نداشته باشد، API **کد 403** برمی‌گرداند.

---

### Story EP1-S4 — مدیریت پروفایل کاربری ⚠️ **بخش‌های اصلی انجام شده**

**As a** user  
**I want to** view and update my profile  
**So that I can** keep my information up-to-date

- **Tasks**
  - ✅ **Task 1**: API `GET /api/auth/me` برای دریافت اطلاعات پروفایل
  - ✅ **Task 2**: API `POST /api/profile/onboarding` برای ویرایش پروفایل
  - ❌ **Task 3**: امکان تغییر پسورد وجود ندارد
  - ❌ **Task 4**: اعتبارسنجی قوی پسورد وجود ندارد
  - ⚠️ **Task 5**: تست‌های محدود موجود است

- **Acceptance Criteria**
  - ✅ کاربر می‌تواند **پروفایل خود** را مشاهده و ویرایش کند.
  - ❌ برای تغییر پسورد، API وجود ندارد.
  - ❌ تاریخ آخرین تغییر پسورد ذخیره نمی‌شود.

---

### Story EP1-S5 — بازیابی رمز عبور (Password Reset) ❌ **انجام نشده**

**As a** user who forgot the password  
**I want to** reset my password securely  
**So that I can** regain access

- **Tasks**
  - ❌ **Task 1**: API `POST /auth/forgot-password` وجود ندارد
  - ❌ **Task 2**: جدول `password_resets` وجود ندارد
  - ❌ **Task 3**: API `POST /auth/reset-password` وجود ندارد
  - ❌ **Task 4**: بی‌اعتبار کردن سشن‌ها پیاده‌سازی نشده

- **Acceptance Criteria**
  - ❌ توکن بازیابی وجود ندارد.
  - ❌ API بازیابی رمز عبور وجود ندارد.
  - ❌ پس از ریست پسورد، سشن‌ها بی‌اعتبار نمی‌شوند.

---

### Story EP1-S6 — Audit Log و ردیابی فعالیت‌ها ❌ **انجام نشده**

**As an** IT Security Officer  
**I want to** see an audit trail of important actions  
**So that I can** investigate security or misuse

- **Tasks**
  - ❌ **Task 1**: جدول `audit_logs` وجود ندارد
  - ⚠️ **Task 2**: برخی رویدادها در `TicketHistory` ثبت می‌شوند اما Audit Log کامل نیست
  - ❌ **Task 3**: API `GET /admin/audit-logs` وجود ندارد

- **Acceptance Criteria**
  - ❌ رویدادهای حساس در Audit Log ثبت نمی‌شوند.
  - ❌ فیلتر بر اساس بازه زمانی، کاربر، نوع عملیات وجود ندارد.

---

### Story EP1-S7 — تنظیمات امنیتی (Password Policy, Session Policy) ❌ **انجام نشده**

**As an** Admin  
**I want to** configure security policies  
**So that I can** comply with company requirements

- **Tasks**
  - ❌ **Task 1**: تنظیمات Password Policy وجود ندارد
  - ⚠️ **Task 2**: زمان انقضای Token در `.env` قابل تنظیم است اما UI ندارد
  - ❌ **Task 3**: امکان Force Logout همه کاربران وجود ندارد

- **Acceptance Criteria**
  - ❌ سیاست‌های امنیتی در UI قابل تنظیم نیستند.
  - ⚠️ تغییر سیاست‌ها فقط از طریق `.env` امکان‌پذیر است.

---

## 🟣 EPIC 2 — سیستم Helpdesk و مدیریت تیکت‌ها ✅ **100% تکمیل شده**

هدف: مدیریت کامل چرخه حیات تیکت‌ها از ایجاد تا بستن، همراه با SLA و کامنت و فایل.

### Story EP2-S1 — ایجاد تیکت (Ticket Creation) ✅ **انجام شده**

**As an** end user (Branch User / Employee)  
**I want to** create a support ticket  
**So that I can** get help for my IT issues

- **Tasks**
  - ✅ **Task 1**: API `POST /api/tickets` برای ایجاد تیکت
  - ✅ **Task 2**: فیلدها: `title`, `description`, `category`, `priority`, `branch_id`, `department_id`, `attachments`
  - ✅ **Task 3**: تعیین SLA بر اساس Priority و یا Ruleهای SLA
  - ✅ **Task 4**: ثبت `created_at`, `sla_due_at`, `status = PENDING`

- **Acceptance Criteria**
  - ✅ `title` و `category` فیلدهای اجباری هستند.
  - ✅ پس از ایجاد، شماره تیکت یکتا (`T-YYYYMMDD-####`) تولید می‌شود.
  - ✅ SLA Deadline بر اساس قوانین SLA محاسبه و ذخیره می‌شود.

---

### Story EP2-S2 — لیست و فیلتر تیکت‌ها ✅ **انجام شده**

**As an** Agent / Admin  
**I want to** list and filter tickets  
**So that I can** manage workload efficiently

- **Tasks**
  - ✅ **Task 1**: API `GET /api/tickets` با فیلتر: `status`, `branch_id`, `assigned_to_id`, `priority`, `category`, `created_from/to`
  - ✅ **Task 2**: پیاده‌سازی Pagination (پارامترهای `page`, `page_size`)
  - ✅ **Task 3**: امکان Sort بر اساس `created_at`, `priority`, `sla_due_at`

- **Acceptance Criteria**
  - ✅ لیست پیش‌فرض حداکثر ۲۰ تیکت در هر صفحه (قابل تنظیم).
  - ✅ اگر تیکتی وجود نداشته باشد، پیام مناسب برگردانده می‌شود.
  - ✅ فیلترها و Sorting هم‌زمان قابل استفاده هستند.

---

### Story EP2-S3 — جزئیات تیکت و تاریخچه ✅ **انجام شده**

**As an** Agent  
**I want to** see full ticket details  
**So that I can** understand the context and history

- **Tasks**
  - ✅ **Task 1**: API `GET /api/tickets/{id}` با تمام جزئیات
  - ✅ **Task 2**: نمایش تاریخچه پیام‌ها، تغییر وضعیت‌ها، تغییر Agent، پیوست‌ها
  - ✅ **Task 3**: طراحی مدل `TicketHistory` برای ذخیره Event Log

- **Acceptance Criteria**
  - ✅ تمام تغییرات تیکت در `TicketHistory` قابل مشاهده است.
  - ✅ امکان مشاهده رویدادها به ترتیب زمانی وجود دارد.
  - ✅ فایل‌های ضمیمه لینک دانلود امن دارند.

---

### Story EP2-S4 — پاسخ به تیکت و کامنت‌ها ✅ **انجام شده**

**As an** Agent  
**I want to** reply to tickets and add internal notes  
**So that I can** communicate with users and the team

- **Tasks**
  - ✅ **Task 1**: API `POST /api/tickets/{id}/comments` با نوع `is_internal` (public/internal)
  - ✅ **Task 2**: ثبت Event برای هر پاسخ در تاریخچه
  - ✅ **Task 3**: ارسال نوتیفیکیشن (ایمیل/تلگرام) به کاربر در صورت پاسخ `public`

- **Acceptance Criteria**
  - ✅ Agent می‌تواند پاسخ عمومی برای کاربر ثبت کند.
  - ✅ Agent می‌تواند کامنت داخلی فقط قابل مشاهده برای تیم پشتیبانی ثبت کند.
  - ✅ پس از پاسخ، وضعیت تیکت در صورت نیاز به **"IN_PROGRESS"** تغییر می‌کند (قابل تنظیم).

---

### Story EP2-S5 — تغییر وضعیت تیکت و بستن تیکت ✅ **انجام شده**

**As an** Agent / User  
**I want to** change ticket status  
**So that I can** reflect the real state of the request

- **Tasks**
  - ✅ **Task 1**: تعریف Statusها: `PENDING`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`
  - ✅ **Task 2**: API `PATCH /api/tickets/{id}/status` با ثبت علت تغییر (comment)
  - ✅ **Task 3**: ثبت `resolved_at` و `closed_at` در صورت تغییر مناسب

- **Acceptance Criteria**
  - ✅ کاربر می‌تواند تیکت خود را در حالت‌های مجاز ببندد.
  - ✅ Agent می‌تواند وضعیت تیکت را تغییر دهد.
  - ✅ تاریخ و کاربر تغییر دهنده در تاریخچه ذخیره می‌شوند.

---

### Story EP2-S6 — SLA Management برای تیکت‌ها ✅ **انجام شده**

**As an** IT Manager  
**I want to** configure and track SLA rules  
**So that I can** ensure timely resolution of tickets

- **Tasks**
  - ✅ **Task 1**: طراحی جداول `sla_rules`, `sla_logs`
  - ✅ **Task 2**: تعیین زمان پاسخ اولیه و زمان حل بر اساس Priority و Category
  - ✅ **Task 3**: Scheduler برای بررسی SLA هر 15 دقیقه
  - ✅ **Task 4**: ثبت هشدار SLA و Breach در `sla_logs` و ارسال نوتیفیکیشن

- **Acceptance Criteria**
  - ✅ برای هر تیکت، SLA هدف در لحظه ایجاد محاسبه و ذخیره می‌شود.
  - ✅ قبل از نزدیک‌شدن به Deadline، هشدار برای Agent/Manager ارسال می‌شود.
  - ✅ در صورت Breach، در گزارش SLA قابل مشاهده است.

---

### Story EP2-S7 — پیوست فایل به تیکت ✅ **انجام شده**

**As a** user/agent  
**I want to** attach files to tickets  
**So that I can** provide more context (screenshots, logs)

- **Tasks**
  - ✅ **Task 1**: API `POST /api/files/upload` با محدودیت حجم و نوع فایل
  - ✅ **Task 2**: ذخیره فایل‌ها در پوشه امن (`storage/uploads`)، ثبت متادیتا در DB
  - ✅ **Task 3**: بررسی امنیتی (اعتبارسنجی نوع و حجم فایل)
  - ✅ **Task 4**: لینک دانلود امن با دسترسی کنترل شده (`GET /api/files/{id}/download`)

- **Acceptance Criteria**
  - ✅ فقط کاربران مجاز به تیکت می‌توانند پیوست‌ها را دانلود کنند.
  - ✅ حداکثر حجم و نوع فایل‌ها از طریق تنظیمات قابل کنترل است.

---

## 🟢 EPIC 3 — سیستم مانیتورینگ شبکه و سرورها (Monitoring & Networking) ❌ **15% تکمیل شده**

هدف: پایش مداوم وضعیت سرورها، روترها، سرویس‌ها و لینک‌های شبکه.

**نکته:** فقط `BranchInfrastructure` برای ثبت اطلاعات زیرساخت موجود است. مانیتورینگ Real-time وجود ندارد.

### Story EP3-S1 — Agent سبک برای کلاینت‌ها/سرورها ❌ **انجام نشده**

**As an** Infrastructure Engineer  
**I want to** have a lightweight agent  
**So that I can** collect metrics from servers and clients

- **Tasks**
  - **Task 1**: طراحی پروتکل ارسال متریک (HTTP یا gRPC) به `/monitoring/ingest`
  - **Task 2**: تعریف ساختار JSON شامل CPU, RAM, Disk, Network
  - **Task 3**: احراز هویت با Token برای هر Agent
  - **Task 4**: ذخیره متریک‌ها در جدول/Time-Series DB

- **Acceptance Criteria**
  - Agent بتواند در بازه‌های زمانی تنظیم‌شده (مثلاً هر ۳۰ ثانیه) متریک ارسال کند.
  - درخواست‌های بدون Token معتبر رد شوند (401).

---

### Story EP3-S2 — مانیتورینگ روترها و سوئیچ‌ها (Mikrotik / Cisco) ❌ **انجام نشده**

**As a** Network Engineer  
**I want to** monitor routers and switches  
**So that I can** detect link or bandwidth issues

- **Tasks**
  - ❌ **Task 1**: تعریف موجودیت `NetworkDevice` (آدرس IP، نوع دستگاه، API/SSH/SNMP) - *انجام نشده*
  - ❌ **Task 2**: پیاده‌سازی ماژول جمع‌آوری متریک (Ping, Interface Traffic) - *انجام نشده*
  - ❌ **Task 3**: Scheduler برای Poll کردن دستگاه‌ها - *انجام نشده*

- **Acceptance Criteria**
  - ❌ برای هر دستگاه، وضعیت Reachability (Up/Down) ثبت شود - *انجام نشده*
  - ❌ ترافیک Interfaceهای کلیدی در دیتابیس ذخیره و قابل نمایش در داشبورد باشد - *انجام نشده*
  - ❌ در صورت Down شدن لینک، Alert تولید شود - *انجام نشده*

---

### Story EP3-S3 — Check سرویس‌ها (HTTP/TCP/Port Check) ❌ **انجام نشده**

**As an** IT Manager  
**I want to** monitor critical services  
**So that I can** react quickly if they go down

- **Tasks**
  - ❌ **Task 1**: جدول `service_checks` وجود ندارد
  - ❌ **Task 2**: Worker برای اجرای دوره‌ای Checkها وجود ندارد
  - ❌ **Task 3**: جدول `service_check_results` وجود ندارد
  - ❌ **Task 4**: تولید Alert وجود ندارد

- **Acceptance Criteria**
  - ❌ Alert برای سرویس‌های Down ایجاد نمی‌شود.
  - ❌ هشدار برای latency وجود ندارد.

---

### Story EP3-S4 — داشبورد گراف‌ها و متریک‌ها ❌ **انجام نشده**

**As an** operations team  
**I want to** see metrics dashboards  
**So that I can** understand system health at a glance

- **Tasks**
  - ❌ **Task 1**: APIهای Read برای متریک‌ها وجود ندارد
  - ❌ **Task 2**: نمودارهای CPU, RAM, Disk, Network وجود ندارد
  - ❌ **Task 3**: بازه‌های زمانی ۲۴ساعته، ۷روزه، ۳۰روزه وجود ندارد

- **Acceptance Criteria**
  - ❌ داشبورد Real-time وجود ندارد.
  - ❌ مشاهده روند متریک‌ها امکان‌پذیر نیست.

---

### Story EP3-S5 — Threshold & Alert Rules برای مانیتورینگ ❌ **انجام نشده**

**As an** IT Manager  
**I want to** define alert rules  
**So that I can** receive notifications only when necessary

- **Tasks**
  - ❌ **Task 1**: جدول `monitoring_rules` وجود ندارد
  - ❌ **Task 2**: موتور ارزیابی Ruleها وجود ندارد
  - ❌ **Task 3**: اتصال Ruleها به Notifications وجود ندارد

- **Acceptance Criteria**
  - ❌ Ruleها برای مانیتورینگ تعریف نمی‌شوند.
  - ❌ Alertهای Deduplicate وجود ندارد.

---

### Story EP3-S6 — مشاهده وضعیت شعب (Branch Health Overview) ⚠️ **بخشی انجام شده**

**As a** Regional Manager  
**I want to** see branch connectivity status  
**So that I can** react to branch outages

**نکته:** فقط ثبت اطلاعات زیرساخت موجود است. مانیتورینگ Real-time وجود ندارد.

- **Tasks**
  - ✅ **Task 1**: مدل `BranchInfrastructure` برای ثبت تجهیزات موجود است
  - ⚠️ **Task 2**: صفحه Infrastructure برای ثبت اطلاعات موجود است اما مانیتورینگ Real-time نیست

- **Acceptance Criteria**
  - ⚠️ اطلاعات زیرساخت ثبت می‌شود اما وضعیت Real-time محاسبه نمی‌شود.
  - ❌ شاخص‌ها بر اساس متریک‌های Real-time محاسبه نمی‌شوند.

---

### Story EP3-S7 — گزارش تاریخچه رویدادهای مانیتورینگ ❌ **انجام نشده**

**As an** ITSM Manager  
**I want to** review monitoring events history  
**So that I can** correlate incidents with infrastructure issues

- **Tasks**
  - ❌ **Task 1**: جدول `monitoring_events` وجود ندارد
  - ❌ **Task 2**: API برای فیلتر Events وجود ندارد

- **Acceptance Criteria**
  - ❌ تاریخچه رویدادهای مانیتورینگ وجود ندارد.
  - ❌ Events قابل لینک شدن به Incidentها نیستند.

---

## 🟡 EPIC 4 — Asset Management و مدیریت دارایی‌ها ❌ **0% تکمیل شده**

هدف: ثبت، ردیابی و مدیریت چرخه عمر دارایی‌های IT.

**نکته:** Asset Management به طور کامل پیاده‌سازی نشده است.

### Story EP4-S1 — ثبت دارایی‌های IT ❌ **انجام نشده**

**As an** Asset Manager  
**I want to** register IT assets  
**So that I can** track hardware and ownership

- **Tasks**
  - ❌ **Task 1**: طراحی مدل `Asset` با فیلدها: نوع، مدل، سریال، تاریخ خرید، شعبه، وضعیت، مالک - *انجام نشده*
  - ❌ **Task 2**: API `POST /assets` و `GET /assets` - *انجام نشده*

- **Acceptance Criteria**
  - ❌ امکان ثبت انواع تجهیزات: PC, Laptop, Router, Switch, TV, Printer و … - *انجام نشده*
  - ❌ سریال و مدل و تاریخ خرید فیلدهای اجباری باشد - *انجام نشده*

---

### Story EP4-S2 — اتصال Asset به Agent مانیتورینگ

**As an** Infrastructure Engineer  
**I want to** link assets with monitoring agents  
**So that I can** see health per asset

- **Tasks**
  - **Task 1**: افزودن فیلد `agent_id` به جدول `assets` یا جدول واسط
  - **Task 2**: API برای لینک/آنلینک کردن Asset و Agent

- **Acceptance Criteria**
  - هر Agent بتواند حداکثر به یک Asset اصلی متصل شود (در صورت نیاز).
  - در داشبورد مانیتورینگ نام Asset قابل مشاهده باشد.

---

### Story EP4-S3 — تاریخچه تعمیرات و رویدادهای دارایی

**As an** Asset Manager  
**I want to** track maintenance history  
**So that I can** understand asset lifecycle

- **Tasks**
  - **Task 1**: جدول `asset_events` (تعمیر، خرابی، جابجایی، تحویل/پس‌گیری)
  - **Task 2**: API برای ثبت رویدادهای جدید

- **Acceptance Criteria**
  - امکان مشاهده Timeline کامل برای هر Asset وجود داشته باشد.
  - انواع رویداد قابل فیلتر باشند.

---

### Story EP4-S4 — هشدار پایان گارانتی

**As an** Asset Manager  
**I want to** get notified before warranty ends  
**So that I can** take preventive actions

- **Tasks**
  - **Task 1**: افزودن فیلد تاریخ پایان گارانتی به Asset
  - **Task 2**: Scheduler برای بررسی دارایی‌هایی که گارانتی‌شان در حال اتمام است
  - **Task 3**: ارسال نوتیفیکیشن ایمیل/تلگرام

- **Acceptance Criteria**
  - حداقل ۳۰ روز قبل از پایان گارانتی هشدار ارسال شود (قابل تنظیم).

---

### Story EP4-S5 — تخصیص Asset به کاربر/شعبه

**As an** IT Manager  
**I want to** assign assets to users or branches  
**So that I can** track responsibility

- **Tasks**
  - **Task 1**: فیلدهای `assigned_to_user_id` و `branch_id`
  - **Task 2**: API برای تغییر تخصیص

- **Acceptance Criteria**
  - همیشه وضعیت فعلی مالک/محل نگهداری Asset مشخص باشد.

---

### Story EP4-S6 — گزارش دارایی‌ها

**As a** management team  
**I want to** see asset reports  
**So that I can** plan budgeting and replacement

- **Tasks**
  - **Task 1**: API گزارش‌ها بر حسب شعبه، نوع، وضعیت، تاریخ خرید

- **Acceptance Criteria**
  - امکان خروجی به Excel/PDF برای لیست دارایی‌ها وجود داشته باشد.

---

### Story EP4-S7 — برچسب‌گذاری و QR Code برای دارایی‌ها

**As an** on-site technician  
**I want to** scan asset QR codes  
**So that I can** quickly access asset info

- **Tasks**
  - **Task 1**: تولید QR Code برای هر Asset (شامل Asset ID/URL)
  - **Task 2**: API برای بازگرداندن اطلاعات از روی QR/ID

- **Acceptance Criteria**
  - اسکن QR کاربر را به صفحه اطلاعات همان Asset هدایت کند.

---

## 🟠 EPIC 5 — Telegram Bot Integration ⚠️ **43% تکمیل شده**

هدف: اتصال کامل سیستم Helpdesk/Monitoring/Asset به بات تلگرام.

### Story EP5-S1 — ساخت بات تلگرام و اتصال حساب کاربری ✅ **انجام شده**

**As a** system user  
**I want to** link my Telegram account  
**So that I can** receive notifications and interact via bot

- **Tasks**
  - ✅ **Task 1**: تنظیم Bot Token در تنظیمات سیستم
  - ✅ **Task 2**: پیاده‌سازی `/start` برای ایجاد/لینک حساب تلگرام به کاربر
  - ✅ **Task 3**: ذخیره `telegram_chat_id` در پروفایل کاربر

- **Acceptance Criteria**
  - ✅ کاربر با ارسال `/start` می‌تواند حساب خود را لینک کند (از طریق لاگین در بات).

---

### Story EP5-S2 — نوتیفیکیشن تیکت‌ها در تلگرام ✅ **انجام شده**

**As an** Agent/User  
**I want to** receive ticket notifications on Telegram  
**So that I can** respond faster

- **Tasks**
  - ✅ **Task 1**: تعریف Event Handler برای: ایجاد تیکت, تغییر وضعیت, پاسخ جدید, تخصیص تیکت
  - ✅ **Task 2**: ارسال پیام تلگرام با جزئیات حداقلی

- **Acceptance Criteria**
  - ✅ ایجاد تیکت → پیام برای Agent/Admin مرتبط ارسال می‌شود.
  - ✅ پاسخ Agent → پیام برای کاربر ارسال می‌شود.
  - ✅ SLA Breach → پیام هشدار برای IT Manager/Agent مسئول ارسال می‌شود.

---

### Story EP5-S3 — منوی اینلاین برای مدیریت تیکت‌ها ✅ **انجام شده**

**As an** Agent  
**I want to** interact with tickets via Telegram menus  
**So that I can** quickly view and update basic info

- **Tasks**
  - ✅ **Task 1**: پیاده‌سازی منوی اینلاین برای: لیست تیکت‌های باز، جزئیات تیکت، تغییر وضعیت ساده
  - ✅ **Task 2**: پیاده‌سازی ConversationHandler برای سناریوی ایجاد تیکت ساده از داخل تلگرام

- **Acceptance Criteria**
  - ✅ UX ساده و قابل فهم، بدون نیاز به تایپ زیاد.
  - ✅ جلوگیری از خطا در Stateهای Conversation.

---

### Story EP5-S4 — مشاهده وضعیت مانیتورینگ شعب در بات ❌ **انجام نشده**

**As a** Branch Manager  
**I want to** see my branch monitoring status in Telegram  
**So that I can** quickly check health

- **Tasks**
  - ❌ **Task 1**: فرمان `"/branch_status"` وجود ندارد
  - ❌ **Task 2**: نمایش خلاصه وضعیت وجود ندارد

- **Acceptance Criteria**
  - ❌ وضعیت مانیتورینگ شعب در بات نمایش داده نمی‌شود.

---

### Story EP5-S5 — مشاهده دارایی‌های شعبه در بات ❌ **انجام نشده**

**As a** Branch IT responsible  
**I want to** list my branch assets via bot  
**So that I can** see inventory quickly

- **Tasks**
  - ❌ **Task 1**: فرمان `"/assets"` وجود ندارد

- **Acceptance Criteria**
  - ❌ دارایی‌های شعبه در بات نمایش داده نمی‌شوند.

---

### Story EP5-S6 — اعلان‌های مانیتورینگ از طریق بات ❌ **انجام نشده**

**As an** on-call engineer  
**I want to** receive monitoring alerts on Telegram  
**So that I can** respond quickly to incidents

- **Tasks**
  - ❌ **Task 1**: اتصال موتور Alert مانیتورینگ به Bot وجود ندارد

- **Acceptance Criteria**
  - ❌ اعلان‌های مانیتورینگ از طریق بات ارسال نمی‌شوند.

---

### Story EP5-S7 — تنظیم سطوح اعلان تلگرام در پروفایل ❌ **انجام نشده**

**As a** user  
**I want to** configure my Telegram notification level  
**So that I can** avoid spam and focus on critical alerts

- **Tasks**
  - ❌ **Task 1**: تنظیمات سطح اعلان در پروفایل وجود ندارد

- **Acceptance Criteria**
  - ❌ تنظیمات سطح اعلان وجود ندارد.

---

## 🔴 EPIC 6 — ITSM Processes (Incident, Problem, Change) ❌ **0% تکمیل شده**

هدف: پیاده‌سازی فرآیندهای اصلی ITSM روی Helpdesk.

**نکته:** ITSM Processes به طور کامل پیاده‌سازی نشده است.

### Story EP6-S1 — Incident Management ❌ **انجام نشده**

**As an** IT Support Agent  
**I want to** register and manage incidents  
**So that I can** restore normal service ASAP

- **Tasks**
  - ❌ **Task 1**: تعریف نوع تیکت Incident و فیلدهای Impact, Urgency, Severity - *انجام نشده*
  - ❌ **Task 2**: ارتباط Incident با Asset و Service - *انجام نشده*

- **Acceptance Criteria**
  - ❌ Impact/Severity در گزارش‌ها قابل فیلتر باشد - *انجام نشده*

---

### Story EP6-S2 — Problem Management

**As a** Problem Manager  
**I want to** link multiple incidents to a problem  
**So that I can** find root cause and prevent recurrence

- **Tasks**
  - **Task 1**: جدول `problems` و ارتباط `problem_incidents`
  - **Task 2**: ثبت Root Cause, Workaround, Permanent Fix

- **Acceptance Criteria**
  - از روی یک Problem بتوان تمام Incidentهای مرتبط را دید.

---

### Story EP6-S3 — Change Management

**As a** Change Manager  
**I want to** manage change requests  
**So that I can** minimize risk to production

- **Tasks**
  - **Task 1**: تعریف `change_requests` با فیلدهای: نوع تغییر، ریسک، تاریخ اجرای پیشنهادی
  - **Task 2**: Workflow تأیید (Request → Review → Approved/Rejected)

- **Acceptance Criteria**
  - هیچ Change با وضعیت `Pending Approval` نتواند به حالت `Implemented` برود بدون تأیید.

---

### Story EP6-S4 — ربط Incident به Eventهای مانیتورینگ

**As an** ITSM Manager  
**I want to** link incidents to monitoring events  
**So that I can** analyze infrastructure issues

- **Tasks**
  - **Task 1**: امکان Attach کردن `monitoring_event_id` به Incident

- **Acceptance Criteria**
  - در نمای Incident، رویداد مانیتورینگ مرتبط قابل مشاهده باشد.

---

### Story EP6-S5 — ماتریس اولویت Incident (Impact × Urgency)

**As an** IT Manager  
**I want to** standardize incident priority  
**So that I can** triage properly

- **Tasks**
  - **Task 1**: پیاده‌سازی ماتریس Priority بر اساس Impact و Urgency

- **Acceptance Criteria**
  - Priority به‌صورت خودکار بر اساس Impact/Urgeny محاسبه شود.

---

### Story EP6-S6 — گزارش‌های ITSM (Incident/Problem/Change)

**As a** management team  
**I want to** see ITSM metrics  
**So that I can** improve processes

- **Tasks**
  - **Task 1**: گزارش تعداد و میانگین زمان حل Incidentها، تعداد Problemها، میزان تغییرات موفق/ناموفق

- **Acceptance Criteria**
  - گزارش‌ها قابل فیلتر بر اساس بازه زمانی و شعبه باشند.

---

### Story EP6-S7 — Templateهای استاندارد برای Incident/Change

**As an** Agent  
**I want to** use templates  
**So that I can** create consistent tickets

- **Tasks**
  - **Task 1**: تعریف Template برای انواع Incident/Change تکراری

- **Acceptance Criteria**
  - Agentها بتوانند از Template برای پیش‌پر کردن فرم‌ها استفاده کنند.

---

## 🟣 EPIC 7 — Notifications & Alerts ✅ **71% تکمیل شده**

هدف: یکپارچه‌سازی سیستم اعلان‌ها برای ایمیل، SMS، Telegram، Web Push.

### Story EP7-S1 — Email Notifications Engine ✅ **انجام شده**

- ✅ پیاده‌سازی Email Service با پشتیبانی از SMTP
- ✅ ارسال ایمیل برای: ایجاد تیکت، تغییر وضعیت، تخصیص تیکت، افزودن کامنت، SLA
- ✅ 14 Template ایمیل HTML با پشتیبانی دو زبانه (فارسی/انگلیسی)
- ✅ پشتیبانی از فایل‌های پیوست، CC، BCC

### Story EP7-S2 — SMS Notifications ❌ **انجام نشده**

- ❌ SMS Gateway پیاده‌سازی نشده

### Story EP7-S3 — Telegram Alerts ✅ **انجام شده**

- ✅ ارسال نوتیفیکیشن تلگرام برای تمام رویدادهای تیکت
- ✅ یکپارچه‌سازی با Telegram Bot
- ✅ اعلان‌های SLA از طریق Telegram

### Story EP7-S4 — Web Push Notifications ❌ **انجام نشده**

- ❌ Web Push API پیاده‌سازی نشده

### Story EP7-S5 — SLA Alerts ✅ **انجام شده**

- ✅ ارسال هشدار SLA از طریق Email و Telegram
- ✅ یکپارچه‌سازی با SLA Scheduler
- ✅ اعلان Escalation

### Story EP7-S6 — Agent Assignment Alerts ✅ **انجام شده**

- ✅ ارسال نوتیفیکیشن برای تخصیص تیکت به Agent
- ✅ ارسال از طریق Email و Telegram

### Story EP7-S7 — مدیریت Templateهای اعلانات ⚠️ **بخشی انجام شده**

- ✅ Templateهای Email در کد موجود است
- ❌ Templateهای اعلانات قابل ویرایش از پنل ادمین نیستند

---

## 🟤 EPIC 8 — داشبورد مدیریتی (Admin & Management Dashboards) ✅ **100% تکمیل شده**

### Story EP8-S1 — داشبورد وضعیت تیکت‌ها ✅ **انجام شده**

- ✅ API `GET /api/reports/overview` برای آمار کلی تیکت‌ها
- ✅ API `GET /api/reports/by-status` برای تیکت‌ها بر اساس وضعیت
- ✅ API `GET /api/reports/by-priority` برای تیکت‌ها بر اساس اولویت
- ✅ API `GET /api/reports/by-branch` برای تیکت‌ها بر اساس شعبه
- ✅ API `GET /api/reports/by-department` برای تیکت‌ها بر اساس دپارتمان
- ✅ API `GET /api/reports/by-date` برای تیکت‌ها بر اساس تاریخ
- ✅ Dashboard در Frontend با نمودارهای Recharts

### Story EP8-S2 — داشبورد SLA ✅ **انجام شده**

- ✅ API `GET /api/reports/sla-compliance` برای گزارش SLA
- ✅ API `GET /api/reports/sla-by-priority` برای گزارش SLA بر اساس اولویت
- ✅ نمایش SLA Compliance در Dashboard
- ✅ نمایش SLA Logs در Frontend

### Story EP8-S3 — داشبورد حجم کاری Agents ✅ **انجام شده**

- ✅ گزارش عملکرد Agents در Reports API
- ✅ نمایش در Dashboard

### Story EP8-S4 — داشبورد مانیتورینگ زیرساخت ⚠️ **بخشی انجام شده**

- ✅ مدل `BranchInfrastructure` برای ثبت اطلاعات زیرساخت
- ✅ API `GET/POST/PUT/DELETE /api/branch-infrastructure`
- ❌ مانیتورینگ Real-time وجود ندارد

### Story EP8-S5 — گزارش مصرف پهنای باند شعبه‌ها ❌ **انجام نشده**

- ❌ گزارش مصرف پهنای باند وجود ندارد

### Story EP8-S6 — خروجی گزارش‌ها به Excel/PDF ✅ **انجام شده**

- ✅ Export به CSV از طریق API `GET /api/reports/export`
- ✅ Export به Excel از طریق API `GET /api/reports/export.xlsx`
- ✅ Export به PDF از طریق API `GET /api/reports/export-pdf`

### Story EP8-S7 — KPI Boxes (MTTR, MTTA, SLA Compliance, Open Incidents) ✅ **انجام شده**

- ✅ KPI Boxes در Dashboard Frontend
- ✅ نمایش آمار Real-time

---

## 🔵 EPIC 9 — سیستم تنظیمات (System Settings & Configuration) ✅ **86% تکمیل شده**

### Story EP9-S1 — مدیریت دسته‌بندی‌ها و اولویت‌ها ✅ **انجام شده**

- ✅ دسته‌بندی‌ها در Enum `TicketCategory` تعریف شده
- ✅ اولویت‌ها در Enum `TicketPriority` تعریف شده
- ✅ API برای مدیریت اولویت‌ها (`GET/POST/PUT/DELETE /api/priorities`)
- ✅ Frontend: صفحه مدیریت اولویت‌ها

### Story EP9-S2 — مدیریت شعب و واحدها ✅ **انجام شده**

- ✅ API `GET/POST/PUT/DELETE /api/branches` برای مدیریت شعب
- ✅ API `GET/POST/PUT/DELETE /api/departments` برای مدیریت دپارتمان‌ها
- ✅ Frontend: صفحات مدیریت شعب و دپارتمان‌ها

### Story EP9-S3 — تنظیمات SLA ✅ **انجام شده**

- ✅ API `GET/POST/PUT/DELETE /api/sla` برای مدیریت قوانین SLA
- ✅ Frontend: صفحه مدیریت SLA با نمایش Logs و Statistics

### Story EP9-S4 — تنظیمات بات تلگرام ✅ **انجام شده**

- ✅ تنظیمات Bot Token در Environment Variables
- ✅ تنظیمات Admin Group ID در Environment Variables
- ✅ API برای لینک تلگرام (`POST /api/auth/link-telegram`)
- ✅ Daily Report Scheduler برای ارسال گزارش روزانه

### Story EP9-S5 — تنظیمات Email/SMS Gateway ⚠️ **بخش Email انجام شده**

- ✅ تنظیمات Email (SMTP) در Environment Variables
- ✅ Frontend: صفحه Settings برای تنظیمات Email
- ❌ تنظیمات SMS Gateway وجود ندارد

### Story EP9-S6 — تنظیمات تم و UI ✅ **انجام شده**

- ✅ پشتیبانی از دو زبان (فارسی/انگلیسی) با i18n
- ✅ Dark Mode در Frontend
- ✅ تنظیم زبان کاربر در پروفایل
- ✅ Mobile Navigation

### Story EP9-S7 — Export/Import تنظیمات ❌ **انجام نشده**

- ❌ Export/Import تنظیمات وجود ندارد

---

## ⚫ EPIC 10 — زیرساخت، امنیت و DevOps ❌ **0% تکمیل شده**

### Story EP10-S1 — Dockerization و Multi-Stage Build ❌ **انجام نشده**

- ❌ Dockerfile وجود ندارد
- ❌ docker-compose.yml وجود ندارد

### Story EP10-S2 — Nginx Reverse Proxy و HTTPS ❌ **انجام نشده**

- ❌ پیکربندی Nginx وجود ندارد
- ❌ HTTPS تنظیم نشده

### Story EP10-S3 — Load Balancer و Scale افقی ❌ **انجام نشده**

- ❌ Load Balancer پیاده‌سازی نشده

### Story EP10-S4 — Backup Automation برای DB و فایل‌ها ❌ **انجام نشده**

- ❌ Backup Automation وجود ندارد

### Story EP10-S5 — Log Management ❌ **انجام نشده**

- ⚠️ Logging با Python logging موجود است
- ❌ ELK / Loki / Structured Logging پیاده‌سازی نشده

### Story EP10-S6 — Security Hardening ⚠️ **بخشی انجام شده**

- ✅ JWT برای Authentication
- ✅ CORS تنظیم شده
- ❌ Rate Limiting پیاده‌سازی نشده
- ⚠️ Security Headers محدود موجود است

### Story EP10-S7 — Audit Log و مانیتورینگ امنیتی ❌ **انجام نشده**

- ❌ Audit Log کامل وجود ندارد
- ❌ مانیتورینگ امنیتی پیاده‌سازی نشده

---

---

## 📋 خلاصه وضعیت Storyها

**آمار کلی:**
- ✅ **تکمیل شده:** 22 Story
- ⚠️ **بخشی انجام شده:** 5 Story
- ❌ **انجام نشده:** 23 Story

**Storyهای تکمیل‌شده (100%):**
- EP2-S1 تا EP2-S7: تمام Storyهای Helpdesk
- EP8-S1 تا EP8-S3, EP8-S6, EP8-S7: داشبورد
- EP9-S1 تا EP9-S6: تنظیمات (به جز Export/Import)

**Storyهای ناقص (0-50%):**
- EP1-S1, EP1-S5, EP1-S6, EP1-S7: Authentication
- EP3-S1 تا EP3-S7: Monitoring
- EP4-S1 تا EP4-S7: Asset Management
- EP5-S4 تا EP5-S7: Telegram Bot
- EP6-S1 تا EP6-S7: ITSM Processes
- EP7-S2, EP7-S4, EP7-S7: Notifications
- EP10-S1 تا EP10-S7: DevOps

---

## 🎁 قابلیت‌های اضافی پیاده‌سازی شده (فراتر از Backlog)

این قابلیت‌ها در Backlog اصلی نبوده‌اند اما پیاده‌سازی شده‌اند:

### ✅ Time Tracker (زمان‌سنج کار)
- ✅ مدل `TimeLog` برای ثبت زمان کار روی تیکت‌ها
- ✅ API `POST /api/time-tracker/start` برای شروع تایمر
- ✅ API `POST /api/time-tracker/stop-active` برای توقف تایمر
- ✅ API `GET /api/time-tracker/ticket/{id}` برای مشاهده لاگ‌های زمان
- ✅ API `GET /api/time-tracker/ticket/{id}/summary` برای خلاصه زمان
- ✅ Frontend: Time Tracker در TicketDetail

### ✅ Custom Fields (فیلدهای سفارشی)
- ✅ مدل `CustomField` و `TicketCustomFieldValue`
- ✅ 11 نوع فیلد: Text, Textarea, Number, Date, DateTime, Boolean, Select, MultiSelect, URL, Email, Phone
- ✅ API کامل برای مدیریت Custom Fields
- ✅ یکپارچه‌سازی با تیکت‌ها
- ✅ Frontend: صفحه مدیریت Custom Fields و کامپوننت رندر

### ✅ Knowledge Base (بانک دانش)
- ✅ مدل `KnowledgeArticle` برای مقالات
- ✅ API `GET/POST/PUT/DELETE /api/knowledge-base` برای مدیریت مقالات
- ✅ جستجو و پیشنهاد مقالات
- ✅ Frontend: کامپوننت `KnowledgeSuggestions` در فرم ایجاد تیکت

### ✅ Profile Onboarding
- ✅ API `POST /api/profile/onboarding` برای جمع‌آوری اطلاعات تکمیلی
- ✅ Frontend: کامپوننت `OnboardingWizard` با Multi-Step Form
- ✅ ذخیره وضعیت Onboarding در localStorage

### ✅ Notifications API
- ✅ API `GET /api/notifications` برای دریافت اعلان‌ها
- ✅ API `POST /api/notifications/mark-read` برای علامت‌گذاری به عنوان خوانده شده
- ✅ مدل `Notification` برای ذخیره اعلان‌ها
- ✅ Frontend: کامپوننت `NotificationBell` با dropdown

### ✅ Automation Rules
- ✅ مدل `AutomationRule` برای قوانین خودکار
- ✅ API `GET/POST/PUT/DELETE /api/automation` برای مدیریت قوانین
- ✅ Background Scheduler برای اجرای قوانین
- ✅ Frontend: صفحه مدیریت Automation

---

### نکات استفاده در Jira / GitHub

- در Jira:
  - برای هر **Epic** یک Issue از نوع Epic بساز و Stories مرتبط را با Keyهای `EPx-Sy` زیر آن قرار بده.
  - **Tasks** هر Story را می‌توانی به صورت Sub-task ثبت کنی.
- در GitHub:
  - برای هر Epic یک **Milestone** یا Label بساز (مثلاً `EPIC-1-Auth`).
  - هر Story یک Issue جدا با چک‌لیست Tasks و Acceptance Criteria باشد.

**تاریخ آخرین به‌روزرسانی:** 2025-01-26  
**نسخه:** 2.0


