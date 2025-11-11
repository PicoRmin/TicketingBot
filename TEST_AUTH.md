# راهنمای تست Authentication / Authentication Testing Guide

## 🚀 تست سریع

### 1. اجرای Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. باز کردن Swagger UI
- آدرس: http://localhost:8000/docs
- مشاهده endpoint های Authentication

### 3. تست Login
1. کلیک روی `POST /api/auth/login`
2. کلیک روی "Try it out"
3. وارد کردن:
   - username: `admin`
   - password: `admin123`
4. کلیک روی "Execute"
5. دریافت `access_token`

### 4. تست Get Current User
1. کلیک روی "Authorize" در بالای صفحه
2. وارد کردن Token: `Bearer <access_token>`
3. کلیک روی "Authorize"
4. کلیک روی `GET /api/auth/me`
5. کلیک روی "Execute"
6. مشاهده اطلاعات کاربر

## 📋 تست با curl

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

## 🐍 تست با Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]
print(f"Token: {token}")

# Get Current User
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(f"User: {response.json()}")
```

## ✅ نتیجه مورد انتظار

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User Response
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "مدیر سیستم",
  "role": "admin",
  "language": "fa",
  "is_active": true,
  "created_at": "2024-11-11T08:00:00",
  "updated_at": "2024-11-11T08:00:00"
}
```

## 🐛 عیب‌یابی

### مشکل: 401 Unauthorized
- مطمئن شوید که username و password صحیح است
- مطمئن شوید که کاربر `is_active=True` است

### مشکل: Token invalid
- مطمئن شوید که Token را به درستی در Header قرار داده‌اید
- فرمت: `Authorization: Bearer <token>`

### مشکل: Inactive user
- کاربر باید `is_active=True` باشد
- می‌توانید با script `create_admin.py` کاربر جدید ایجاد کنید

---

**تاریخ**: 2024-11-11

