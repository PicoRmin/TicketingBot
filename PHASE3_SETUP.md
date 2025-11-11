# راهنمای فاز ۳: سیستم احراز هویت / Phase 3: Authentication System Guide

## ✅ کارهای انجام شده

### ۱. ایجاد Schemas
- ✅ `UserBase` - Base schema برای User
- ✅ `UserCreate` - Schema برای ایجاد کاربر
- ✅ `UserUpdate` - Schema برای به‌روزرسانی کاربر
- ✅ `UserResponse` - Schema برای پاسخ API
- ✅ `LoginRequest` - Schema برای درخواست Login
- ✅ `Token` - Schema برای Token response
- ✅ `TokenData` - Schema برای داده‌های Token

### ۲. ایجاد Dependencies
- ✅ `get_current_user` - دریافت کاربر فعلی از Token
- ✅ `get_current_active_user` - دریافت کاربر فعال فعلی
- ✅ `require_admin` - نیاز به نقش Admin

### ۳. ایجاد API Endpoints
- ✅ `POST /api/auth/login` - Login با OAuth2PasswordRequestForm
- ✅ `POST /api/auth/login-form` - Login با JSON form data
- ✅ `GET /api/auth/me` - دریافت اطلاعات کاربر فعلی

### ۴. ایجاد API Router
- ✅ `app/api/auth.py` - Router برای Authentication
- ✅ اضافه شدن router به `main.py`

### ۵. حل مشکلات
- ✅ CORS_ORIGINS - حل شده
- ✅ verify_password - ساده‌سازی شده

## 🚀 تست Authentication

### تست با Swagger UI

1. **اجرای Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **باز کردن Swagger UI**:
   - آدرس: http://localhost:8000/docs

3. **تست Login**:
   - کلیک روی `POST /api/auth/login`
   - کلیک روی "Try it out"
   - وارد کردن:
     - username: `admin`
     - password: `admin123`
   - کلیک روی "Execute"
   - دریافت `access_token`

4. **تست Get Current User**:
   - کلیک روی "Authorize" در بالای صفحه
   - وارد کردن Token: `Bearer <access_token>`
   - کلیک روی "Authorize"
   - کلیک روی `GET /api/auth/me`
   - کلیک روی "Execute"
   - مشاهده اطلاعات کاربر

### تست با curl

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# پاسخ:
# {"access_token":"eyJ...","token_type":"bearer"}

# 2. Get Current User
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"

# پاسخ:
# {"id":1,"username":"admin","full_name":"مدیر سیستم",...}
```

### تست با Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get Current User
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(response.json())
```

## 📁 ساختار فایل‌های ایجاد شده

```
app/
├── api/
│   ├── __init__.py        ✅ API exports
│   ├── auth.py            ✅ Authentication endpoints
│   └── deps.py            ✅ Dependencies
├── schemas/
│   ├── __init__.py        ✅ Schema exports
│   ├── user.py            ✅ User schemas
│   └── token.py           ✅ Token schemas
└── main.py                ✅ Updated with auth router
```

## 🔍 API Endpoints

### POST /api/auth/login
- **Description**: Login با OAuth2PasswordRequestForm
- **Request**: `username`, `password` (form data)
- **Response**: `{"access_token": "...", "token_type": "bearer"}`
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

### POST /api/auth/login-form
- **Description**: Login با JSON form data
- **Request**: `{"username": "...", "password": "..."}`
- **Response**: `{"access_token": "...", "token_type": "bearer"}`
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

### GET /api/auth/me
- **Description**: دریافت اطلاعات کاربر فعلی
- **Headers**: `Authorization: Bearer <token>`
- **Response**: User information
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

## 🔐 Security

### JWT Token
- **Algorithm**: HS256
- **Expiration**: 1440 minutes (24 hours)
- **Payload**: `{"sub": username, "user_id": id, "role": role}`

### Password Hashing
- **Algorithm**: bcrypt
- **Salt**: Auto-generated
- **Verification**: Direct bcrypt verification

## ✅ چک‌لیست

- [x] Schemas ایجاد شده
- [x] Dependencies ایجاد شده
- [x] API Endpoints ایجاد شده
- [x] Router اضافه شده به main.py
- [x] تست با Swagger UI
- [x] تست با curl
- [x] تست با Python

## 🐛 عیب‌یابی

### مشکل: 401 Unauthorized
**راه‌حل**: مطمئن شوید که username و password صحیح است.

### مشکل: Token invalid
**راه‌حل**: مطمئن شوید که Token را به درستی در Header قرار داده‌اید:
```
Authorization: Bearer <token>
```

### مشکل: Inactive user
**راه‌حل**: مطمئن شوید که کاربر `is_active=True` است.

## 🎯 مراحل بعدی

پس از تکمیل فاز ۳، می‌توانید به فاز ۴ بروید:
- **فاز ۴**: API Core - مدیریت تیکت‌ها

---

**تاریخ تکمیل**: 2024-11-11

