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

## 🔵 EPIC 1 — سیستم احراز هویت و مدیریت کاربران (Authentication & Authorization)

هدف: پیاده‌سازی یک سیستم امن برای ثبت‌نام، لاگین، مدیریت نقش‌ها و پروفایل کاربران.

### Story EP1-S1 — ثبت‌نام کاربر جدید با ایمیل/موبایل

**As a** new user  
**I want to** register with email or mobile  
**So that I can** access the system securely

- **Tasks**
  - **Task 1**: طراحی API `POST /auth/register` با FastAPI
  - **Task 2**: تعریف مدل دیتابیس `User` با فیلدهای: `id`, `full_name`, `email`, `mobile`, `password_hash`, `role`, `is_active`
  - **Task 3**: اعتبارسنجی ورودی‌ها (ایمیل معتبر، حداقل طول پسورد، یکتا بودن ایمیل و موبایل)
  - **Task 4**: ارسال کد تأیید (ایمیل یا SMS – بسته به تنظیمات)
  - **Task 5**: ذخیره لاگ ثبت‌نام در جدول `audit_logs`
  - **Task 6**: تست واحد و تست یکپارچه برای سناریوهای ثبت‌نام موفق/ناموفق

- **Acceptance Criteria**
  - کاربر بتواند با **ایمیل یا موبایل** ثبت‌نام کند.
  - اگر ایمیل یا موبایل تکراری باشد، **پیام خطای واضح** بازگردانده شود.
  - پس از ثبت‌نام، **کد تأیید** ارسال شود (یا فلگ فعال‌سازی در محیط توسعه شبیه‌سازی شود).
  - اگر فعال‌سازی اجباری است، تا قبل از فعال‌سازی، کاربر نتواند لاگین کند.
  - تمام درخواست‌ها در جدول لاگ ذخیره شوند (IP, User Agent, زمان).

---

### Story EP1-S2 — ورود کاربر (Login با JWT)

**As a** registered user  
**I want to** log in using my email/mobile and password  
**So that I can** access protected resources

- **Tasks**
  - **Task 1**: طراحی API `POST /auth/login` با بازگشت `access_token` و `refresh_token`
  - **Task 2**: استفاده از JWT با `HS256` و کلید مخفی از `.env`
  - **Task 3**: پیاده‌سازی Rate Limiting روی لاگین (مثلاً ۵ تلاش در ۱۵ دقیقه)
  - **Task 4**: ذخیره Refresh Token در جدول `refresh_tokens` با تاریخ انقضا
  - **Task 5**: پیاده‌سازی endpoint `POST /auth/refresh` برای دریافت توکن جدید
  - **Task 6**: تست سناریوهای پسورد اشتباه، کاربر غیرفعال، حساب قفل شده

- **Acceptance Criteria**
  - ورود با **ایمیل/رمز عبور** و یا **موبایل/رمز عبور** امکان‌پذیر باشد (بر اساس تنظیمات).
  - در صورت نامعتبر بودن اطلاعات، پیام خطای استاندارد برگردد (بدون فاش کردن اینکه ایمیل/کاربر وجود دارد یا نه).
  - در صورت موفقیت، **JWT Access Token** و **Refresh Token** بازگردانده شود.
  - پس از چند تلاش ناموفق متوالی، حساب به صورت موقت قفل شود (قابل تنظیم).
  - تمام تلاش‌های ورود لاگ شوند (موفق/ناموفق).

---

### Story EP1-S3 — مدیریت نقش‌ها و دسترسی‌ها (RBAC)

**As an** Admin  
**I want to** define roles and permissions  
**So that I can** control what each user can access

- **Tasks**
  - **Task 1**: طراحی مدل Role/Permission (`Role`, `Permission`, `user_roles`)
  - **Task 2**: تعریف نقش‌های پیش‌فرض: `Admin`, `IT Manager`, `Agent`, `Branch User`, `ReadOnly`
  - **Task 3**: پیاده‌سازی Dependency در FastAPI برای کنترل دسترسی (`get_current_user_with_roles`)
  - **Task 4**: پیاده‌سازی endpointهای مدیریت نقش‌ها: `GET/POST/PUT/DELETE /admin/roles`
  - **Task 5**: افزودن Middleware برای ثبت لاگ دسترسی‌های رد شده (403)

- **Acceptance Criteria**
  - فقط **Admin** بتواند نقش جدید ایجاد یا ویرایش کند.
  - کاربران با نقش `Agent` فقط **تیکت‌های تخصیص داده شده به خود** یا تیکت‌های شعبه خود (بر اساس تنظیمات) را ببینند.
  - `Branch Manager` فقط تیکت‌های **شعبه خودش** را ببیند.
  - اگر کاربری مجوز دسترسی نداشته باشد، API باید **کد 403** و پیام مناسب برگرداند.

---

### Story EP1-S4 — مدیریت پروفایل کاربری

**As a** user  
**I want to** view and update my profile  
**So that I can** keep my information up-to-date

- **Tasks**
  - **Task 1**: API `GET /me` برای دریافت اطلاعات پروفایل
  - **Task 2**: API `PUT /me` برای ویرایش نام، موبایل، زبان، تصویر پروفایل
  - **Task 3**: امکان تغییر پسورد با API `POST /me/change-password`
  - **Task 4**: اعتبارسنجی قوی پسورد (طول، حروف بزرگ/کوچک، عدد)
  - **Task 5**: تست‌های واحد و یکپارچه

- **Acceptance Criteria**
  - کاربر بتواند **نام، موبایل، زبان رابط کاربری** را ویرایش کند.
  - برای تغییر پسورد، وارد کردن پسورد فعلی الزامی باشد.
  - تاریخ آخرین تغییر پسورد ذخیره شود.

---

### Story EP1-S5 — بازیابی رمز عبور (Password Reset)

**As a** user who forgot the password  
**I want to** reset my password securely  
**So that I can** regain access

- **Tasks**
  - **Task 1**: API `POST /auth/forgot-password` برای ارسال لینک/کد بازیابی
  - **Task 2**: ذخیره Token بازیابی در جدول `password_resets` با انقضا
  - **Task 3**: API `POST /auth/reset-password` برای تنظیم پسورد جدید
  - **Task 4**: بی‌اعتبار کردن تمام سشن‌ها و توکن‌های قبلی پس از ریست پسورد

- **Acceptance Criteria**
  - توکن بازیابی فقط یک‌بار قابل استفاده باشد و پس از استفاده منقضی شود.
  - اگر توکن منقضی یا نامعتبر باشد، پیام خطای واضح بازگردد.
  - پس از ریست پسورد، کاربر مجبور به لاگین مجدد باشد.

---

### Story EP1-S6 — Audit Log و ردیابی فعالیت‌ها

**As an** IT Security Officer  
**I want to** see an audit trail of important actions  
**So that I can** investigate security or misuse

- **Tasks**
  - **Task 1**: طراحی جدول `audit_logs` (user_id, action, resource_type, resource_id, ip, user_agent, created_at)
  - **Task 2**: ثبت رویدادهای کلیدی: لاگین، لاگ‌آوت، ثبت‌نام، ایجاد/ویرایش/حذف تیکت، تغییر نقش، تغییر تنظیمات
  - **Task 3**: API `GET /admin/audit-logs` با فیلتر تاریخ، کاربر، نوع اکشن

- **Acceptance Criteria**
  - تمام رویدادهای حساس در Audit Log ثبت شوند.
  - فیلتر بر اساس بازه زمانی، کاربر، نوع عملیات قابل انجام باشد.

---

### Story EP1-S7 — تنظیمات امنیتی (Password Policy, Session Policy)

**As an** Admin  
**I want to** configure security policies  
**So that I can** comply with company requirements

- **Tasks**
  - **Task 1**: تنظیمات حداقل پیچیدگی پسورد (قابل تنظیم در UI/Config)
  - **Task 2**: تنظیم زمان انقضای Session/Token
  - **Task 3**: امکان Force Logout همه کاربران (در صورت رخداد امنیتی)

- **Acceptance Criteria**
  - سیاست‌های امنیتی در دیتابیس یا فایل تنظیمات ذخیره شوند.
  - تغییر سیاست‌ها بلافاصله روی لاگین‌ها/سشن‌های جدید اعمال شود.

---

## 🟣 EPIC 2 — سیستم Helpdesk و مدیریت تیکت‌ها

هدف: مدیریت کامل چرخه حیات تیکت‌ها از ایجاد تا بستن، همراه با SLA و کامنت و فایل.

### Story EP2-S1 — ایجاد تیکت (Ticket Creation)

**As an** end user (Branch User / Employee)  
**I want to** create a support ticket  
**So that I can** get help for my IT issues

- **Tasks**
  - **Task 1**: API `POST /tickets` برای ایجاد تیکت
  - **Task 2**: فیلدها: `title`, `description`, `category`, `priority`, `branch_id`, `department_id`, `attachments`
  - **Task 3**: تعیین SLA بر اساس Priority و یا Ruleهای SLA
  - **Task 4**: ثبت `created_at`, `sla_due_at`, `status = NEW`

- **Acceptance Criteria**
  - `title` و `category` و `priority` فیلدهای اجباری باشند.
  - پس از ایجاد، شماره تیکت یکتا (`TCK-YYYY-XXXX`) تولید شود.
  - SLA Deadline بر اساس قوانین SLA محاسبه و ذخیره شود.

---

### Story EP2-S2 — لیست و فیلتر تیکت‌ها

**As an** Agent / Admin  
**I want to** list and filter tickets  
**So that I can** manage workload efficiently

- **Tasks**
  - **Task 1**: API `GET /tickets` با فیلتر: `status`, `branch`, `agent`, `priority`, `category`, `created_from/to`
  - **Task 2**: پیاده‌سازی Pagination (پارامترهای `page`, `page_size`)
  - **Task 3**: امکان Sort بر اساس `created_at`, `priority`, `sla_due_at`

- **Acceptance Criteria**
  - لیست پیش‌فرض حداکثر ۲۰ تیکت در هر صفحه (قابل تنظیم).
  - اگر تیکتی وجود نداشته باشد، پیام **"تیکتی یافت نشد"** برگردد.
  - فیلترها و Sorting هم‌زمان قابل استفاده باشند.

---

### Story EP2-S3 — جزئیات تیکت و تاریخچه

**As an** Agent  
**I want to** see full ticket details  
**So that I can** understand the context and history

- **Tasks**
  - **Task 1**: API `GET /tickets/{id}` با تمام جزئیات
  - **Task 2**: نمایش تاریخچه پیام‌ها، تغییر وضعیت‌ها، تغییر Agent، پیوست‌ها
  - **Task 3**: طراحی مدل `ticket_history` برای ذخیره Event Log

- **Acceptance Criteria**
  - تمام تغییرات تیکت در `ticket_history` قابل مشاهده باشد.
  - امکان مشاهده رویدادها به ترتیب زمانی (جدیدترین در بالا یا پایین – قابل تنظیم).
  - فایل‌های ضمیمه لینک دانلود امن داشته باشند.

---

### Story EP2-S4 — پاسخ به تیکت و کامنت‌ها

**As an** Agent  
**I want to** reply to tickets and add internal notes  
**So that I can** communicate with users and the team

- **Tasks**
  - **Task 1**: API `POST /tickets/{id}/comments` با نوع `public` یا `internal`
  - **Task 2**: ثبت Event برای هر پاسخ در تاریخچه
  - **Task 3**: ارسال نوتیفیکیشن (ایمیل/تلگرام) به کاربر در صورت پاسخ `public`

- **Acceptance Criteria**
  - Agent بتواند پاسخ عمومی برای کاربر ثبت کند.
  - Agent بتواند کامنت داخلی فقط قابل مشاهده برای تیم پشتیبانی ثبت کند.
  - پس از پاسخ، وضعیت تیکت در صورت نیاز به **"IN_PROGRESS"** تغییر کند (قابل تنظیم).

---

### Story EP2-S5 — تغییر وضعیت تیکت و بستن تیکت

**As an** Agent / User  
**I want to** change ticket status  
**So that I can** reflect the real state of the request

- **Tasks**
  - **Task 1**: تعریف Statusها: `NEW`, `IN_PROGRESS`, `PENDING`, `RESOLVED`, `CLOSED`, `CANCELLED`
  - **Task 2**: API `POST /tickets/{id}/status` با ثبت علت تغییر (اختیاری/اجباری)
  - **Task 3**: ثبت `resolved_at` و `closed_at` در صورت تغییر مناسب

- **Acceptance Criteria**
  - کاربر بتواند تیکت خود را در حالت‌های مجاز ببندد (مثلاً از `RESOLVED` → `CLOSED`).
  - Agent نتواند تیکت را بدون ثبت علت مشخص از `IN_PROGRESS` به `CANCELLED` ببرد (در صورت سیاست).
  - تاریخ و کاربر تغییر دهنده در تاریخچه ذخیره شوند.

---

### Story EP2-S6 — SLA Management برای تیکت‌ها

**As an** IT Manager  
**I want to** configure and track SLA rules  
**So that I can** ensure timely resolution of tickets

- **Tasks**
  - **Task 1**: طراحی جداول `sla_rules`, `sla_logs`
  - **Task 2**: تعیین زمان پاسخ اولیه و زمان حل بر اساس Priority و Category
  - **Task 3**: Scheduler برای بررسی SLA هر X دقیقه
  - **Task 4**: ثبت هشدار SLA و Breach در `sla_logs` و ارسال نوتیفیکیشن

- **Acceptance Criteria**
  - برای هر تیکت، SLA هدف در لحظه ایجاد محاسبه و ذخیره شود.
  - قبل از نزدیک‌شدن به Deadline، هشدار برای Agent/Manager ارسال شود.
  - در صورت Breach، در گزارش SLA قابل مشاهده باشد.

---

### Story EP2-S7 — پیوست فایل به تیکت

**As a** user/agent  
**I want to** attach files to tickets  
**So that I can** provide more context (screenshots, logs)

- **Tasks**
  - **Task 1**: API `POST /tickets/{id}/attachments` با محدودیت حجم و نوع فایل
  - **Task 2**: ذخیره فایل‌ها در پوشه امن یا Storage Service، ثبت متادیتا در DB
  - **Task 3**: بررسی امنیتی (Scan ساده، جلوگیری از اجرای مستقیم)
  - **Task 4**: لینک دانلود امن با دسترسی کنترل شده

- **Acceptance Criteria**
  - فقط کاربران مجاز به تیکت بتوانند پیوست‌ها را دانلود کنند.
  - حداکثر حجم و نوع فایل‌ها از طریق تنظیمات قابل کنترل باشد.

---

## 🟢 EPIC 3 — سیستم مانیتورینگ شبکه و سرورها (Monitoring & Networking)

هدف: پایش مداوم وضعیت سرورها، روترها، سرویس‌ها و لینک‌های شبکه.

### Story EP3-S1 — Agent سبک برای کلاینت‌ها/سرورها

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

### Story EP3-S2 — مانیتورینگ روترها و سوئیچ‌ها (Mikrotik / Cisco)

**As a** Network Engineer  
**I want to** monitor routers and switches  
**So that I can** detect link or bandwidth issues

- **Tasks**
  - **Task 1**: تعریف موجودیت `NetworkDevice` (آدرس IP، نوع دستگاه، API/SSH/SNMP)
  - **Task 2**: پیاده‌سازی ماژول جمع‌آوری متریک (Ping, Interface Traffic)
  - **Task 3**: Scheduler برای Poll کردن دستگاه‌ها

- **Acceptance Criteria**
  - برای هر دستگاه، وضعیت Reachability (Up/Down) ثبت شود.
  - ترافیک Interfaceهای کلیدی در دیتابیس ذخیره و قابل نمایش در داشبورد باشد.
  - در صورت Down شدن لینک، Alert تولید شود.

---

### Story EP3-S3 — Check سرویس‌ها (HTTP/TCP/Port Check)

**As an** IT Manager  
**I want to** monitor critical services  
**So that I can** react quickly if they go down

- **Tasks**
  - **Task 1**: تعریف جدول `service_checks` با نوع: HTTP, TCP, ICMP
  - **Task 2**: پیاده‌سازی Worker برای اجرای دوره‌ای Checkها
  - **Task 3**: ذخیره نتایج در جدول `service_check_results` (status, latency)
  - **Task 4**: تولید Alert در صورت شکست متوالی چند چک

- **Acceptance Criteria**
  - اگر API یا سرویس Down باشد، Alert ایجاد شود (Notification + ثبت در DB).
  - اگر latency از Threshold عبور کند، هشدار سطح پایین‌تر ثبت شود.

---

### Story EP3-S4 — داشبورد گراف‌ها و متریک‌ها

**As an** operations team  
**I want to** see metrics dashboards  
**So that I can** understand system health at a glance

- **Tasks**
  - **Task 1**: طراحی APIهای Read برای گرفتن متریک‌ها در بازه زمانی (`from`, `to`, `group_by`)
  - **Task 2**: پیاده‌سازی نمودارهای: CPU, RAM, Disk, Network, Uptime, Packet Loss
  - **Task 3**: امکان انتخاب بازه‌های زمانی ۲۴ساعته، ۷روزه، ۳۰روزه

- **Acceptance Criteria**
  - داشبورد Real-time با رفرش خودکار (مثلاً هر ۳۰ ثانیه).
  - مشاهده روند متریک‌ها در دوره‌های مختلف امکان‌پذیر باشد.

---

### Story EP3-S5 — Threshold & Alert Rules برای مانیتورینگ

**As an** IT Manager  
**I want to** define alert rules  
**So that I can** receive notifications only when necessary

- **Tasks**
  - **Task 1**: ایجاد جدول `monitoring_rules` (متریک، Threshold، مدت زمان، نوع Alert)
  - **Task 2**: پیاده‌سازی موتور ارزیابی Ruleها روی متریک‌های جمع‌آوری‌شده
  - **Task 3**: اتصال این Ruleها به سیستم Notifications (Email/Telegram)

- **Acceptance Criteria**
  - Ruleها بتوانند مبتنی بر درصد (مثلاً CPU > ۸۰٪ برای ۵ دقیقه) تعریف شوند.
  - Alertهای تکراری برای همان وضعیت Deduplicate شوند (تولید نشدن اسپم).

---

### Story EP3-S6 — مشاهده وضعیت شعب (Branch Health Overview)

**As a** Regional Manager  
**I want to** see branch connectivity status  
**So that I can** react to branch outages

- **Tasks**
  - **Task 1**: تعریف ارتباط بین Branch و Network Devices/Links
  - **Task 2**: صفحه داشبورد خلاصه وضعیت هر شعبه (Up/Down, Latency, Bandwidth)

- **Acceptance Criteria**
  - هر شعبه یک وضعیت کلی (Healthy/Degraded/Down) داشته باشد.
  - شاخص‌ها بر اساس آخرین متریک‌های دریافتی محاسبه شوند.

---

### Story EP3-S7 — گزارش تاریخچه رویدادهای مانیتورینگ

**As an** ITSM Manager  
**I want to** review monitoring events history  
**So that I can** correlate incidents with infrastructure issues

- **Tasks**
  - **Task 1**: ذخیره Events مهم (Up/Down, Threshold Breach) در جدول `monitoring_events`
  - **Task 2**: API برای فیلتر تاریخ، دستگاه، نوع رویداد

- **Acceptance Criteria**
  - امکان مشاهده تاریخچه قطع و وصل شدن لینک‌ها و سرویس‌ها وجود داشته باشد.
  - Events قابل لینک شدن به Incidentها باشند.

---

## 🟡 EPIC 4 — Asset Management و مدیریت دارایی‌ها

هدف: ثبت، ردیابی و مدیریت چرخه عمر دارایی‌های IT.

### Story EP4-S1 — ثبت دارایی‌های IT

**As an** Asset Manager  
**I want to** register IT assets  
**So that I can** track hardware and ownership

- **Tasks**
  - **Task 1**: طراحی مدل `Asset` با فیلدها: نوع، مدل، سریال، تاریخ خرید، شعبه، وضعیت، مالک
  - **Task 2**: API `POST /assets` و `GET /assets`

- **Acceptance Criteria**
  - امکان ثبت انواع تجهیزات: PC, Laptop, Router, Switch, TV, Printer و …
  - سریال و مدل و تاریخ خرید فیلدهای اجباری باشد.

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

## 🟠 EPIC 5 — Telegram Bot Integration

هدف: اتصال کامل سیستم Helpdesk/Monitoring/Asset به بات تلگرام.

### Story EP5-S1 — ساخت بات تلگرام و اتصال حساب کاربری

**As a** system user  
**I want to** link my Telegram account  
**So that I can** receive notifications and interact via bot

- **Tasks**
  - **Task 1**: تنظیم Bot Token در تنظیمات سیستم
  - **Task 2**: پیاده‌سازی `/start` برای ایجاد/لینک حساب تلگرام به کاربر
  - **Task 3**: ذخیره `telegram_chat_id` در پروفایل کاربر

- **Acceptance Criteria**
  - کاربر با ارسال `/start` بتواند حساب خود را لینک کند (با یک کد یکبارمصرف یا لینک).

---

### Story EP5-S2 — نوتیفیکیشن تیکت‌ها در تلگرام

**As an** Agent/User  
**I want to** receive ticket notifications on Telegram  
**So that I can** respond faster

- **Tasks**
  - **Task 1**: تعریف Event Handler برای: ایجاد تیکت, تغییر وضعیت, پاسخ جدید
  - **Task 2**: ارسال پیام تلگرام با جزئیات حداقلی + لینک به پنل وب

- **Acceptance Criteria**
  - ایجاد تیکت → پیام برای Agent/Queue مرتبط ارسال شود.
  - پاسخ Agent → پیام برای کاربر ارسال شود.
  - SLA Breach → پیام هشدار برای IT Manager/Agent مسئول ارسال شود.

---

### Story EP5-S3 — منوی اینلاین برای مدیریت تیکت‌ها

**As an** Agent  
**I want to** interact with tickets via Telegram menus  
**So that I can** quickly view and update basic info

- **Tasks**
  - **Task 1**: پیاده‌سازی منوی اینلاین برای: لیست تیکت‌های باز، جزئیات تیکت، تغییر وضعیت ساده
  - **Task 2**: پیاده‌سازی ConversationHandler برای سناریوی ایجاد تیکت ساده از داخل تلگرام

- **Acceptance Criteria**
  - UX ساده و قابل فهم، بدون نیاز به تایپ زیاد.
  - جلوگیری از خطا در Stateهای Conversation.

---

### Story EP5-S4 — مشاهده وضعیت مانیتورینگ شعب در بات

**As a** Branch Manager  
**I want to** see my branch monitoring status in Telegram  
**So that I can** quickly check health

- **Tasks**
  - **Task 1**: فرمان `"/branch_status"` و منوی انتخاب شعبه
  - **Task 2**: نمایش خلاصه: لینک‌ها Up/Down، Latency، هشدارهای اخیر

- **Acceptance Criteria**
  - برای هر شعبه وضعیت کلی به صورت خلاصه متنی نمایش داده شود.

---

### Story EP5-S5 — مشاهده دارایی‌های شعبه در بات

**As a** Branch IT responsible  
**I want to** list my branch assets via bot  
**So that I can** see inventory quickly

- **Tasks**
  - **Task 1**: فرمان `"/assets"` و فیلتر بر اساس شعبه کاربر

- **Acceptance Criteria**
  - فقط دارایی‌های مرتبط با شعبه کاربر نمایش داده شوند.

---

### Story EP5-S6 — اعلان‌های مانیتورینگ از طریق بات

**As an** on-call engineer  
**I want to** receive monitoring alerts on Telegram  
**So that I can** respond quickly to incidents

- **Tasks**
  - **Task 1**: اتصال موتور Alert مانیتورینگ به Bot

- **Acceptance Criteria**
  - هنگام Down شدن سرویس/لینک، پیام هشدار با سطح Severity مناسب ارسال شود.

---

### Story EP5-S7 — تنظیم سطوح اعلان تلگرام در پروفایل

**As a** user  
**I want to** configure my Telegram notification level  
**So that I can** avoid spam and focus on critical alerts

- **Tasks**
  - **Task 1**: افزودن تنظیمات سطح اعلان (Only Critical / All / None)

- **Acceptance Criteria**
  - فقط اعلان‌های مطابق با سطح تنظیم‌شده برای هر کاربر ارسال شوند.

---

## 🔴 EPIC 6 — ITSM Processes (Incident, Problem, Change)

هدف: پیاده‌سازی فرآیندهای اصلی ITSM روی Helpdesk.

### Story EP6-S1 — Incident Management

**As an** IT Support Agent  
**I want to** register and manage incidents  
**So that I can** restore normal service ASAP

- **Tasks**
  - **Task 1**: تعریف نوع تیکت Incident و فیلدهای Impact, Urgency, Severity
  - **Task 2**: ارتباط Incident با Asset و Service

- **Acceptance Criteria**
  - Impact/Severity در گزارش‌ها قابل فیلتر باشد.

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

## 🟣 EPIC 7 — Notifications & Alerts

هدف: یکپارچه‌سازی سیستم اعلان‌ها برای ایمیل، SMS، Telegram، Web Push.

### Story EP7-S1 — Email Notifications Engine

### Story EP7-S2 — SMS Notifications (در صورت موجود بودن Gateway)

### Story EP7-S3 — Telegram Alerts (اتصال به EP5)

### Story EP7-S4 — Web Push Notifications

### Story EP7-S5 — SLA Alerts (اتصال به EP2/EP3)

### Story EP7-S6 — Agent Assignment Alerts

### Story EP7-S7 — مدیریت Templateهای اعلانات

> برای هر Story در این Epic:
> - **Tasks** شامل: تعریف Template، متغیرهای داینامیک، اتصال به Eventها، تست ارسال
> - **Acceptance Criteria**: ثبت تمام نوتیفیکیشن‌ها در لاگ، امکان فعال/غیرفعال کردن نوع اعلان برای هر کاربر

---

## 🟤 EPIC 8 — داشبورد مدیریتی (Admin & Management Dashboards)

### Story EP8-S1 — داشبورد وضعیت تیکت‌ها

### Story EP8-S2 — داشبورد SLA

### Story EP8-S3 — داشبورد حجم کاری Agents

### Story EP8-S4 — داشبورد مانیتورینگ زیرساخت

### Story EP8-S5 — گزارش مصرف پهنای باند شعبه‌ها

### Story EP8-S6 — خروجی گزارش‌ها به Excel/PDF

### Story EP8-S7 — KPI Boxes (MTTR, MTTA, SLA Compliance, Open Incidents)

> برای همه Storyهای این Epic:
> - **Tasks**: طراحی API گزارش‌ها، تجمیع داده، طراحی UI Widgetها
> - **Acceptance Criteria**: فیلتر تاریخ، فیلتر شعبه، واکنش‌گرا بودن داشبورد، به‌روزرسانی قابل‌قبول (مثلاً هر ۱ دقیقه)

---

## 🔵 EPIC 9 — سیستم تنظیمات (System Settings & Configuration)

### Story EP9-S1 — مدیریت دسته‌بندی‌ها و اولویت‌ها

### Story EP9-S2 — مدیریت شعب و واحدها

### Story EP9-S3 — تنظیمات SLA

### Story EP9-S4 — تنظیمات بات تلگرام (Token, Admin Group, Notification Levels)

### Story EP9-S5 — تنظیمات Email/SMS Gateway

### Story EP9-S6 — تنظیمات تم و UI (Theme, Language)

### Story EP9-S7 — Export/Import تنظیمات

> هر Story شامل:
> - **Tasks**: CRUD صفحه تنظیمات، اعتبارسنجی، ذخیره در DB/Config
> - **Acceptance Criteria**: تغییر تنظیمات بدون نیاز به Downtime (تا حد امکان)، ثبت در Audit Log

---

## ⚫ EPIC 10 — زیرساخت، امنیت و DevOps

### Story EP10-S1 — Dockerization و Multi-Stage Build

### Story EP10-S2 — Nginx Reverse Proxy و HTTPS

### Story EP10-S3 — Load Balancer و Scale افقی

### Story EP10-S4 — Backup Automation برای DB و فایل‌ها

### Story EP10-S5 — Log Management (ELK / Loki / Structured Logging)

### Story EP10-S6 — Security Hardening (JWT, Rate Limiting, CORS, Headers)

### Story EP10-S7 — Audit Log و مانیتورینگ امنیتی

> برای تمامی Storyهای این Epic:
> - **Tasks**: نوشتن Dockerfile، تنظیم CI/CD، اضافه کردن Health Check، پیکربندی Nginx، تنظیم Backup Job
> - **Acceptance Criteria**: تمام APIها پشت HTTPS، نیاز به JWT، Rate Limit فعال، لاگ کامل هر اکشن مهم.

---

### نکات استفاده در Jira / GitHub

- در Jira:
  - برای هر **Epic** یک Issue از نوع Epic بساز و Stories مرتبط را با Keyهای `EPx-Sy` زیر آن قرار بده.
  - **Tasks** هر Story را می‌توانی به صورت Sub-task ثبت کنی.
- در GitHub:
  - برای هر Epic یک **Milestone** یا Label بساز (مثلاً `EPIC-1-Auth`).
  - هر Story یک Issue جدا با چک‌لیست Tasks و Acceptance Criteria باشد.


