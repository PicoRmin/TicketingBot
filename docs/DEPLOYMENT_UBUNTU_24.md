# 🚀 راهنمای کامل دیپلوی روی اوبونتو 24.04 - سیستم تیکتینگ ایرانمهر

این راهنما به صورت قدم به قدم نحوه دیپلوی سیستم تیکتینگ ایرانمهر روی سرور اوبونتو 24.04 با دامنه `corlink.ir` را توضیح می‌دهد.

---

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیشنیازها)
2. [آماده‌سازی سرور](#آمادهسازی-سرور)
3. [نصب وابستگی‌ها](#نصب-وابستگیها)
4. [کلون و نصب پروژه](#کلون-و-نصب-پروژه)
5. [تنظیمات دیتابیس](#تنظیمات-دیتابیس)
6. [تنظیمات Environment](#تنظیمات-environment)
7. [تنظیمات Nginx](#تنظیمات-nginx)
8. [تنظیمات SSL (Let's Encrypt)](#تنظیمات-ssl-lets-encrypt)
9. [راه‌اندازی Systemd Service](#راهاندازی-systemd-service)
10. [راه‌اندازی Telegram Bot](#راهاندازی-telegram-bot)
11. [تنظیمات Firewall](#تنظیمات-firewall)
12. [تنظیمات Backup](#تنظیمات-backup)
13. [بررسی و تست](#بررسی-و-تست)
14. [Troubleshooting](#troubleshooting)

---

## پیش‌نیازها

### سخت‌افزار حداقل:

- **CPU**: 2 Core
- **RAM**: 4 GB
- **Storage**: 50 GB (برای دیتابیس، فایل‌ها و لاگ‌ها)
- **Network**: اتصال اینترنت پایدار با IP ثابت

### نرم‌افزار:

- **OS**: Ubuntu 24.04 LTS
- **Python**: 3.10 یا بالاتر
- **PostgreSQL**: 14+ (توصیه می‌شود) یا SQLite
- **Nginx**: 1.18+
- **Git**: آخرین نسخه

### دسترسی:

- دسترسی **root** یا کاربر با دسترسی **sudo**
- دسترسی به **DNS** برای تنظیم رکوردهای دامنه
- دسترسی به **پورت 80 و 443** (برای HTTP و HTTPS)

---

## آماده‌سازی سرور

### 1. به‌روزرسانی سیستم

```bash
# به‌روزرسانی لیست پکیج‌ها
sudo apt update
sudo apt upgrade -y

# ریستارت در صورت نیاز
sudo reboot
```

### 2. ایجاد کاربر جدید (اختیاری اما توصیه می‌شود)

```bash
# ایجاد کاربر جدید
sudo adduser ticketing

# اضافه کردن به گروه sudo
sudo usermod -aG sudo ticketing

# ورود به عنوان کاربر جدید
su - ticketing
```

### 3. تنظیمات اولیه

```bash
# نصب ابزارهای ضروری
sudo apt install -y curl wget git vim ufw

# تنظیم timezone
sudo timedatectl set-timezone Asia/Tehran

# بررسی timezone
timedatectl
```

---

## نصب وابستگی‌ها

### 1. نصب Python 3.10+

```bash
# بررسی نسخه Python
python3 --version

# اگر Python 3.10+ نصب نیست:
sudo apt install -y python3.10 python3.10-venv python3-pip

# نصب build essentials برای کامپایل پکیج‌ها
sudo apt install -y build-essential python3-dev
```

### 2. نصب PostgreSQL

```bash
# نصب PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# شروع سرویس
sudo systemctl start postgresql
sudo systemctl enable postgresql

# بررسی وضعیت
sudo systemctl status postgresql
```

### 3. نصب Nginx

```bash
# نصب Nginx
sudo apt install -y nginx

# شروع سرویس
sudo systemctl start nginx
sudo systemctl enable nginx

# بررسی وضعیت
sudo systemctl status nginx
```

### 4. نصب Certbot (برای SSL)

```bash
# نصب certbot
sudo apt install -y certbot python3-certbot-nginx
```

---

## کلون و نصب پروژه

### 1. ایجاد دایرکتوری پروژه

```bash
# رفتن به دایرکتوری home
cd ~

# ایجاد دایرکتوری برای پروژه‌ها
mkdir -p ~/projects
cd ~/projects

# کلون کردن پروژه (یا آپلود فایل‌ها)
# اگر از Git استفاده می‌کنید:
git clone <repository-url> imehrTicketing
# یا
# اگر فایل‌ها را آپلود کرده‌اید:
# unzip imehrTicketing.zip
cd imehrTicketing
```

### 2. ایجاد Virtual Environment

```bash
# ایجاد virtual environment
python3 -m venv venv

# فعال‌سازی
source venv/bin/activate

# به‌روزرسانی pip
pip install --upgrade pip
```

### 3. نصب Dependencies

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# بررسی نصب
pip list
```

---

## تنظیمات دیتابیس

### 1. ایجاد Database و User

```bash
# ورود به PostgreSQL
sudo -u postgres psql

# در PostgreSQL shell:
CREATE DATABASE ticketing_db;
CREATE USER ticketing_user WITH PASSWORD 'YOUR_STRONG_PASSWORD_HERE';
ALTER ROLE ticketing_user SET client_encoding TO 'utf8';
ALTER ROLE ticketing_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ticketing_user SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE ticketing_db TO ticketing_user;
\c ticketing_db
GRANT ALL ON SCHEMA public TO ticketing_user;
\q
```

**⚠️ مهم**: `YOUR_STRONG_PASSWORD_HERE` را با رمز عبور قوی جایگزین کنید!

### 2. تست اتصال

```bash
# تست اتصال
psql -U ticketing_user -d ticketing_db -h localhost -c "SELECT version();"
```

### 3. ایجاد جداول

```bash
# فعال‌سازی virtual environment (اگر نیست)
source venv/bin/activate

# اجرای migration
python scripts/init_db.py
```

### 4. ایجاد کاربر ادمین

```bash
# ایجاد کاربر ادمین
python scripts/create_admin.py

# یا دستی:
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
db = SessionLocal()
admin = User(
    username='admin',
    password_hash=get_password_hash('admin123'),
    full_name='مدیر سیستم',
    role='central_admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

---

## تنظیمات Environment

### 1. ایجاد فایل .env

```bash
# کپی از env.example
cp env.example .env

# ویرایش فایل
nano .env
```

### 2. محتوای فایل .env

```env
# Application
APP_NAME=Iranmehr Ticketing System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL)
DATABASE_URL=postgresql://ticketing_user:YOUR_STRONG_PASSWORD_HERE@localhost:5432/ticketing_db

# Security - حتماً تغییر دهید!
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_MINIMUM_32_CHARACTERS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_SECRET=YOUR_GENERATED_REFRESH_SECRET_KEY
REFRESH_TOKEN_EXPIRE_DAYS=14

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_WEBHOOK_URL=https://corlink.ir/webhook
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret

# Email Configuration
EMAIL_ENABLED=True
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_SMTP_USE_TLS=True
EMAIL_SMTP_USE_SSL=False
EMAIL_FROM_ADDRESS=noreply@corlink.ir
EMAIL_FROM_NAME=سیستم تیکتینگ ایرانمهر
EMAIL_REPLY_TO=support@corlink.ir
EMAIL_BCC_ADDRESSES=admin@corlink.ir

# CORS - دامنه‌های مجاز
CORS_ORIGINS=https://corlink.ir,https://www.corlink.ir,https://admin.corlink.ir

# API Base URL
API_BASE_URL=https://corlink.ir

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ticketing/app.log

# File Storage
UPLOAD_DIR=/var/ticketing/storage/uploads
MAX_UPLOAD_SIZE=10485760
```

### 3. تولید Secret Keys

```bash
# تولید SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# تولید REFRESH_TOKEN_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

مقادیر تولید شده را در فایل `.env` جایگزین کنید.

### 4. محدود کردن دسترسی فایل .env

```bash
# محدود کردن دسترسی
chmod 600 .env
chown $USER:$USER .env
```

### 5. ایجاد دایرکتوری‌های لازم

```bash
# ایجاد دایرکتوری لاگ
sudo mkdir -p /var/log/ticketing
sudo chown $USER:$USER /var/log/ticketing

# ایجاد دایرکتوری storage
sudo mkdir -p /var/ticketing/storage/uploads
sudo chown -R $USER:$USER /var/ticketing
```

---

## تنظیمات Nginx

### 1. ایجاد Configuration File

```bash
# ایجاد فایل configuration
sudo nano /etc/nginx/sites-available/ticketing
```

### 2. محتوای Configuration

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name corlink.ir www.corlink.ir;

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
    listen [::]:443 ssl http2;
    server_name corlink.ir www.corlink.ir;

    # SSL certificates (Let's Encrypt - بعداً تنظیم می‌شود)
    ssl_certificate /etc/letsencrypt/live/corlink.ir/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/corlink.ir/privkey.pem;
    
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

    # Proxy settings for API
    location /api/ {
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

    # Serve frontend (if built)
    location / {
        root /var/www/ticketing;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # Static files (if serving from Nginx)
    location /static/ {
        alias /home/ticketing/projects/imehrTicketing/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/ticketing_access.log;
    error_log /var/log/nginx/ticketing_error.log;
}
```

### 3. فعال‌سازی Configuration

```bash
# ایجاد symbolic link
sudo ln -s /etc/nginx/sites-available/ticketing /etc/nginx/sites-enabled/

# حذف default site (اختیاری)
sudo rm /etc/nginx/sites-enabled/default

# تست configuration
sudo nginx -t

# اگر تست موفق بود، reload
sudo systemctl reload nginx
```

---

## تنظیمات SSL (Let's Encrypt)

### 1. دریافت Certificate

```bash
# دریافت certificate
sudo certbot --nginx -d corlink.ir -d www.corlink.ir

# در طول فرآیند:
# - ایمیل خود را وارد کنید
# - شرایط را بپذیرید
# - انتخاب کنید که آیا می‌خواهید ایمیل دریافت کنید (اختیاری)
```

### 2. تست Auto-renewal

```bash
# تست auto-renewal
sudo certbot renew --dry-run

# بررسی وضعیت certificate
sudo certbot certificates
```

### 3. تنظیم Auto-renewal (به صورت خودکار تنظیم می‌شود)

```bash
# بررسی cron job
sudo systemctl status certbot.timer

# یا
sudo crontab -l | grep certbot
```

---

## راه‌اندازی Systemd Service

### 1. ایجاد Service File

```bash
# ایجاد فایل service
sudo nano /etc/systemd/system/ticketing.service
```

### 2. محتوای Service File

```ini
[Unit]
Description=Iranmehr Ticketing System
After=network.target postgresql.service

[Service]
Type=simple
User=ticketing
Group=ticketing
WorkingDirectory=/home/ticketing/projects/imehrTicketing
Environment="PATH=/home/ticketing/projects/imehrTicketing/venv/bin"
ExecStart=/home/ticketing/projects/imehrTicketing/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ticketing

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**⚠️ مهم**: مسیرها را با مسیر واقعی پروژه خود جایگزین کنید!

### 3. فعال‌سازی و شروع Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# فعال‌سازی service (شروع خودکار در boot)
sudo systemctl enable ticketing

# شروع service
sudo systemctl start ticketing

# بررسی وضعیت
sudo systemctl status ticketing

# مشاهده لاگ‌ها
sudo journalctl -u ticketing -f
```

---

## راه‌اندازی Telegram Bot

### 1. دریافت Bot Token

1. در تلگرام، با `@BotFather` صحبت کنید
2. دستور `/newbot` را ارسال کنید
3. نام و username ربات را انتخاب کنید
4. Token دریافت شده را در فایل `.env` قرار دهید:
   ```env
   TELEGRAM_BOT_TOKEN=your-token-here
   ```

### 2. راه‌اندازی Bot

Bot به صورت خودکار با شروع سرویس راه‌اندازی می‌شود. برای بررسی:

```bash
# بررسی لاگ‌ها
sudo journalctl -u ticketing -f | grep -i telegram

# یا
tail -f /var/log/ticketing/app.log | grep -i telegram
```

### 3. تست Bot

1. در تلگرام، ربات را پیدا کنید
2. دستور `/start` را ارسال کنید
3. باید پیام خوشامدگویی را دریافت کنید

---

## تنظیمات Firewall

### 1. فعال‌سازی UFW

```bash
# بررسی وضعیت
sudo ufw status

# اگر غیرفعال است، فعال کنید
sudo ufw enable

# اجازه SSH (مهم!)
sudo ufw allow 22/tcp

# اجازه HTTP
sudo ufw allow 80/tcp

# اجازه HTTPS
sudo ufw allow 443/tcp

# بررسی وضعیت
sudo ufw status verbose
```

### 2. تنظیمات اضافی (اختیاری)

```bash
# محدود کردن SSH به IP خاص (اختیاری)
sudo ufw allow from YOUR_IP_ADDRESS to any port 22

# یا استفاده از fail2ban برای محافظت از SSH
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## تنظیمات Backup

### 1. ایجاد اسکریپت Backup

```bash
# ایجاد فایل backup script
nano ~/backup_ticketing.sh
```

### 2. محتوای اسکریپت

```bash
#!/bin/bash

# تنظیمات
BACKUP_DIR="/var/backups/ticketing"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# ایجاد دایرکتوری backup
mkdir -p $BACKUP_DIR

# Backup Database (PostgreSQL)
echo "Backing up PostgreSQL database..."
pg_dump -U ticketing_user -h localhost ticketing_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz
echo "Database backup completed: db_$DATE.sql.gz"

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

### 3. قابل اجرا کردن اسکریپت

```bash
# قابل اجرا کردن
chmod +x ~/backup_ticketing.sh

# تست اجرا
~/backup_ticketing.sh
```

### 4. تنظیم Cron Job

```bash
# ویرایش crontab
crontab -e

# اضافه کردن (هر روز ساعت 2 صبح)
0 2 * * * /home/ticketing/backup_ticketing.sh >> /var/log/ticketing/backup.log 2>&1
```

---

## بررسی و تست

### 1. بررسی سرویس‌ها

```bash
# بررسی Nginx
sudo systemctl status nginx

# بررسی PostgreSQL
sudo systemctl status postgresql

# بررسی Ticketing Service
sudo systemctl status ticketing

# بررسی Certbot Timer
sudo systemctl status certbot.timer
```

### 2. تست API

```bash
# تست Health Check
curl https://corlink.ir/api/health

# تست با Authentication
curl -X POST https://corlink.ir/api/auth/login-form \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 3. تست Frontend

1. مرورگر را باز کنید
2. به آدرس `https://corlink.ir` بروید
3. باید صفحه Login یا Dashboard را ببینید

### 4. تست Telegram Bot

1. در تلگرام، ربات را پیدا کنید
2. دستور `/start` را ارسال کنید
3. باید پیام خوشامدگویی را دریافت کنید

---

## Troubleshooting

### مشکل 1: سرویس شروع نمی‌شود

```bash
# بررسی لاگ‌ها
sudo journalctl -u ticketing -n 50

# بررسی فایل .env
cat .env | grep -v PASSWORD

# تست دستی اجرا
cd /home/ticketing/projects/imehrTicketing
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### مشکل 2: خطای Database Connection

```bash
# بررسی PostgreSQL
sudo systemctl status postgresql

# تست اتصال
psql -U ticketing_user -d ticketing_db -h localhost -c "SELECT 1;"

# بررسی تنظیمات .env
cat .env | grep DATABASE_URL
```

### مشکل 3: خطای SSL Certificate

```bash
# بررسی certificate
sudo certbot certificates

# تمدید دستی
sudo certbot renew

# بررسی Nginx configuration
sudo nginx -t
```

### مشکل 4: خطای Permission

```bash
# بررسی دسترسی فایل‌ها
ls -la /var/log/ticketing
ls -la /var/ticketing/storage

# اصلاح دسترسی
sudo chown -R ticketing:ticketing /var/log/ticketing
sudo chown -R ticketing:ticketing /var/ticketing
```

### مشکل 5: Telegram Bot کار نمی‌کند

```bash
# بررسی Token
cat .env | grep TELEGRAM_BOT_TOKEN

# بررسی لاگ‌ها
tail -f /var/log/ticketing/app.log | grep -i telegram

# تست دستی
python -c "from app.telegram_bot.bot import test_telegram_connection; import asyncio; asyncio.run(test_telegram_connection('YOUR_TOKEN'))"
```

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

## Checklist نهایی

### قبل از دیپلوی:

- [ ] Python 3.10+ نصب شده
- [ ] PostgreSQL نصب و راه‌اندازی شده
- [ ] Nginx نصب شده
- [ ] Virtual Environment ایجاد شده
- [ ] Dependencies نصب شده
- [ ] فایل `.env` ایجاد و تنظیم شده
- [ ] Secret Keys تولید شده
- [ ] `DEBUG=False` تنظیم شده
- [ ] Database ایجاد شده
- [ ] Migrations اجرا شده
- [ ] کاربر ادمین ایجاد شده

### دیپلوی:

- [ ] Nginx Configuration تنظیم شده
- [ ] SSL Certificate دریافت شده
- [ ] Systemd Service ایجاد شده
- [ ] Service شروع شده
- [ ] Firewall تنظیم شده
- [ ] Backup Script ایجاد شده
- [ ] Cron Job تنظیم شده

### بعد از دیپلوی:

- [ ] Health Check کار می‌کند
- [ ] API در دسترس است
- [ ] Frontend در دسترس است
- [ ] Telegram Bot کار می‌کند
- [ ] SSL Certificate معتبر است
- [ ] Backup خودکار کار می‌کند
- [ ] لاگ‌ها درست نوشته می‌شوند

---

## دستورات مفید

### مدیریت Service

```bash
# شروع
sudo systemctl start ticketing

# توقف
sudo systemctl stop ticketing

# راه‌اندازی مجدد
sudo systemctl restart ticketing

# مشاهده وضعیت
sudo systemctl status ticketing

# مشاهده لاگ‌ها
sudo journalctl -u ticketing -f
```

### مدیریت Nginx

```bash
# تست configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Restart
sudo systemctl restart nginx

# مشاهده لاگ‌ها
sudo tail -f /var/log/nginx/ticketing_access.log
sudo tail -f /var/log/nginx/ticketing_error.log
```

### مدیریت Database

```bash
# Backup
pg_dump -U ticketing_user -h localhost ticketing_db > backup.sql

# Restore
psql -U ticketing_user -h localhost ticketing_db < backup.sql
```

---

**آخرین به‌روزرسانی**: 2025-01-25  
**نسخه**: 1.0.0  
**دامنه**: corlink.ir

