## Phase 2 – User Experience, Onboarding & Knowledge

> هدف: ارتقای تجربه کاربری برای همه نقش‌ها، طراحی جریان‌های تعاملی onboarding و راه‌اندازی بانک دانش یکپارچه.

### 1. Mobile-first Navigation & UX
- طراحی Bottom Navigation ثابت برای نسخه موبایل (Home, Tickets, Monitoring, Notifications, Profile).
- استفاده از layout adaptive (CSS Grid/Flex + media queries) برای کارت‌ها و جدول‌ها.
- تعریف gestureهای سریع (swipe برای اقدام روی کارت، pull-to-refresh) و تست کاربری روی دستگاه‌های واقعی.
- اضافه‌کردن Progressive Web App (PWA) manifest و caching برای تجربه شبه‌اپلیکیشنی.

### 2. Interactive Onboarding Wizard
- ایجاد onboarding چندمرحله‌ای: معرفی سیستم، دریافت اطلاعات تکمیلی (سن، مهارت، اهداف)، پیشنهاد وظایف روزمره.
- استفاده از Tooltip و Coach Markها برای هدایت کاربر در UI (پورتال و پنل).
- ذخیره وضعیت onboarding در LocalStorage و سرور برای ادامه از همان مرحله و امکان Skip.
- تحلیل داده‌های onboarding برای پیشنهاد SLA یا نقش مناسب.

### 3. Knowledge Base Platform
- مدل داده: `kb_article` با فیلدهای عنوان، محتوا (Markdown/HTML)، تگ، سطح دسترسی، نسخه و وضعیت انتشار.
- API و UI CRUD برای نویسندگان، امکان پیش‌نویس، بازبینی و تاریخچه نسخه‌ها.
- موتور جستجوی full-text (PostgreSQL TSVECTOR یا Elasticsearch) با پیشنهاد خودکار.
- ادغام با User Portal، پنل کارشناس و ربات تلگرام: نمایش مقاله‌های مرتبط هنگام ایجاد تیکت یا پاسخ.
- ثبت feedback روی مقاله‌ها (Was this helpful?) و گزارش محبوب‌ترین محتوا.

### 4. Customer Portal Enhancements
- تاریخچه مشکلات با grouping بر اساس دسته/شعبه و timeline فشرده با وضعیت SLA.
- اعلان in-app و push (از طریق PWA) برای پاسخ، تغییر وضعیت، SLA warning و پیام ادمین.
- فرم ایجاد تیکت با فیلدهای دینامیک، پیشنهاد مقاله و امکان ذخیره Draft.
- ابزار تحلیل مشتری: export تیکت‌های شخصی، گزارش دوره‌ای به ایمیل یا PDF.

---

### خروجی‌های مورد انتظار این فاز
- تجربه کاربری سازگار با موبایل و onboarding هوشمند.
- بانک دانش با جستجوی پیشرفته، نسخه‌بندی و ادغام کامل در بسترهای وب و تلگرام.
- کاربران امکان دریافت پیشنهاد مقاله و اعلان‌های درون برنامه‌ای را خواهند داشت.

