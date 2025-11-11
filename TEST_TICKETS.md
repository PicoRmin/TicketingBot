# راهنمای تست Ticket API / Ticket API Testing Guide

## 🚀 تست سریع

### 1. اجرای Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. باز کردن Swagger UI
- آدرس: http://localhost:8000/docs
- مشاهده endpoint های Tickets

### 3. تست کامل جریان

#### مرحله ۱: Login
1. کلیک روی `POST /api/auth/login`
2. وارد کردن:
   - username: `admin`
   - password: `admin123`
3. دریافت `access_token`

#### مرحله ۲: Authorize
1. کلیک روی "Authorize" در بالای صفحه
2. وارد کردن: `Bearer <access_token>`
3. کلیک روی "Authorize"

#### مرحله ۳: ایجاد تیکت
1. کلیک روی `POST /api/tickets`
2. وارد کردن:
   ```json
   {
     "title": "مشکل اینترنت",
     "description": "اینترنت در بخش IT قطع شده است و نیاز به بررسی دارد",
     "category": "internet"
   }
   ```
3. کلیک روی "Execute"
4. مشاهده تیکت ایجاد شده با شماره یکتا (مثلاً: T-20241111-0001)

#### مرحله ۴: لیست تیکت‌ها
1. کلیک روی `GET /api/tickets`
2. تنظیم پارامترها:
   - page: 1
   - page_size: 10
3. کلیک روی "Execute"
4. مشاهده لیست تیکت‌ها با pagination

#### مرحله ۵: جزئیات تیکت
1. کلیک روی `GET /api/tickets/{ticket_id}`
2. وارد کردن ticket_id از تیکت ایجاد شده
3. کلیک روی "Execute"
4. مشاهده جزئیات کامل تیکت

#### مرحله ۶: تغییر وضعیت (فقط ادمین)
1. کلیک روی `PATCH /api/tickets/{ticket_id}/status`
2. وارد کردن ticket_id
3. وارد کردن:
   ```json
   {
     "status": "in_progress"
   }
   ```
4. کلیک روی "Execute"
5. مشاهده تیکت با وضعیت جدید

## 📋 تست با curl

### کامل جریان

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. ایجاد تیکت
curl -X POST "http://localhost:8000/api/tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "مشکل اینترنت",
    "description": "اینترنت در بخش IT قطع شده است",
    "category": "internet"
  }' | jq

# 3. لیست تیکت‌ها
curl -X GET "http://localhost:8000/api/tickets?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. دریافت تیکت بر اساس ID
curl -X GET "http://localhost:8000/api/tickets/1" \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. به‌روزرسانی تیکت
curl -X PUT "http://localhost:8000/api/tickets/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "مشکل اینترنت - به‌روزرسانی شده",
    "description": "اینترنت در بخش IT قطع شده است - نیاز به بررسی فوری"
  }' | jq

# 6. تغییر وضعیت (فقط ادمین)
curl -X PATCH "http://localhost:8000/api/tickets/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }' | jq
```

## 🐍 تست با Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. ایجاد تیکت
ticket_data = {
    "title": "مشکل اینترنت",
    "description": "اینترنت در بخش IT قطع شده است",
    "category": "internet"
}
response = requests.post(
    f"{BASE_URL}/api/tickets",
    json=ticket_data,
    headers=headers
)
ticket = response.json()
print(f"✅ Ticket created: {ticket['ticket_number']}")

# 3. لیست تیکت‌ها
response = requests.get(
    f"{BASE_URL}/api/tickets?page=1&page_size=10",
    headers=headers
)
tickets = response.json()
print(f"✅ Total tickets: {tickets['total']}")

# 4. دریافت تیکت
ticket_id = ticket['id']
response = requests.get(
    f"{BASE_URL}/api/tickets/{ticket_id}",
    headers=headers
)
ticket = response.json()
print(f"✅ Ticket: {ticket['ticket_number']} - {ticket['status']}")

# 5. تغییر وضعیت
response = requests.patch(
    f"{BASE_URL}/api/tickets/{ticket_id}/status",
    json={"status": "in_progress"},
    headers=headers
)
updated_ticket = response.json()
print(f"✅ Status updated: {updated_ticket['status']}")
```

## ✅ نتیجه مورد انتظار

### ایجاد تیکت
```json
{
  "id": 1,
  "ticket_number": "T-20241111-0001",
  "title": "مشکل اینترنت",
  "description": "اینترنت در بخش IT قطع شده است",
  "category": "internet",
  "status": "pending",
  "user_id": 1,
  "created_at": "2024-11-11T08:00:00",
  "updated_at": "2024-11-11T08:00:00"
}
```

### لیست تیکت‌ها
```json
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

## 🐛 عیب‌یابی

### مشکل: 401 Unauthorized
**راه‌حل**: مطمئن شوید که Token را در Header قرار داده‌اید:
```
Authorization: Bearer <token>
```

### مشکل: 403 Forbidden
**راه‌حل**: 
- کاربران فقط می‌توانند تیکت‌های خود را ببینند
- فقط ادمین می‌تواند وضعیت را تغییر دهد

### مشکل: 404 Not Found
**راه‌حل**: مطمئن شوید که ticket_id صحیح است

### مشکل: شماره تیکت تکراری
**راه‌حل**: این مشکل نباید رخ دهد. اگر رخ داد، دیتابیس را بررسی کنید.

---

**تاریخ**: 2024-11-11

