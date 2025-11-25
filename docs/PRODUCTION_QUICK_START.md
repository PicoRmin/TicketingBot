# ⚡ راهنمای سریع استقرار Production

راهنمای سریع برای استقرار سیستم تیکتینگ ایرانمهر در Production.

## مراحل سریع

### 1. نصب وابستگی‌ها

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. راه‌اندازی خودکار

```bash
python scripts/setup_production.py
```

این اسکریپت:
- دایرکتوری‌های لازم را ایجاد می‌کند
- فایل `.env` را از `env.example` ایجاد می‌کند
- Secret Keys را تولید می‌کند
- تنظیمات Production را بررسی می‌کند

### 3. تنظیمات `.env`

فایل `.env` را ویرایش کنید و تنظیمات خود را اضافه کنید:

```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/ticketing_db
SECRET_KEY=YOUR_GENERATED_SECRET_KEY
# ... سایر تنظیمات
```

### 4. راه‌اندازی Database

```bash
# PostgreSQL
createdb ticketing_db
# یا
psql -c "CREATE DATABASE ticketing_db;"

# اجرای migrations
python scripts/init_db.py

# ایجاد کاربر ادمین
python scripts/create_admin.py
```

### 5. راه‌اندازی سرویس

#### Linux (systemd)

```bash
# کپی فایل service
sudo cp scripts/ticketing.service /etc/systemd/system/
sudo nano /etc/systemd/system/ticketing.service  # ویرایش مسیرها

# فعال‌سازی
sudo systemctl daemon-reload
sudo systemctl enable ticketing
sudo systemctl start ticketing
```

#### Windows

```cmd
# به عنوان Administrator
scripts\install_windows_service.bat
```

### 6. بررسی وضعیت

```bash
# Linux
sudo systemctl status ticketing
./scripts/check_production.sh

# Windows
nssm status TicketingService
```

### 7. تنظیم Backup

```bash
# Linux - اضافه کردن به crontab
crontab -e
# اضافه کردن:
0 2 * * * /path/to/imehrTicketing/scripts/backup.sh

# Windows - استفاده از Task Scheduler
# اجرای scripts\backup.bat هر روز ساعت 2 صبح
```

## بررسی نهایی

```bash
# Health Check
curl http://localhost:8000/health

# بررسی لاگ‌ها
tail -f logs/app.log
```

## مستندات کامل

برای جزئیات بیشتر، به [راهنمای کامل Production Setup](./PRODUCTION_SETUP.md) مراجعه کنید.

---

**آخرین به‌روزرسانی:** 2025-01-23

