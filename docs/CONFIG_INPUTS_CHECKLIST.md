# ✅ Iranmehr Ticketing – Config & Inputs Checklist

این فایل برای جمع‌آوری تمام ورودی‌هایی است که در مراحل آینده از کارفرما لازم داریم. پس از نهایی‌سازی هر مورد، مقدار در ستون «وضعیت/مقدار» ثبت می‌شود تا در انتهای پروژه همه تنظیمات یک‌جا آماده باشند.

| ردیف | دسته | توضیح | وضعیت / مقدار |
| --- | --- | --- | --- |
| 1 | دامنه و DNS | دامنه‌های اصلی (api/admin/portal) + رکوردهای موردنیاز (A, CNAME) | _(پر شود)_ |
| 2 | SSL / Let’s Encrypt | ایمیل تماس Let’s Encrypt، مسیر گواهی، سیاست تمدید و Challenge Path | _(پر شود)_ |
| 3 | Reverse Proxy & Nginx | سرور مقصد، سیستم‌عامل، کاربر service، محدودیت دسترسی، مسیر static | _(پر شود)_ |
| 4 | CI/CD Pipeline | مخزن مبدا، شاخه‌های هدف، محیط‌های Deployment، دسترسی Runner/Actions | _(پر شود)_ |
| 5 | CI/CD Secrets | توکن GitHub/GitLab، SSH key، ENV secrets (DATABASE_URL, SMTP, TELEGRAM) | _(پر شود)_ |
| 6 | سرور Production | IP/Hostname، دسترسی SSH/RDP، سیستم‌عامل، سیاست Backup | _(پر شود)_ |
| 7 | پایگاه‌داده | نوع (PostgreSQL/...), نسخه، اطلاعات اتصال، سیاست High Availability | _(پر شود)_ |
| 8 | SMTP/Email | سرویس‌دهنده، پورت، SSL/TLS، کاربر/رمز، Reply-To، BCC، DMARC/DKIM | _(پر شود)_ |
| 9 | Telegram Bot | توکن، webhook URL، سیاست امنیتی، Allowed updates | _(پر شود)_ |
|10 | Notification Channels | Slack/Microsoft Teams/Webhook URLهای خارجی، آستانه ارسال | _(پر شود)_ |
|11 | Knowledge Base | ساختار مقالات، زبان‌ها، نقش‌های دسترسی، دسته‌بندی پیش‌فرض | _(پر شود)_ |
|12 | Real-time/Webhook | URL مقصد مشتریان، امضا/secret، سیاست Retry/Dead-letter | _(پر شود)_ |
|13 | CRM Integration | سیستم هدف (Dynamics/Zoho/...)، API keys، محدوده داده و mapping | _(پر شود)_ |
|14 | Performance Targets | تعداد کاربر همزمان، حداکثر تیکت روزانه، SLA پاسخ/حل | _(پر شود)_ |
|15 | Security Policies | نیازمندی 2FA، الزامات Audit Logging، سیاست چرخش رمز و Least Privilege | _(پر شود)_ |
|16 | Redis / Cache | آیا Redis نیاز است؟ دسترسی، آدرس، احراز هویت، استفاده برای Session/Rate Limit | _(پر شود)_ |
|17 | Monitoring Stack | ابزار انتخابی (Prometheus/Grafana/ELK)، alert channels، retention | _(پر شود)_ |
|18 | Backup & DR | مقصد نهایی Backup (S3/NAS)، retention اضافه، فرکانس تست بازیابی | _(پر شود)_ |
|19 | Documentation & Training | فرمت خروجی، زبان ترجیحی، سبک ویدیوها، کانال انتشار | _(پر شود)_ |

> در طول اجرای هر مرحله، هر مقدار جدید بلافاصله در این جدول ثبت و پس از تأیید علامت‌گذاری می‌شود.

