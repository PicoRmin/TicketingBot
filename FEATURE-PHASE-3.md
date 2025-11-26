## Phase 3 – Network, Branch & Monitoring Intelligence

> هدف: ایجاد دید لحظه‌ای از وضعیت شبکه، VoIP، CCTV و زیرساخت شعب، و فراهم‌سازی ابزارهای عملیات از راه دور.

### 1. Real-time Monitoring Service
- طراحی microservice مستقل (FastAPI/WebSocket) که heartbeat شعب، latency و وضعیت تجهیزات را دریافت کند.
- انتخاب پایگاه‌داده سری زمانی (TimescaleDB یا InfluxDB) برای ذخیره کیفیت اینترنت، packet loss، jitter.
- ساخت Notification Engine که در صورت down بودن لینک یا افزایش latency، هشدار فوری صادر کند (تلگرام / push).
- داشبورد real-time در پنل مدیر سیستم با نمودارهای زنده و فیلتر شعبه/لینک.

### 2. VoIP & CCTV Dashboards
- جمع‌آوری وضعیت SIP Registration، MOS، Jitter، Packet Loss از مراکز تلفنی و ارائه KPIها در UI.
- مانیتورینگ NVR/Camera: وضعیت آنلاین/آفلاین، snapshot روزانه، هشدار ورود غیرمجاز یا قطع دوربین.
- اتصال داده‌ها به تیکتینگ برای ایجاد خودکار تیکت هنگام وقوع خرابی VoIP/CCTV بر اساس policy.

### 3. Branch Network Maps & Documentation
- تولید اتوماتیک نقشه topology هر شعبه (Graphviz/vis.js) از داده‌های `BranchInfrastructure`.
- نمایش IP/VLAN، مسیرهای ارتباطی، کیفیت لینک و وابستگی سرویس‌ها در صفحه جزئیات شعبه.
- امکان دانلود PDF/PNG نقشه شبکه و پیوست آن به مستندات داخلی.
- افزودن بخش «Network Logs» برای ثبت تغییرات و رخدادهای مرتبط با شعبه.

### 4. Automation Scripts & Remote Ops
- سیستم Remote Script Execution با sandbox، role-based approval و audit trail.
- Firmware Checker دوره‌ای برای تجهیزات حیاتی و گزارش نسخه‌های معوق.
- Asset Discovery برای کشف خودکار دستگاه‌های جدید و همگام‌سازی با موجودی.
- Sync فایل‌های مهم (config, backup) بین شعب و مرکز، همراه با هشدار شکست یا تغییر فایل.

---

### خروجی‌های مورد انتظار این فاز
- دید بلادرنگ از اینترنت، VoIP و CCTV تمام شعب.
- نقشه شبکه تعاملی برای هر شعبه و امکان اجرای عملیات از راه دور با امنیت کامل.
- اتصال مانیتورینگ به جریان تیکت برای ایجاد خودکار تیکت و اولویت‌بندی هوشمند.

