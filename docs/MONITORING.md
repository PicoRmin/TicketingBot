# 📊 راهنمای Monitoring و Logging - سیستم تیکتینگ ایرانمهر

## فهرست مطالب
1. [معرفی](#معرفی)
2. [Health Check](#health-check)
3. [Logging](#logging)
4. [Monitoring Tools](#monitoring-tools)
5. [Alerting](#alerting)
6. [Performance Monitoring](#performance-monitoring)

---

## معرفی

راهنمای کامل برای Monitoring و Logging سیستم تیکتینگ ایرانمهر در محیط Production.

---

## Health Check

### Endpoint

```bash
GET /health
```

### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected"
}
```

### استفاده

```bash
# بررسی سلامت سیستم
curl http://localhost:8000/health

# با timeout
curl --max-time 5 http://localhost:8000/health

# در script
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Service is healthy"
else
    echo "Service is down!"
fi
```

---

## Logging

### ساختار لاگ‌ها

لاگ‌ها در فایل `logs/app.log` ذخیره می‌شوند.

### سطوح Logging

- **DEBUG**: اطلاعات جزئی برای debugging
- **INFO**: اطلاعات عمومی
- **WARNING**: هشدارها
- **ERROR**: خطاها
- **CRITICAL**: خطاهای بحرانی

### مشاهده لاگ‌ها

```bash
# مشاهده لاگ‌های زنده
tail -f logs/app.log

# آخرین 100 خط
tail -n 100 logs/app.log

# خطاها
grep ERROR logs/app.log

# خطاهای امروز
grep "$(date +%Y-%m-%d)" logs/app.log | grep ERROR

# آمار خطاها
grep ERROR logs/app.log | wc -l

# خطاهای یک ساعت گذشته
grep "$(date -d '1 hour ago' +%Y-%m-%d)" logs/app.log | grep ERROR
```

### Log Rotation

استفاده از `logrotate` (Linux):

```bash
# فایل /etc/logrotate.d/ticketing
/path/to/imehrTicketing/logs/app.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ticketing > /dev/null 2>&1 || true
    endscript
}
```

---

## Monitoring Tools

### 1. System Monitoring

```bash
# استفاده از CPU و Memory
htop

# یا
top

# فضای دیسک
df -h

# استفاده از حافظه
free -h

# Network
iftop
```

### 2. Application Monitoring

```bash
# بررسی وضعیت سرویس (systemd)
sudo systemctl status ticketing

# لاگ‌های systemd
sudo journalctl -u ticketing -f

# آخرین 50 خط
sudo journalctl -u ticketing -n 50

# خطاها
sudo journalctl -u ticketing | grep ERROR
```

### 3. Database Monitoring

#### PostgreSQL

```sql
-- تعداد اتصالات
SELECT count(*) FROM pg_stat_activity;

-- کوئری‌های کند
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- اندازه دیتابیس
SELECT pg_size_pretty(pg_database_size('ticketing_db'));
```

#### SQLite

```bash
# اندازه فایل
ls -lh ticketing.db

# بررسی integrity
sqlite3 ticketing.db "PRAGMA integrity_check;"
```

---

## Alerting

### Email Alerts

می‌توانید از cron job برای ارسال ایمیل در صورت خطا استفاده کنید:

```bash
# فایل scripts/check_and_alert.sh
#!/bin/bash
ERROR_COUNT=$(grep -c ERROR logs/app.log | tail -100)
if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "High error count: $ERROR_COUNT" | mail -s "Ticketing System Alert" admin@example.com
fi
```

### Health Check Monitoring

```bash
# فایل scripts/monitor_health.sh
#!/bin/bash
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Service is down!" | mail -s "Ticketing System Down" admin@example.com
    systemctl restart ticketing
fi
```

---

## Performance Monitoring

### 1. Response Time

```bash
# تست response time
time curl http://localhost:8000/health

# با Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

### 2. Database Performance

```sql
-- Slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### 3. Application Metrics

می‌توانید از Prometheus و Grafana برای monitoring پیشرفته استفاده کنید.

---

**آخرین به‌روزرسانی:** 2025-01-23  
**نسخه:** 1.0.0

