# راهنمای استقرار Production

این راهنما برای استقرار سیستم تیکتینگ ایرانمهر در محیط Production است.

**⚠️ توجه**: این فایل برای سازگاری با نسخه‌های قبلی نگه داشته شده است. برای راهنمای کامل و به‌روز، به [راهنمای Production Setup](./docs/PRODUCTION_SETUP.md) مراجعه کنید.

## پیش‌نیازها

- Python 3.10+
- PostgreSQL (توصیه می‌شود) یا SQLite
- Nginx (برای reverse proxy)
- Supervisor یا systemd (برای مدیریت process)

## 1. تنظیمات Environment Variables

فایل `.env` را در ریشه پروژه ایجاد کنید:

```bash
# Application
APP_NAME=Iranmehr Ticketing System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL توصیه می‌شود)
DATABASE_URL=postgresql://user:password@localhost:5432/ticketing_db

# Security - حتماً تغییر دهید!
SECRET_KEY=your-very-long-and-random-secret-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_SECRET=your-very-long-and-random-refresh-secret-key-here
REFRESH_TOKEN_EXPIRE_DAYS=14

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret

# CORS - فقط دامنه‌های مجاز
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# API Base URL
API_BASE_URL=https://api.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ticketing/app.log

# File Storage
UPLOAD_DIR=/var/ticketing/storage/uploads
MAX_UPLOAD_SIZE=10485760
```

## 2. نصب وابستگی‌ها

```bash
# ایجاد virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt
```

## 3. تنظیمات Database

### PostgreSQL

```bash
# نصب PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# ایجاد دیتابیس
sudo -u postgres psql
CREATE DATABASE ticketing_db;
CREATE USER ticketing_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ticketing_db TO ticketing_user;
\q
```

### اجرای Migration

```bash
# اجرای migration برای ایجاد جداول
python scripts/init_db.py

# یا اگر از Alembic استفاده می‌کنید
alembic upgrade head
```

## 4. تنظیمات Security

### تولید Secret Key

```bash
python scripts/generate_secret_key.py
```

### تنظیمات فایل‌ها

- اطمینان حاصل کنید که فایل `.env` در `.gitignore` است
- دسترسی فایل `.env` را محدود کنید: `chmod 600 .env`
- اطمینان حاصل کنید که `DEBUG=False` در Production

## 5. تنظیمات Logging

```bash
# ایجاد دایرکتوری لاگ
sudo mkdir -p /var/log/ticketing
sudo chown $USER:$USER /var/log/ticketing
```

## 6. استقرار با systemd

فایل `/etc/systemd/system/ticketing.service` ایجاد کنید:

```ini
[Unit]
Description=Iranmehr Ticketing System
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/imehrTicketing
Environment="PATH=/path/to/imehrTicketing/venv/bin"
ExecStart=/path/to/imehrTicketing/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

فعال‌سازی:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ticketing
sudo systemctl start ticketing
sudo systemctl status ticketing
```

## 7. تنظیمات Nginx

فایل `/etc/nginx/sites-available/ticketing` ایجاد کنید:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

فعال‌سازی:

```bash
sudo ln -s /etc/nginx/sites-available/ticketing /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 8. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## 9. Backup Strategy

### Backup Database

```bash
# PostgreSQL
pg_dump -U ticketing_user ticketing_db > backup_$(date +%Y%m%d).sql

# SQLite
cp ticketing.db backup_$(date +%Y%m%d).db
```

### Automated Backup Script

فایل `scripts/backup.sh` ایجاد کنید:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ticketing"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U ticketing_user ticketing_db > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/ticketing/storage/uploads

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

اجرای خودکار با cron:

```bash
# هر روز ساعت 2 صبح
0 2 * * * /path/to/scripts/backup.sh
```

## 10. Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Log Monitoring

```bash
# مشاهده لاگ‌های زنده
tail -f /var/log/ticketing/app.log

# جستجوی خطاها
grep ERROR /var/log/ticketing/app.log
```

## 11. Performance Optimization

### Database Indexing

اطمینان حاصل کنید که indexes مناسب ایجاد شده‌اند.

### Caching (اختیاری)

برای استفاده از Redis:

```bash
pip install redis
```

## 12. Troubleshooting

### بررسی وضعیت سرویس

```bash
sudo systemctl status ticketing
sudo journalctl -u ticketing -f
```

### بررسی لاگ‌ها

```bash
tail -f /var/log/ticketing/app.log
```

### بررسی Database Connection

```bash
psql -U ticketing_user -d ticketing_db -c "SELECT 1;"
```

## نکات امنیتی

1. ✅ همیشه `DEBUG=False` در Production
2. ✅ از Secret Key قوی استفاده کنید
3. ✅ فایل `.env` را در `.gitignore` قرار دهید
4. ✅ دسترسی فایل‌ها را محدود کنید
5. ✅ از HTTPS استفاده کنید
6. ✅ CORS را به دامنه‌های مجاز محدود کنید
7. ✅ Backup منظم انجام دهید
8. ✅ به‌روزرسانی‌های امنیتی را نصب کنید

