## راهنمای Performance Tests

این سند نحوه اجرای تست‌های Load و Stress روی بک‌اند FastAPI را توضیح می‌دهد.

---

### اهداف

- اندازه‌گیری زمان پاسخ‌گویی Endpoint‌های حیاتی (Tickets, Reports, SLA)
- شناسایی گلوگاه‌ها در شرایط ترافیک متوسط و اوج
- ایجاد گزارش استاندارد برای مانیتورینگ در آینده

---

### پیش‌نیازها

- Backend روی `http://127.0.0.1:8000` در حال اجرا باشد.
- کاربر ادمین برای دریافت Token داشته باشید (با `scripts/create_admin.py`).
- پکیج‌های مورد نیاز (httpx) با `pip install -r requirements.txt` نصب شده باشند.

---

### اجرای تست

```bash
# از ریشه پروژه
python -m tests.performance.run_performance_tests \
  --username admin \
  --password "Pass123!" \
  --load-concurrency 15 \
  --load-duration 90 \
  --stress-start 10 \
  --stress-max 60 \
  --stress-step 10
```

پارامترهای مهم:

| پارامتر | توضیح |
|---------|-------|
| `--base-url` | آدرس سرویس (پیش‌فرض: `http://127.0.0.1:8000`) |
| `--token` | اگر دستی Token دارید وارد کنید؛ در غیر اینصورت username/password بدهید |
| `--load-concurrency` | تعداد درخواست همزمان در تست Load |
| `--load-duration` | طول تست Load بر حسب ثانیه |
| `--stress-max` | حداکثر سطح همزمانی برای تست Stress |

---

### خروجی

هر سناریو یک آبجکت JSON مانند زیر چاپ می‌کند:

```json
{
  "title": "Load Test",
  "total_requests": 420,
  "success_count": 420,
  "failure_count": 0,
  "avg_ms": 185.21,
  "p95_ms": 310.55,
  "max_ms": 520.44,
  "error_samples": []
}
```

- `avg_ms`: میانگین تاخیر
- `p95_ms`: زمان پاسخ 95 درصد درخواست‌ها
- `error_samples`: حداکثر 5 خطای آخر برای عیب‌یابی سریع

---

### تفسیر نتایج

- **Load Test**: اگر `p95_ms` زیر 400 باشد و خطای 5xx نداشته باشیم، وضعیت مطلوب است.
- **Stress Test**: اولین سطحی که نرخ خطا از 5٪ بیشتر می‌شود، سقف تحمل فعلی سیستم است.

---

### پیشنهادات بعد از تست

1. اگر خطا زیاد بود، لاگ‌های backend (`logs/app.log`) را بررسی کنید.
2. Queryهای کند را با SQLAlchemy `echo=True` پروفایل کنید.
3. نتایج را در `docs/TESTING.md` وارد کنید یا در ابزار مانیتورینگ ذخیره کنید.

---

**آخرین به‌روزرسانی:** 2025-11-24

