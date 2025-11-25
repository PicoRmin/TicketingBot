# 🚀 راهنمای کامل استقرار Production - سیستم تیکتینگ ایرانمهر

## فهرست مطالب
1. [معرفی](#معرفی)
2. [پیش‌نیازها](#پیش‌نیازها)
3. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
4. [تنظیمات امنیتی](#تنظیمات-امنیتی)
5. [تنظیمات Database](#تنظیمات-database)
6. [تنظیمات Web Server](#تنظیمات-web-server)
7. [Windows Service Setup](#windows-service-setup)
8. [Backup Strategy](#backup-strategy)
9. [Monitoring و Logging](#monitoring-و-logging)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)
12. [Checklist استقرار](#checklist-استقرار)

---

## معرفی

این راهنما برای استقرار سیستم تیکتینگ ایرانمهر در محیط Production طراحی شده است. تمام مراحل با دقت و امنیت کامل انجام می‌شود.

### ویژگی‌های Production Setup:

- ✅ پشتیبانی از PostgreSQL و SQLite
- ✅ راه‌اندازی با systemd (Linux) و Windows Service
- ✅ پشتیبانی از Nginx Reverse Proxy
- ✅ SSL/TLS با Let's Encrypt
- ✅ Backup خودکار
- ✅ Monitoring و Logging
- ✅ Performance Optimization

---

## پیش‌نیازها

### سخت‌افزار حداقل:

- **CPU**: 2 Core
- **RAM**: 4 GB
- **Storage**: 20 GB (برای دیتابیس و فایل‌ها)
- **Network**: اتصال اینترنت پایدار

### نرم‌افزار:

#### Linux:
- Python 3.10+
- PostgreSQL 12+ (توصیه می‌شود) یا SQLite
- Nginx 1.18+
- systemd
- certbot (برای SSL)

#### Windows:
- Python 3.10+
- PostgreSQL 12+ (توصیه می‌شود) یا SQLite
- IIS یا Nginx (اختیاری)
- NSSM (Non-Sucking Service Manager) برای Windows Service

---

## نصب و راه‌اندازی

### 1. دریافت کد

```bash
# کلون کردن پروژه
git clone <repository-url>
cd imehrTicketing

# یا دانلود و استخراج
# ...
```

### 2. ایجاد Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. نصب Dependencies

```bash
# نصب وابستگی‌ها
pip install --upgrade pip
pip install -r requirements.txt

# برای Production، بدون dev dependencies
pip install -r requirements.txt --no-deps
```

### 4. تنظیمات Environment Variables

فایل `.env` را در ریشه پروژه ایجاد کنید:

```bash
cp env.example .env
nano .env  # یا ویرایشگر دلخواه
```

**مهم**: فایل `.env` را در `.gitignore` قرار دهید و هرگز commit نکنید!

---

## تنظیمات امنیتی

### 1. تولید Secret Keys

```bash
# تولید SECRET_KEY
python scripts/generate_secret_key.py

# یا دستی:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. تنظیمات `.env` برای Production

```env
# Application
APP_NAME=Iranmehr Ticketing System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL توصیه می‌شود)
DATABASE_URL=postgresql://ticketing_user:STRONG_PASSWORD@localhost:5432/ticketing_db

# Security - حتماً تغییر دهید!
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_MINIMUM_32_CHARACTERS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_SECRET=YOUR_GENERATED_REFRESH_SECRET_KEY
REFRESH_TOKEN_EXPIRE_DAYS=14

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret

# Email Configuration
EMAIL_ENABLED=True
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_SMTP_USE_TLS=True
EMAIL_SMTP_USE_SSL=False
EMAIL_FROM_ADDRESS=noreply@iranmehr.com
EMAIL_FROM_NAME=سیستم تیکتینگ ایرانمهر
EMAIL_REPLY_TO=support@iranmehr.com
EMAIL_BCC_ADDRESSES=admin@iranmehr.com,logs@iranmehr.com

# CORS - فقط دامنه‌های مجاز
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# API Base URL
API_BASE_URL=https://api.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ticketing/app.log  # Linux
# LOG_FILE=C:\Logs\ticketing\app.log  # Windows

# File Storage
UPLOAD_DIR=/var/ticketing/storage/uploads  # Linux
# UPLOAD_DIR=C:\Ticketing\storage\uploads  # Windows
MAX_UPLOAD_SIZE=10485760  # 10 MB
```

### 3. محدود کردن دسترسی فایل `.env`

```bash
# Linux
chmod 600 .env
chown $USER:$USER .env

# Windows
icacls .env /inheritance:r /grant:r "%USERNAME%:F"
```

### 4. بررسی تنظیمات Production

```bash
# بررسی تنظیمات
python -c "from app.config import settings; settings.validate_production_settings(); print('Settings OK')"
```

---

## تنظیمات Database

### PostgreSQL (توصیه می‌شود)

#### نصب PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### ایجاد Database و User

```bash
sudo -u postgres psql

-- در PostgreSQL shell:
CREATE DATABASE ticketing_db;
CREATE USER ticketing_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE ticketing_db TO ticketing_user;
\c ticketing_db
GRANT ALL ON SCHEMA public TO ticketing_user;
\q
```

#### تست اتصال

```bash
psql -U ticketing_user -d ticketing_db -c "SELECT version();"
```

### SQLite (برای محیط‌های کوچک)

```bash
# SQLite نیازی به نصب ندارد
# فقط DATABASE_URL را تنظیم کنید:
# DATABASE_URL=sqlite:///./ticketing.db
```

### اجرای Migrations

```bash
# اجرای migration برای ایجاد جداول
python scripts/init_db.py

# ایجاد کاربر ادمین
python scripts/create_admin.py
```

---

## تنظیمات Web Server

### Nginx (Linux)

#### نصب Nginx

```bash
sudo apt-get install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### تنظیمات Nginx

فایل `/etc/nginx/sites-available/ticketing` ایجاد کنید:

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # File upload size
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (if serving from Nginx)
    location /static/ {
        alias /path/to/imehrTicketing/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/ticketing_access.log;
    error_log /var/log/nginx/ticketing_error.log;
}
```

#### فعال‌سازی Configuration

```bash
# ایجاد symbolic link
sudo ln -s /etc/nginx/sites-available/ticketing /etc/nginx/sites-enabled/

# حذف default site (اختیاری)
sudo rm /etc/nginx/sites-enabled/default

# تست configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# نصب certbot
sudo apt-get install certbot python3-certbot-nginx

# دریافت certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (به صورت خودکار تنظیم می‌شود)
sudo certbot renew --dry-run
```

---

## Windows Service Setup

### استفاده از NSSM

#### نصب NSSM

1. دانلود NSSM از: https://nssm.cc/download
2. استخراج و کپی `nssm.exe` به `C:\Windows\System32`

#### ایجاد Windows Service

```cmd
# در Command Prompt با دسترسی Administrator
nssm install TicketingService

# در پنجره NSSM:
# Path: C:\path\to\imehrTicketing\venv\Scripts\python.exe
# Startup directory: C:\path\to\imehrTicketing
# Arguments: -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

یا با استفاده از command line:

```cmd
nssm install TicketingService "C:\path\to\imehrTicketing\venv\Scripts\python.exe" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
nssm set TicketingService AppDirectory "C:\path\to\imehrTicketing"
nssm set TicketingService DisplayName "Iranmehr Ticketing System"
nssm set TicketingService Description "سیستم تیکتینگ ایرانمهر"
nssm set TicketingService Start SERVICE_AUTO_START
```

#### مدیریت Service

```cmd
# شروع
nssm start TicketingService

# توقف
nssm stop TicketingService

# راه‌اندازی مجدد
nssm restart TicketingService

# حذف
nssm remove TicketingService confirm
```

---

## Backup Strategy

### 1. اسکریپت Backup (Linux)

فایل `scripts/backup.sh` ایجاد کنید:

```bash
#!/bin/bash

# تنظیمات
BACKUP_DIR="/var/backups/ticketing"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# ایجاد دایرکتوری backup
mkdir -p $BACKUP_DIR

# Backup Database (PostgreSQL)
if command -v pg_dump &> /dev/null; then
    echo "Backing up PostgreSQL database..."
    pg_dump -U ticketing_user ticketing_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz
    echo "Database backup completed: db_$DATE.sql.gz"
fi

# Backup Database (SQLite)
if [ -f "ticketing.db" ]; then
    echo "Backing up SQLite database..."
    cp ticketing.db $BACKUP_DIR/db_$DATE.db
    gzip $BACKUP_DIR/db_$DATE.db
    echo "SQLite backup completed: db_$DATE.db.gz"
fi

# Backup uploads
if [ -d "/var/ticketing/storage/uploads" ]; then
    echo "Backing up uploads..."
    tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/ticketing/storage/uploads
    echo "Uploads backup completed: uploads_$DATE.tar.gz"
fi

# حذف backup‌های قدیمی
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete
echo "Old backups (older than $RETENTION_DAYS days) deleted"

# گزارش
echo "Backup completed at $(date)"
ls -lh $BACKUP_DIR | tail -5
```

اجرای خودکار با cron:

```bash
# ویرایش crontab
crontab -e

# اضافه کردن (هر روز ساعت 2 صبح)
0 2 * * * /path/to/imehrTicketing/scripts/backup.sh >> /var/log/ticketing/backup.log 2>&1
```

### 2. اسکریپت Backup (Windows)

فایل `scripts/backup.bat` ایجاد کنید:

```batch
@echo off
setlocal

REM تنظیمات
set BACKUP_DIR=C:\Backups\Ticketing
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set RETENTION_DAYS=7

REM ایجاد دایرکتوری backup
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Backup Database (PostgreSQL)
where pg_dump >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backing up PostgreSQL database...
    pg_dump -U ticketing_user ticketing_db | gzip > "%BACKUP_DIR%\db_%DATE%.sql.gz"
    echo Database backup completed: db_%DATE%.sql.gz
)

REM Backup Database (SQLite)
if exist "ticketing.db" (
    echo Backing up SQLite database...
    copy "ticketing.db" "%BACKUP_DIR%\db_%DATE%.db"
    gzip "%BACKUP_DIR%\db_%DATE%.db"
    echo SQLite backup completed: db_%DATE%.db.gz
)

REM Backup uploads
if exist "C:\Ticketing\storage\uploads" (
    echo Backing up uploads...
    tar -czf "%BACKUP_DIR%\uploads_%DATE%.tar.gz" "C:\Ticketing\storage\uploads"
    echo Uploads backup completed: uploads_%DATE%.tar.gz
)

REM حذف backup‌های قدیمی (PowerShell)
powershell -Command "Get-ChildItem '%BACKUP_DIR%' | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-%RETENTION_DAYS%)} | Remove-Item"

echo Backup completed at %date% %time%
dir "%BACKUP_DIR%" /O-D | findstr /C:"db_" /C:"uploads_"

endlocal
```

اجرای خودکار با Task Scheduler:

1. Task Scheduler را باز کنید
2. Create Basic Task
3. نام: Ticketing Backup
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
6. Program: `C:\path\to\imehrTicketing\scripts\backup.bat`

---

## Monitoring و Logging

### 1. Health Check

```bash
# بررسی سلامت سیستم
curl http://localhost:8000/health

# پاسخ:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "environment": "production",
#   "database": "connected"
# }
```

### 2. Log Monitoring

```bash
# مشاهده لاگ‌های زنده
tail -f /var/log/ticketing/app.log

# جستجوی خطاها
grep ERROR /var/log/ticketing/app.log

# خطاهای امروز
grep "$(date +%Y-%m-%d)" /var/log/ticketing/app.log | grep ERROR

# آمار خطاها
grep ERROR /var/log/ticketing/app.log | wc -l
```

### 3. System Monitoring

```bash
# بررسی وضعیت سرویس (Linux)
sudo systemctl status ticketing

# بررسی لاگ‌های systemd
sudo journalctl -u ticketing -f

# بررسی استفاده از منابع
htop  # یا top
df -h  # فضای دیسک
free -h  # حافظه
```

---

## Performance Optimization

### 1. Database Optimization

#### PostgreSQL

```sql
-- ایجاد indexes
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_comments_ticket_id ON comments(ticket_id);

-- تحلیل و به‌روزرسانی آمار
ANALYZE;
VACUUM ANALYZE;
```

#### SQLite

```sql
-- ایجاد indexes
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);

-- بهینه‌سازی
PRAGMA optimize;
```

### 2. Application Optimization

```python
# در app/main.py
# استفاده از workers برای uvicorn
# uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 3. Caching (اختیاری)

برای استفاده از Redis:

```bash
# نصب Redis
sudo apt-get install redis-server

# نصب Python client
pip install redis

# استفاده در کد (مثال)
# from redis import Redis
# redis_client = Redis(host='localhost', port=6379, db=0)
```

---

## Troubleshooting

### مشکلات رایج

#### 1. سرویس شروع نمی‌شود

```bash
# بررسی لاگ‌ها
sudo journalctl -u ticketing -n 50

# بررسی تنظیمات
python -c "from app.config import settings; print(settings.DATABASE_URL)"

# تست اتصال دیتابیس
psql -U ticketing_user -d ticketing_db -c "SELECT 1;"
```

#### 2. خطای Database Connection

```bash
# بررسی PostgreSQL
sudo systemctl status postgresql

# بررسی تنظیمات
cat .env | grep DATABASE_URL

# تست اتصال
python -c "from app.database import engine; engine.connect()"
```

#### 3. خطای Permission

```bash
# بررسی دسترسی فایل‌ها
ls -la .env
ls -la logs/
ls -la storage/

# اصلاح دسترسی
chmod 600 .env
chmod 755 logs/
chmod 755 storage/
```

#### 4. خطای Port در حال استفاده

```bash
# بررسی port
sudo netstat -tulpn | grep 8000

# یا
sudo lsof -i :8000

# توقف process
sudo kill -9 <PID>
```

---

## Checklist استقرار

### قبل از استقرار:

- [ ] Python 3.10+ نصب شده
- [ ] PostgreSQL نصب و راه‌اندازی شده
- [ ] Virtual Environment ایجاد شده
- [ ] Dependencies نصب شده
- [ ] فایل `.env` ایجاد و تنظیم شده
- [ ] Secret Keys تولید شده
- [ ] `DEBUG=False` تنظیم شده
- [ ] Database ایجاد شده
- [ ] Migrations اجرا شده
- [ ] کاربر ادمین ایجاد شده

### استقرار:

- [ ] سرویس systemd/Windows Service ایجاد شده
- [ ] Nginx تنظیم شده
- [ ] SSL Certificate نصب شده
- [ ] Health Check کار می‌کند
- [ ] لاگ‌ها درست نوشته می‌شوند

### بعد از استقرار:

- [ ] Backup خودکار تنظیم شده
- [ ] Monitoring تنظیم شده
- [ ] تست کامل انجام شده
- [ ] مستندات به‌روزرسانی شده

---

## نکات امنیتی مهم

1. ✅ **همیشه `DEBUG=False` در Production**
2. ✅ **از Secret Key قوی استفاده کنید (حداقل 32 کاراکتر)**
3. ✅ **فایل `.env` را در `.gitignore` قرار دهید**
4. ✅ **دسترسی فایل `.env` را محدود کنید (`chmod 600`)**
5. ✅ **از HTTPS استفاده کنید**
6. ✅ **CORS را به دامنه‌های مجاز محدود کنید**
7. ✅ **Backup منظم انجام دهید**
8. ✅ **به‌روزرسانی‌های امنیتی را نصب کنید**
9. ✅ **Firewall را تنظیم کنید**
10. ✅ **از Strong Password برای Database استفاده کنید**

---

**آخرین به‌روزرسانی:** 2025-01-23  
**نسخه:** 1.0.0

